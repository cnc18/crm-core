"""CRUD generico reutilizable (patron Repository).

El patron Repository concentra el acceso a la base de datos en un solo lugar:
los servicios y endpoints piden datos al repositorio sin escribir consultas SQL
sueltas por todo el codigo. BaseRepository ofrece las operaciones comunes para
cualquier modelo; cada modelo puede tener su propio repo que herede de este.
"""

from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.base import Base

# Tipo generico: cualquier modelo que herede de Base (Cliente, Producto, etc.).
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType], db: Session):
        self.model = model  # la clase del modelo (ej. Producto)
        self.db = db        # la sesion de SQLAlchemy

    def get_by_id(self, id: int) -> ModelType | None:
        """Devuelve un registro por su id, o None si no existe."""
        return self.db.get(self.model, id)

    def get_all(self) -> list[ModelType]:
        """Devuelve todos los registros del modelo."""
        return list(self.db.scalars(select(self.model)).all())

    def create(self, **data) -> ModelType:
        """Crea un registro con los datos dados, lo guarda y lo devuelve."""
        obj = self.model(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)  # recarga el objeto con lo que asigno la base (id, created_at)
        return obj
