"""Modelos de receta: una Receta se compone de varios RecetaInsumo (materias primas).

Relaciones:
- Receta 1---N RecetaInsumo  (una receta lista varios insumos; cada insumo pertenece a una receta).
- RecetaInsumo N---1 MateriaPrima  (cada insumo apunta a la materia prima que consume).
"""

from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDTimestampMixin
from app.models.materia_prima import MateriaPrima


class Receta(IDTimestampMixin, Base):
    __tablename__ = "recetas"

    nombre: Mapped[str] = mapped_column(String(120))
    rinde_unidades: Mapped[int] = mapped_column()  # cuantas unidades de producto rinde

    # Lista de insumos de la receta. Si se borra la receta, se borran sus insumos.
    insumos: Mapped[list["RecetaInsumo"]] = relationship(
        back_populates="receta", cascade="all, delete-orphan"
    )


class RecetaInsumo(IDTimestampMixin, Base):
    __tablename__ = "receta_insumos"

    receta_id: Mapped[int] = mapped_column(ForeignKey("recetas.id"))
    materia_prima_id: Mapped[int] = mapped_column(ForeignKey("materias_primas.id"))
    cantidad: Mapped[Decimal] = mapped_column(Numeric(10, 2))  # cuanto consume de esa materia
    unidad: Mapped[str] = mapped_column(String(20))  # ml / unidad

    # Lado "muchos": cada insumo pertenece a una receta y apunta a una materia prima.
    receta: Mapped["Receta"] = relationship(back_populates="insumos")
    materia_prima: Mapped["MateriaPrima"] = relationship()
