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
    db: Session, nombre: str, precio: Decimal, receta_id: int
) -> Producto:
    """Crea un producto nuevo. La receta indicada debe existir."""
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
