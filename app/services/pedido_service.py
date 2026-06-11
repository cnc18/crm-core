"""Logica de negocio: armar pedido, calcular total y transiciones de estado."""

from collections import defaultdict
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors import ConflictError, InvalidDataError, NotFoundError
from app.models.materia_prima import MateriaPrima
from app.models.pedido import Pedido
from app.repositories.cliente_repo import ClienteRepository
from app.repositories.pedido_repo import PedidoRepository
from app.repositories.producto_repo import ProductoRepository
from app.repositories.receta_repo import RecetaRepository


def crear_pedido(db: Session, cliente_id: int, items: list[dict]) -> Pedido:
    """Crea un pedido en estado 'pendiente'. NO toca materias primas todavia.

    items: lista de {'producto_id', 'cantidad'}. Para cada item se toma el precio
    ACTUAL del producto (precio_unitario congelado al momento del pedido) y se
    suma al total. El descuento de stock ocurre despues, al pasar a produccion.
    """
    if ClienteRepository(db).get_by_id(cliente_id) is None:
        raise NotFoundError(f"No existe un cliente con id {cliente_id}")
    if not items:
        raise InvalidDataError("El pedido debe tener al menos un item")

    prod_repo = ProductoRepository(db)
    lineas: list[dict] = []
    total = Decimal(0)
    for it in items:
        producto = prod_repo.get_by_id(it["producto_id"])
        if producto is None:
            raise NotFoundError(f"No existe un producto con id {it['producto_id']}")

        cantidad = it["cantidad"]
        precio = producto.precio  # precio actual, se congela en la linea
        total += precio * cantidad
        lineas.append(
            {
                "producto_id": producto.id,
                "cantidad": cantidad,
                "precio_unitario": precio,
            }
        )

    # estado="pendiente" y descontado=False vienen por default del modelo.
    return PedidoRepository(db).crear(cliente_id, total, lineas)


def _materias_necesarias(db: Session, pedido: Pedido) -> dict[int, Decimal]:
    """Acumula cuanto se necesita de cada materia para producir TODO el pedido.

    Por cada item: cantidades de la receta del producto x la cantidad pedida.
    Varios items pueden compartir una materia, asi que se suman por materia_prima_id.
    """
    receta_repo = RecetaRepository(db)
    recetas: dict[int, object] = {}  # cache por receta_id (productos que la comparten)
    necesario: dict[int, Decimal] = defaultdict(lambda: Decimal(0))
    for item in pedido.items:
        receta_id = item.producto.receta_id
        receta = recetas.get(receta_id) or receta_repo.get_con_insumos(receta_id)
        recetas[receta_id] = receta
        if receta is None:
            continue  # producto sin receta: no consume materias
        for insumo in receta.insumos:
            necesario[insumo.materia_prima_id] += insumo.cantidad * item.cantidad
    return necesario


def listar_pedidos(db: Session, estado: str | None = None) -> list[Pedido]:
    """Lista pedidos, opcionalmente filtrados por estado."""
    return PedidoRepository(db).listar(estado)


def obtener_pedido(db: Session, pedido_id: int) -> Pedido:
    """Devuelve un pedido con sus items (404 si no existe)."""
    pedido = PedidoRepository(db).get_con_items(pedido_id)
    if pedido is None:
        raise NotFoundError(f"No existe un pedido con id {pedido_id}")
    return pedido


def descontar_materias(db: Session, pedido_id: int) -> Pedido:
    """Descuenta del stock las materias primas que consume el pedido. ATOMICO: todo o nada.

    Pasos (en este orden, que es lo que garantiza la atomicidad):
    1. Calcula cuanto se necesita de cada materia (varios items se ACUMULAN).
    2. Bloquea las filas de esas materias (SELECT ... FOR UPDATE) para que dos
       pedidos en paralelo no lean el mismo stock y lo gasten dos veces.
    3. VERIFICA que alcanza para TODAS antes de tocar nada. Una materia inactiva
       cuenta como stock 0.
    4. Si falta de alguna -> NO descuenta nada y lanza error con el detalle.
    5. Si alcanza -> descuenta todas y marca descontado=True en UN solo commit.
       Si el commit falla, PostgreSQL revierte todo (no queda a medias).
    """
    repo = PedidoRepository(db)
    pedido = repo.get_con_items(pedido_id)
    if pedido is None:
        raise NotFoundError(f"No existe un pedido con id {pedido_id}")
    if pedido.descontado:  # idempotencia: no descontar dos veces
        raise InvalidDataError("El pedido ya tiene las materias primas descontadas")

    necesario = _materias_necesarias(db, pedido)
    if not necesario:  # nada que descontar (recetas vacias): solo marcar
        return repo.marcar_descontado(pedido, True)

    # 2. Traer y BLOQUEAR las materias involucradas en una sola consulta.
    materias = db.scalars(
        select(MateriaPrima)
        .where(MateriaPrima.id.in_(necesario.keys()))
        .with_for_update()
    ).all()
    por_id = {m.id: m for m in materias}

    # 3-4. Verificar TODO antes de descontar; juntar faltantes con su detalle.
    faltantes = []
    for materia_id, necesita in necesario.items():
        materia = por_id.get(materia_id)
        disponible = materia.stock_actual if (materia and materia.activo) else Decimal(0)
        if disponible < necesita:
            nombre = materia.nombre if materia else f"id {materia_id}"
            faltantes.append(f"{nombre} (necesita {necesita}, hay {disponible})")

    if faltantes:
        # No se toco ningun stock: el pedido queda como estaba.
        raise ConflictError("Stock insuficiente: " + "; ".join(faltantes))

    # 5. Hay de todo -> descontar todo y marcar descontado en un unico commit.
    for materia_id, necesita in necesario.items():
        por_id[materia_id].stock_actual -= necesita
    pedido.descontado = True
    db.commit()
    db.refresh(pedido)
    return pedido


# Transiciones de estado permitidas (de -> a). Lo que no este aca es invalido.
_TRANSICIONES = {
    "pendiente": {"confirmado", "cancelado"},
    "confirmado": {"en_produccion", "entregado", "cancelado"},  # puede saltar a entregado
    "en_produccion": {"entregado", "cancelado"},
    "entregado": {"cancelado"},  # cancelar un entregado devuelve materias (ver abajo)
    "cancelado": set(),  # estado terminal
}


def _devolver_materias(db: Session, pedido: Pedido) -> None:
    """Suma de vuelta al stock las materias que el pedido habia descontado.

    Muta el stock en memoria (sin commit: lo confirma cambiar_estado) y baja el
    flag descontado. Devolver stock siempre es seguro, no hay que verificar nada.
    """
    necesario = _materias_necesarias(db, pedido)
    if necesario:
        materias = db.scalars(
            select(MateriaPrima)
            .where(MateriaPrima.id.in_(necesario.keys()))
            .with_for_update()
        ).all()
        por_id = {m.id: m for m in materias}
        for materia_id, cant in necesario.items():
            materia = por_id.get(materia_id)
            if materia is not None:
                materia.stock_actual += cant
    pedido.descontado = False


def cambiar_estado(db: Session, pedido_id: int, nuevo_estado: str) -> Pedido:
    """Cambia el estado del pedido respetando el flujo, y mueve el stock cuando toca.

    - Transicion invalida (ej. entregado -> pendiente) -> error, no cambia nada.
    - Al pasar a en_produccion o entregado: descuenta materias (si aun no se hizo).
      El descuento es atomico y lanza si falta stock; el estado no avanza en ese caso.
    - Al cancelar un pedido que YA descontó: devuelve las materias al stock y baja
      el flag descontado, todo en un mismo commit.
    """
    repo = PedidoRepository(db)
    pedido = repo.get_con_items(pedido_id)
    if pedido is None:
        raise NotFoundError(f"No existe un pedido con id {pedido_id}")

    actual = pedido.estado
    if nuevo_estado not in _TRANSICIONES.get(actual, set()):
        raise InvalidDataError(f"Transicion invalida: {actual} -> {nuevo_estado}")

    # Descuento al entrar a produccion/entregado, solo si todavia no se desconto.
    # Se hace ANTES de cambiar el estado: si falta stock, lanza y el estado no avanza.
    if nuevo_estado in ("en_produccion", "entregado") and not pedido.descontado:
        descontar_materias(db, pedido_id)  # atomico; deja descontado=True (mismo objeto)

    # Cancelar un pedido ya descontado: devolver las materias.
    if nuevo_estado == "cancelado" and pedido.descontado:
        _devolver_materias(db, pedido)

    pedido.estado = nuevo_estado
    db.commit()
    db.refresh(pedido)
    return pedido
