"""Esquemas Pydantic de cliente (entrada/salida de la API)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.api.schemas.validators import TextoObligatorio


class ClienteCreate(BaseModel):
    """Datos de ENTRADA: lo que el cliente de la API envia para registrar un lead."""

    telefono: TextoObligatorio
    nombre: str | None = None
    canal_origen: str = "whatsapp"


class ClienteOut(BaseModel):
    """Datos de SALIDA: lo que la API devuelve de un cliente."""

    # from_attributes permite construir el schema directo desde el modelo de SQLAlchemy.
    model_config = ConfigDict(from_attributes=True)

    id: int
    telefono: str
    nombre: str | None
    estado_lead: str
    canal_origen: str
    created_at: datetime
