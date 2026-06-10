"""Acceso a datos de materias primas (hereda el CRUD generico de BaseRepository)."""

from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.materia_prima import MateriaPrima
from app.repositories.base_repo import BaseRepository


class MateriaPrimaRepository(BaseRepository[MateriaPrima]):
    # crear() y get_by_id() vienen heredados de BaseRepository (create / get_by_id).

    def __init__(self, db: Session):
        super().__init__(MateriaPrima, db)

    def listar_activas(self) -> list[MateriaPrima]:
        """Lista solo materias primas activas (las dadas de baja no se muestran)."""
        stmt = (
            select(MateriaPrima)
            .where(MateriaPrima.activo.is_(True))
            .order_by(func.lower(MateriaPrima.nombre))  # orden alfabetico util
        )
        return list(self.db.scalars(stmt).all())

    def actualizar(self, materia: MateriaPrima, **cambios) -> MateriaPrima:
        """Aplica solo los campos presentes en 'cambios' y guarda."""
        for campo, valor in cambios.items():
            setattr(materia, campo, valor)
        self.db.commit()
        self.db.refresh(materia)
        return materia

    def desactivar(self, materia: MateriaPrima) -> MateriaPrima:
        """Borrado SUAVE: marca activo=false, no elimina de la base."""
        return self.actualizar(materia, activo=False)

    def ajustar_stock(self, materia: MateriaPrima, nuevo_stock: Decimal) -> MateriaPrima:
        """Cambia unicamente el stock_actual de la materia."""
        return self.actualizar(materia, stock_actual=nuevo_stock)

    def get_stock_actual(self, id: int) -> Decimal | None:
        """Devuelve el stock_actual de una materia prima ACTIVA por su id.

        None si no existe o si esta dada de baja (activo=False).
        """
        materia = self.get_by_id(id)  # get_by_id viene heredado de BaseRepository
        if materia is None or not materia.activo:
            return None
        return materia.stock_actual
