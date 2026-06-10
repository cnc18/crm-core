"""Modelo Oferta: promociones que crea marketing y consulta ventas (tabla ofertas)."""

from datetime import date

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDTimestampMixin
from app.models.producto import Producto


class Oferta(IDTimestampMixin, Base):
    __tablename__ = "ofertas"

    titulo: Mapped[str] = mapped_column(String(120))
    descripcion: Mapped[str] = mapped_column(Text)
    activa: Mapped[bool] = mapped_column(default=True)  # ofertas inactivas no se muestran
    fecha_inicio: Mapped[date | None] = mapped_column(default=None)
    fecha_fin: Mapped[date | None] = mapped_column(default=None)
    creada_por: Mapped[str] = mapped_column(String(50), default="manual")  # "manual" o agente

    # FK opcional: si es NULL la oferta es general (no atada a un producto concreto).
    producto_id: Mapped[int | None] = mapped_column(ForeignKey("productos.id"), default=None)
    producto: Mapped["Producto | None"] = relationship()
