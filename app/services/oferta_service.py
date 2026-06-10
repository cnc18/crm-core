"""Logica de negocio de ofertas: crear, editar, listar y activar/desactivar."""

from datetime import date

from sqlalchemy.orm import Session

from app.errors import NotFoundError
from app.models.oferta import Oferta
from app.repositories.oferta_repo import OfertaRepository
from app.repositories.producto_repo import ProductoRepository


def _validar_producto(db: Session, producto_id: int | None) -> None:
    """Si la oferta apunta a un producto, ese producto debe existir."""
    if producto_id is not None and ProductoRepository(db).get_by_id(producto_id) is None:
        raise NotFoundError(f"No existe un producto con id {producto_id}")


def crear_oferta(
    db: Session,
    titulo: str,
    descripcion: str,
    producto_id: int | None = None,
    fecha_inicio: date | None = None,
    fecha_fin: date | None = None,
    creada_por: str = "manual",
) -> Oferta:
    """Crea una oferta nueva (activa por default segun el modelo)."""
    _validar_producto(db, producto_id)
    repo = OfertaRepository(db)
    return repo.create(
        titulo=titulo,
        descripcion=descripcion,
        producto_id=producto_id,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        creada_por=creada_por,
    )


def editar_oferta(db: Session, oferta_id: int, **cambios) -> Oferta:
    """Edita campos de una oferta existente. Ignora claves con valor None."""
    repo = OfertaRepository(db)
    oferta = repo.get_by_id(oferta_id)
    if oferta is None:
        raise NotFoundError(f"No existe una oferta con id {oferta_id}")

    cambios = {k: v for k, v in cambios.items() if v is not None}
    if "producto_id" in cambios:
        _validar_producto(db, cambios["producto_id"])
    return repo.update(oferta, **cambios)


def listar_ofertas(db: Session, solo_activas: bool = False) -> list[Oferta]:
    """Lista ofertas: todas, o solo las activas y vigentes (para ventas)."""
    repo = OfertaRepository(db)
    return repo.get_activas() if solo_activas else repo.listar_todas()


def set_activa(db: Session, oferta_id: int, activa: bool) -> Oferta:
    """Activa o desactiva una oferta (no se borra de la base)."""
    repo = OfertaRepository(db)
    oferta = repo.get_by_id(oferta_id)
    if oferta is None:
        raise NotFoundError(f"No existe una oferta con id {oferta_id}")
    return repo.update(oferta, activa=activa)
