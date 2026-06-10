"""Endpoints de ofertas: panel de marketing (CRUD) y consulta del agente de ventas."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.schemas.oferta import OfertaCrear, OfertaEditar, OfertaSalida
from app.db.session import get_db
from app.services.oferta_service import (
    crear_oferta,
    editar_oferta,
    listar_ofertas,
    set_activa,
)

router = APIRouter(prefix="/ofertas", tags=["ofertas"])


class EstadoOferta(BaseModel):
    """Body del PATCH de estado: activar/desactivar."""

    activa: bool


@router.post("", response_model=OfertaSalida)
def crear(datos: OfertaCrear, db: Session = Depends(get_db)):
    """Crea una oferta nueva."""
    return crear_oferta(
        db,
        titulo=datos.titulo,
        descripcion=datos.descripcion,
        producto_id=datos.producto_id,
        fecha_inicio=datos.fecha_inicio,
        fecha_fin=datos.fecha_fin,
        creada_por=datos.creada_por,
    )


@router.get("", response_model=list[OfertaSalida])
def listar(db: Session = Depends(get_db)):
    """Lista todas las ofertas (para el panel)."""
    return listar_ofertas(db)


@router.get("/activas", response_model=list[OfertaSalida])
def listar_activas(db: Session = Depends(get_db)):
    """Lista solo ofertas activas y vigentes hoy (lo consulta el agente de ventas)."""
    return listar_ofertas(db, solo_activas=True)


@router.put("/{oferta_id}", response_model=OfertaSalida)
def editar(oferta_id: int, datos: OfertaEditar, db: Session = Depends(get_db)):
    """Edita campos de una oferta existente."""
    return editar_oferta(db, oferta_id, **datos.model_dump(exclude_unset=True))


@router.delete("/{oferta_id}", response_model=OfertaSalida)
def borrar(oferta_id: int, db: Session = Depends(get_db)):
    """Borrado SUAVE: marca activa=false, no elimina de la base."""
    return set_activa(db, oferta_id, activa=False)


@router.patch("/{oferta_id}/estado", response_model=OfertaSalida)
def cambiar_estado(oferta_id: int, datos: EstadoOferta, db: Session = Depends(get_db)):
    """Activa o desactiva una oferta segun 'activa'."""
    return set_activa(db, oferta_id, activa=datos.activa)
