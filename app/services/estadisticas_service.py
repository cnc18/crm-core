"""Logica de estadisticas: consultas de lectura agregadas (sumas, conteos, agrupaciones).

Las agregaciones se hacen en la base con SQLAlchemy (func.count/sum, group_by),
no trayendo filas a Python. Sin datos, los conteos/sumas dan 0 (no error).
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.cliente import Cliente
from app.models.pedido import Pedido, PedidoItem
from app.models.producto import Producto

# Estados que cuentan como "cerrado" (no requieren accion / ya finalizaron).
_ESTADOS_CERRADOS = ("entregado", "cancelado")


def resumen(db: Session) -> dict:
    """Numeros clave para las tarjetas del dashboard, en un solo JSON.

    - total_clientes: cuantos clientes hay en total.
    - clientes_nuevos_mes: clientes creados desde el inicio del mes actual.
    - ventas_mes: suma del total de pedidos del mes (excluye cancelados).
    - pedidos_pendientes: pedidos no cerrados (ni entregados ni cancelados).
    - total_productos_activos: productos con activo=True.
    """
    inicio_mes = func.date_trunc("month", func.now())  # 1er dia del mes actual, 00:00

    total_clientes = db.scalar(select(func.count()).select_from(Cliente))
    clientes_nuevos_mes = db.scalar(
        select(func.count()).select_from(Cliente).where(Cliente.created_at >= inicio_mes)
    )
    # Suma de ventas del mes; coalesce a 0 para que sin pedidos de igual un numero.
    ventas_mes = db.scalar(
        select(func.coalesce(func.sum(Pedido.total), 0)).where(
            Pedido.created_at >= inicio_mes,
            Pedido.estado != "cancelado",
        )
    )
    pedidos_pendientes = db.scalar(
        select(func.count())
        .select_from(Pedido)
        .where(Pedido.estado.notin_(_ESTADOS_CERRADOS))
    )
    total_productos_activos = db.scalar(
        select(func.count()).select_from(Producto).where(Producto.activo.is_(True))
    )

    return {
        "total_clientes": total_clientes,
        "clientes_nuevos_mes": clientes_nuevos_mes,
        "ventas_mes": ventas_mes,
        "pedidos_pendientes": pedidos_pendientes,
        "total_productos_activos": total_productos_activos,
    }


# Mapea el periodo del request a la unidad de date_trunc de PostgreSQL.
_UNIDAD_PERIODO = {"dia": "day", "semana": "week", "mes": "month"}


def ventas_por_periodo(db: Session, periodo: str = "mes") -> list[dict]:
    """Serie de ventas (suma de totales de pedidos) agrupada por periodo, para graficar.

    Agrupa por dia/semana/mes con date_trunc, suma los totales (excluye cancelados),
    toma los ultimos 12 periodos y los devuelve en orden cronologico ascendente.
    Cada punto: {"periodo": <etiqueta>, "total": <suma>}. Sin datos -> [].
    """
    unidad = _UNIDAD_PERIODO[periodo]  # KeyError si invalido (el router ya valida)
    bucket = func.date_trunc(unidad, Pedido.created_at)

    stmt = (
        select(bucket.label("periodo"), func.coalesce(func.sum(Pedido.total), 0).label("total"))
        .where(Pedido.estado != "cancelado")
        .group_by(bucket)
        .order_by(bucket.desc())  # mas recientes primero para limitar a 12
        .limit(12)
    )
    filas = db.execute(stmt).all()

    # reversed -> orden cronologico ascendente para la grafica.
    return [{"periodo": _etiqueta(p, periodo), "total": t} for p, t in reversed(filas)]


def _etiqueta(bucket, periodo: str) -> str:
    """Formatea el inicio del periodo: 'YYYY-MM' para mes, 'YYYY-MM-DD' para dia/semana."""
    if periodo == "mes":
        return bucket.strftime("%Y-%m")
    return bucket.strftime("%Y-%m-%d")


def leads_por_estado(db: Session) -> list[dict]:
    """Conteo de clientes agrupados por estado_lead, para la grafica de leads.

    Devuelve [{"estado": <estado_lead>, "cantidad": <conteo>}], de mayor a menor.
    Sin clientes -> [].
    """
    stmt = (
        select(Cliente.estado_lead, func.count().label("cantidad"))
        .group_by(Cliente.estado_lead)
        .order_by(func.count().desc())  # el estado mas comun primero
    )
    filas = db.execute(stmt).all()
    return [{"estado": estado, "cantidad": cantidad} for estado, cantidad in filas]


def top_productos(db: Session, limite: int = 5) -> list[dict]:
    """Productos mas vendidos, calculados desde pedido_items (excluye cancelados).

    Por producto suma cantidades (cantidad_vendida) e ingreso (cantidad x precio
    congelado). Ordena de mayor a menor cantidad y corta en 'limite'. Sin ventas -> [].
    """
    stmt = (
        select(
            PedidoItem.producto_id,
            Producto.nombre,
            func.sum(PedidoItem.cantidad).label("cantidad_vendida"),
            func.coalesce(
                func.sum(PedidoItem.cantidad * PedidoItem.precio_unitario), 0
            ).label("ingreso"),
        )
        .join(Producto, Producto.id == PedidoItem.producto_id)
        .join(Pedido, Pedido.id == PedidoItem.pedido_id)
        .where(Pedido.estado != "cancelado")
        .group_by(PedidoItem.producto_id, Producto.nombre)
        .order_by(func.sum(PedidoItem.cantidad).desc())
        .limit(limite)
    )
    filas = db.execute(stmt).all()
    return [
        {
            "producto": producto_id,
            "nombre": nombre,
            "cantidad_vendida": cantidad_vendida,
            "ingreso": ingreso,
        }
        for producto_id, nombre, cantidad_vendida, ingreso in filas
    ]
