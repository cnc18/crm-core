"""Logica de negocio de recetas: ver, reemplazar, agregar y quitar insumos.

Las rutas operan sobre la receta de un producto; cada cambio en la receta altera
el calculo de disponibilidad de ese producto (depende de sus insumos).
"""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.errors import NotFoundError
from app.models.producto import Producto
from app.models.receta import Receta
from app.repositories.materia_prima_repo import MateriaPrimaRepository
from app.repositories.producto_repo import ProductoRepository
from app.repositories.receta_repo import RecetaRepository


def _get_producto_o_404(db: Session, producto_id: int) -> Producto:
    producto = ProductoRepository(db).get_by_id(producto_id)
    if producto is None:
        raise NotFoundError(f"No existe un producto con id {producto_id}")
    return producto


def _get_receta_o_404(repo: RecetaRepository, receta_id: int) -> Receta:
    receta = repo.get_con_insumos(receta_id)
    if receta is None:
        raise NotFoundError(f"No existe una receta con id {receta_id}")
    return receta


def _validar_materia(db: Session, materia_prima_id: int) -> None:
    """La materia prima referida por el insumo debe existir."""
    if MateriaPrimaRepository(db).get_by_id(materia_prima_id) is None:
        raise NotFoundError(f"No existe una materia prima con id {materia_prima_id}")


def _armar_salida(producto: Producto, receta: Receta) -> dict:
    """Arma la respuesta: producto + lista de insumos con el nombre de cada materia."""
    return {
        "producto_id": producto.id,
        "producto_nombre": producto.nombre,
        "receta_id": receta.id,
        "nombre": receta.nombre,
        "rinde_unidades": receta.rinde_unidades,
        "insumos": [
            {
                "materia_prima_id": i.materia_prima_id,
                "nombre": i.materia_prima.nombre,
                "cantidad": i.cantidad,
                "unidad": i.unidad,
            }
            for i in receta.insumos
        ],
    }


def ver_receta_de_producto(db: Session, producto_id: int) -> dict:
    """Devuelve la receta de un producto con sus insumos y cantidades."""
    producto = _get_producto_o_404(db, producto_id)
    receta = _get_receta_o_404(RecetaRepository(db), producto.receta_id)
    return _armar_salida(producto, receta)


def reemplazar_receta_de_producto(
    db: Session, producto_id: int, insumos: list[dict]
) -> dict:
    """Reemplaza la receta completa del producto por la lista de insumos dada."""
    producto = _get_producto_o_404(db, producto_id)
    repo = RecetaRepository(db)
    receta = _get_receta_o_404(repo, producto.receta_id)
    for it in insumos:
        _validar_materia(db, it["materia_prima_id"])
    repo.reemplazar_insumos(receta, insumos)
    return _armar_salida(producto, receta)


def agregar_insumo_a_producto(
    db: Session,
    producto_id: int,
    materia_prima_id: int,
    cantidad: Decimal,
    unidad: str,
) -> dict:
    """Agrega un insumo a la receta del producto."""
    producto = _get_producto_o_404(db, producto_id)
    repo = RecetaRepository(db)
    receta = _get_receta_o_404(repo, producto.receta_id)
    _validar_materia(db, materia_prima_id)
    repo.agregar_insumo(receta, materia_prima_id, cantidad, unidad)
    db.refresh(receta)  # recarga la lista de insumos con el nuevo
    return _armar_salida(producto, receta)


def quitar_insumo(db: Session, insumo_id: int) -> None:
    """Quita un insumo de su receta (borra esa linea de la receta)."""
    repo = RecetaRepository(db)
    insumo = repo.get_insumo(insumo_id)
    if insumo is None:
        raise NotFoundError(f"No existe un insumo de receta con id {insumo_id}")
    repo.quitar_insumo(insumo)
