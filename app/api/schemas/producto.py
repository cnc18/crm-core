"""Esquemas Pydantic de producto."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ProductoOut(BaseModel):
    """Datos de SALIDA: lo que la API devuelve de un producto."""

    # from_attributes permite construir el schema directo desde el modelo de SQLAlchemy.
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    precio: Decimal
    activo: bool
    receta_id: int
    created_at: datetime
