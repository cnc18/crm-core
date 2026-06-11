"""Esquemas Pydantic de pedido y sus items."""

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# Estados validos del pedido (mismo conjunto que maneja el servicio).
EstadoPedido = Literal["pendiente", "confirmado", "en_produccion", "entregado", "cancelado"]


class PedidoItemEntrada(BaseModel):
    """Una linea del pedido al crearlo: que producto y cuanto."""

    producto_id: int
    cantidad: int = Field(gt=0)  # debe pedir al menos 1


class PedidoCrear(BaseModel):
    """Datos de ENTRADA para crear un pedido."""

    cliente_id: int
    items: list[PedidoItemEntrada] = Field(min_length=1)  # no puede ir vacio


class CambiarEstado(BaseModel):
    """Body para cambiar el estado de un pedido."""

    nuevo_estado: EstadoPedido


class PedidoItemSalida(BaseModel):
    """Una linea del pedido como se devuelve (precio congelado al momento del pedido)."""

    model_config = ConfigDict(from_attributes=True)

    producto_id: int
    cantidad: int
    precio_unitario: Decimal


class PedidoSalida(BaseModel):
    """Datos de SALIDA: el pedido completo con sus items."""

    # from_attributes permite construirlo directo desde el modelo (con items cargados).
    model_config = ConfigDict(from_attributes=True)

    id: int
    cliente_id: int
    estado: str
    total: Decimal
    descontado: bool
    created_at: datetime
    items: list[PedidoItemSalida]
