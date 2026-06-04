"""Modelo Cliente: contacto/lead del CRM, identificado por su telefono."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IDTimestampMixin


class Cliente(IDTimestampMixin, Base):
    __tablename__ = "clientes"

    telefono: Mapped[str] = mapped_column(String(30), unique=True)  # identificador unico
    nombre: Mapped[str | None] = mapped_column(String(120))  # puede ser nulo
    estado_lead: Mapped[str] = mapped_column(String(20), default="nuevo")
    canal_origen: Mapped[str] = mapped_column(String(20), default="whatsapp")
