"""Esquemas Pydantic de disponibilidad de stock."""

from decimal import Decimal

from pydantic import BaseModel


class DisponibilidadOut(BaseModel):
    """Datos de SALIDA del calculo de unidades disponibles de un producto."""

    # nombre/precio son opcionales para cubrir el caso "producto no encontrado".
    nombre: str | None = None
    precio: Decimal | None = None
    unidades_disponibles: int
    disponible: bool
