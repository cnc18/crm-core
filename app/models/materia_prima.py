"""Modelo MateriaPrima: insumos para fabricar los productos (esencias, alcohol, frascos)."""

from decimal import Decimal

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IDTimestampMixin


class MateriaPrima(IDTimestampMixin, Base):
    __tablename__ = "materias_primas"

    nombre: Mapped[str] = mapped_column(String(120))
    tipo: Mapped[str] = mapped_column(String(20))  # esencia / alcohol / frasco
    stock_actual: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    unidad: Mapped[str] = mapped_column(String(20))  # ml / unidad
