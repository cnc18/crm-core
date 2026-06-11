"""Modelos de pedido y pedido_item.

Relaciones:
- Pedido 1---N PedidoItem  (un pedido tiene varias lineas; cada linea es de un pedido).
- PedidoItem N---1 Producto  (cada linea apunta al producto que se vende).
"""

from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDTimestampMixin
from app.models.producto import Producto


class Pedido(IDTimestampMixin, Base):
    __tablename__ = "pedidos"

    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"))
    estado: Mapped[str] = mapped_column(String(20), default="pendiente")
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    # descontado=True => ya se restaron las materias primas del stock (al pasar a produccion).
    descontado: Mapped[bool] = mapped_column(default=False)

    # Lineas del pedido. Si se borra el pedido, se borran sus items.
    items: Mapped[list["PedidoItem"]] = relationship(
        back_populates="pedido", cascade="all, delete-orphan"
    )


class PedidoItem(IDTimestampMixin, Base):
    __tablename__ = "pedido_items"

    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos.id"))
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"))
    cantidad: Mapped[int] = mapped_column()
    precio_unitario: Mapped[Decimal] = mapped_column(Numeric(10, 2))  # precio al momento del pedido

    # Lado "muchos": cada item pertenece a un pedido y apunta a un producto.
    pedido: Mapped["Pedido"] = relationship(back_populates="items")
    producto: Mapped["Producto"] = relationship()
