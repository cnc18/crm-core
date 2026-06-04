"""Acceso a datos de materias primas (hereda el CRUD generico de BaseRepository)."""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.materia_prima import MateriaPrima
from app.repositories.base_repo import BaseRepository


class MateriaPrimaRepository(BaseRepository[MateriaPrima]):
    def __init__(self, db: Session):
        super().__init__(MateriaPrima, db)

    def get_stock_actual(self, id: int) -> Decimal | None:
        """Devuelve el stock_actual de una materia prima por su id (None si no existe)."""
        materia = self.get_by_id(id)  # get_by_id viene heredado de BaseRepository
        return materia.stock_actual if materia is not None else None
