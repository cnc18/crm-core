"""Logica de negocio de productos: alta, listado, edicion y baja suave."""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.errors import NotFoundError
from app.models.producto import Producto
from app.models.receta import Receta
from app.repositories.producto_repo import ProductoRepository


def _get_o_404(repo: ProductoRepository, producto_id: int) -> Producto:
    """Resuelve id -> objeto, o lanza NotFoundError (404)."""
    producto = repo.get_by_id(producto_id)
    if producto is None:
        raise NotFoundError(f"No existe un producto con id {producto_id}")
    return producto


def crear_producto(
    db: Session, nombre: str, precio: Decimal, receta_id: int | None = None
) -> Producto:
    """Crea un producto. Si no se pasa receta_id, le crea una receta VACIA propia.

    - Sin receta_id (flujo nuevo): se crea una Receta vacia "Receta de {nombre}" y
      se asocia al producto, todo en una transaccion (o ambos o ninguno). Despues
      se le cargan insumos desde la seccion de recetas.
    - Con receta_id (compat): usa esa receta existente (debe existir).
    """
    if receta_id is None:
        return ProductoRepository(db).crear_con_receta_vacia(
            nombre, precio, receta_nombre=f"Receta de {nombre}"
        )

    if db.get(Receta, receta_id) is None:
        raise NotFoundError(f"No existe una receta con id {receta_id}")
    return ProductoRepository(db).create(
        nombre=nombre, precio=precio, receta_id=receta_id
    )


def listar_productos(db: Session) -> list[Producto]:
    """Lista solo los productos activos."""
    return ProductoRepository(db).listar_activos()


def obtener_producto(db: Session, producto_id: int) -> Producto:
    """Devuelve un producto por id (404 si no existe)."""
    return _get_o_404(ProductoRepository(db), producto_id)


def editar_producto(db: Session, producto_id: int, **cambios) -> Producto:
    """Edita campos de un producto (nombre, precio, activo). Ignora claves None."""
    repo = ProductoRepository(db)
    producto = _get_o_404(repo, producto_id)
    cambios = {k: v for k, v in cambios.items() if v is not None}
    return repo.actualizar(producto, **cambios)


def desactivar_producto(db: Session, producto_id: int) -> Producto:
    """Borrado SUAVE: marca activo=false (no se elimina de la base)."""
    repo = ProductoRepository(db)
    producto = _get_o_404(repo, producto_id)
    return repo.desactivar(producto)
