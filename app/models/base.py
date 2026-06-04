"""Base declarativa de SQLAlchemy y mixins reutilizables (id, timestamps)."""

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Clase base de la que heredan todos los modelos (tablas) del proyecto."""


class IDTimestampMixin:
    """Mixin reutilizable: aporta 'id' y 'created_at' a cualquier modelo que lo herede,
    para no repetir estas columnas en cada tabla."""

    # Clave primaria entera y autoincremental (PostgreSQL la genera sola).
    id: Mapped[int] = mapped_column(primary_key=True)

    # Fecha de creacion: la pone la base de datos automaticamente al insertar la fila.
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
