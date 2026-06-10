"""Esquemas Pydantic de oferta (entrada/salida de la API)."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, model_validator

from app.api.schemas.validators import TextoObligatorio


def _validar_fechas(inicio: date | None, fin: date | None) -> None:
    """fecha_fin no puede ser anterior a fecha_inicio (si ambas estan presentes)."""
    if inicio is not None and fin is not None and fin < inicio:
        raise ValueError("fecha_fin no puede ser anterior a fecha_inicio")


class OfertaCrear(BaseModel):
    """Datos de ENTRADA para crear una oferta."""

    titulo: TextoObligatorio
    descripcion: TextoObligatorio
    producto_id: int | None = None
    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    creada_por: str = "manual"

    @model_validator(mode="after")
    def fechas_coherentes(self) -> "OfertaCrear":
        _validar_fechas(self.fecha_inicio, self.fecha_fin)
        return self


class OfertaEditar(BaseModel):
    """Datos de ENTRADA para editar una oferta: todos los campos opcionales."""

    titulo: TextoObligatorio | None = None
    descripcion: TextoObligatorio | None = None
    producto_id: int | None = None
    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    activa: bool | None = None

    @model_validator(mode="after")
    def fechas_coherentes(self) -> "OfertaEditar":
        _validar_fechas(self.fecha_inicio, self.fecha_fin)
        return self


class OfertaSalida(BaseModel):
    """Datos de SALIDA: lo que la API devuelve de una oferta."""

    # from_attributes permite construir el schema directo desde el modelo de SQLAlchemy.
    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str
    descripcion: str
    activa: bool
    producto_id: int | None
    fecha_inicio: date | None
    fecha_fin: date | None
    creada_por: str
    created_at: datetime
