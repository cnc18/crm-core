"""Endpoints para crear, consultar y cambiar el estado de pedidos."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas.pedido import (
    CambiarEstado,
    EstadoPedido,
    PedidoCrear,
    PedidoSalida,
)
from app.db.session import get_db
from app.services import pedido_service

router = APIRouter(prefix="/pedidos", tags=["pedidos"])


@router.post("", response_model=PedidoSalida)
def crear(datos: PedidoCrear, db: Session = Depends(get_db)):
    """Crea un pedido en estado 'pendiente' (no toca materias primas)."""
    items = [i.model_dump() for i in datos.items]
    return pedido_service.crear_pedido(db, datos.cliente_id, items)


@router.get("", response_model=list[PedidoSalida])
def listar(estado: EstadoPedido | None = None, db: Session = Depends(get_db)):
    """Lista pedidos; filtro opcional por estado (?estado=confirmado)."""
    return pedido_service.listar_pedidos(db, estado)


@router.get("/{pedido_id}", response_model=PedidoSalida)
def ver(pedido_id: int, db: Session = Depends(get_db)):
    """Devuelve un pedido con sus items."""
    return pedido_service.obtener_pedido(db, pedido_id)


@router.patch("/{pedido_id}/estado", response_model=PedidoSalida)
def cambiar_estado(pedido_id: int, datos: CambiarEstado, db: Session = Depends(get_db)):
    """Cambia el estado del pedido; dispara descuento o devolucion de materias.

    Errores via handler global: 404 no existe, 400 transicion invalida,
    409 stock insuficiente (con el detalle de que materia falta).
    """
    return pedido_service.cambiar_estado(db, pedido_id, datos.nuevo_estado)
