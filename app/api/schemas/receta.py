"""Esquemas Pydantic de receta (entrada/salida de la API)."""

from decimal import Decimal

from pydantic import BaseModel, Field

from app.api.schemas.materia_prima import Unidad  # Literal["ml", "gramos", "unidad"]


class RecetaInsumoEntrada(BaseModel):
    """Un insumo de la receta: que materia, cuanto y en que unidad."""

    materia_prima_id: int
    cantidad: Decimal = Field(gt=0)  # debe ser mayor a 0
    unidad: Unidad


class RecetaEditar(BaseModel):
    """Datos de ENTRADA para reemplazar la receta completa."""

    insumos: list[RecetaInsumoEntrada]


class InsumoSalida(BaseModel):
    """Un insumo tal como se devuelve: con el nombre de la materia prima."""

    materia_prima_id: int
    nombre: str  # nombre de la materia prima
    cantidad: Decimal
    unidad: str


class RecetaSalida(BaseModel):
    """Datos de SALIDA: el producto y la lista de insumos de su receta."""

    producto_id: int
    producto_nombre: str
    receta_id: int
    nombre: str  # nombre de la receta
    rinde_unidades: int
    insumos: list[InsumoSalida]
