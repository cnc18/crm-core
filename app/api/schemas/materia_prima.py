"""Esquemas Pydantic de materia prima (entrada/salida de la API)."""

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.api.schemas.validators import TextoObligatorio

# Unidades de medida permitidas para una materia prima.
Unidad = Literal["ml", "gramos", "unidad"]


class MateriaPrimaCrear(BaseModel):
    """Datos de ENTRADA para crear una materia prima."""

    nombre: TextoObligatorio
    tipo: TextoObligatorio  # esencia / alcohol / frasco
    stock_actual: Decimal = Field(ge=0)  # no puede ser negativo
    unidad: Unidad


class MateriaPrimaEditar(BaseModel):
    """Datos de ENTRADA para editar: todos los campos opcionales."""

    nombre: TextoObligatorio | None = None
    tipo: TextoObligatorio | None = None
    stock_actual: Decimal | None = Field(default=None, ge=0)
    unidad: Unidad | None = None


class AjusteStock(BaseModel):
    """Body para ajustar el stock: o un valor absoluto, o una cantidad a sumar/restar.

    - stock_actual: fija el stock a ese valor (reemplaza).
    - cantidad: suma (positivo) o resta (negativo) sobre el stock actual.
    Enviar exactamente uno de los dos.
    """

    stock_actual: Decimal | None = Field(default=None, ge=0)
    cantidad: Decimal | None = None

    @model_validator(mode="after")
    def exactamente_uno(self) -> "AjusteStock":
        if (self.stock_actual is None) == (self.cantidad is None):
            raise ValueError(
                "Enviá 'stock_actual' (valor absoluto) o 'cantidad' (delta), no ambos ni ninguno"
            )
        return self


class MateriaPrimaSalida(BaseModel):
    """Datos de SALIDA: lo que la API devuelve de una materia prima."""

    # from_attributes permite construir el schema directo desde el modelo de SQLAlchemy.
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    tipo: str
    stock_actual: Decimal
    unidad: str
    activo: bool
    created_at: datetime
