"""Modelo Producto: el articulo final que se vende, fabricado a partir de una Receta."""

from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDTimestampMixin
from app.models.receta import Receta


class Producto(IDTimestampMixin, Base):
    __tablename__ = "productos"

    nombre: Mapped[str] = mapped_column(String(120))
    precio: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    activo: Mapped[bool] = mapped_column(default=True)  # productos inactivos no se venden

    # Cada producto se fabrica segun una receta (Producto N---1 Receta).
    # Nullable como respaldo: permite un producto sin receta a nivel base.
    receta_id: Mapped[int | None] = mapped_column(ForeignKey("recetas.id"), nullable=True)
    receta: Mapped["Receta | None"] = relationship()
