"""Esquemas Pydantic de producto (entrada/salida de la API)."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.api.schemas.validators import TextoObligatorio


class ProductoCrear(BaseModel):
    """Datos de ENTRADA para crear un producto."""

    nombre: TextoObligatorio
    precio: Decimal = Field(gt=0)  # el precio debe ser mayor a 0
    receta_id: int  # obligatoria: todo producto se fabrica segun una receta


class ProductoEditar(BaseModel):
    """Datos de ENTRADA para editar: todos los campos opcionales."""

    nombre: TextoObligatorio | None = None
    precio: Decimal | None = Field(default=None, gt=0)
    activo: bool | None = None


class ProductoSalida(BaseModel):
    """Datos de SALIDA: lo que la API devuelve de un producto."""

    # from_attributes permite construir el schema directo desde el modelo de SQLAlchemy.
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    precio: Decimal
    activo: bool
    receta_id: int
    created_at: datetime
