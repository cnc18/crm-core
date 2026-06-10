"""Logica de negocio: calcula cuantas unidades se pueden producir segun receta."""

from sqlalchemy.orm import Session

from app.repositories.producto_repo import ProductoRepository


def calcular_unidades_disponibles(producto_id: int, db: Session) -> dict:
    """Calcula cuantas unidades de un producto se pueden fabricar con el stock actual.

    Logica:
    1. Busca el producto y su receta.
    2. Para cada insumo: cuantas unidades alcanza ese insumo = stock_actual // cantidad
       (division entera hacia abajo: 250ml de esencia / 30ml = 8 unidades, sobra resto).
    3. El total = el MINIMO de esas cifras, porque el insumo mas escaso limita la produccion.

    Siempre devuelve un diccionario con la misma forma (nunca lanza excepcion), para que
    quien lo llame (un endpoint, por ejemplo) reciba una respuesta clara en cualquier caso.
    """
    # Caso A: el producto no existe -> resultado claro, sin reventar.
    producto = ProductoRepository(db).get_by_id(producto_id)
    if producto is None:
        return {
            "encontrado": False,
            "nombre": None,
            "precio": None,
            "unidades_disponibles": 0,
            "disponible": False,
            "motivo": f"No existe un producto con id {producto_id}",
        }

    # Caso B: el producto existe pero no tiene receta -> no se puede calcular produccion.
    receta = producto.receta
    if receta is None or not receta.insumos:
        return {
            "encontrado": True,
            "nombre": producto.nombre,
            "precio": producto.precio,
            "unidades_disponibles": 0,
            "disponible": False,
            "motivo": "El producto no tiene receta (o la receta no tiene insumos)",
        }

    # Caso C: calculo normal. Por cada insumo, cuantas unidades permite su stock.
    capacidades = []
    for insumo in receta.insumos:
        materia = insumo.materia_prima
        # Materia dada de baja (activo=False): se trata como no disponible -> limita a 0.
        if not materia.activo:
            capacidades.append(0)
            continue
        stock = materia.stock_actual
        necesita = insumo.cantidad
        if necesita <= 0:  # receta mal definida: evita division por cero, ignora ese insumo
            continue
        # // = division entera hacia abajo. Si el stock es 0, da 0 (y el minimo sera 0).
        capacidades.append(int(stock // necesita))

    # El insumo mas escaso manda. Sin insumos validos => 0.
    unidades = min(capacidades) if capacidades else 0

    return {
        "encontrado": True,
        "nombre": producto.nombre,
        "precio": producto.precio,
        "unidades_disponibles": unidades,
        "disponible": unidades > 0,
        "motivo": None if unidades > 0 else "Sin stock suficiente en algun insumo",
    }
