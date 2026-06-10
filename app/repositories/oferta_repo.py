"""Acceso a datos de ofertas (hereda el CRUD generico de BaseRepository)."""

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.oferta import Oferta
from app.repositories.base_repo import BaseRepository


class OfertaRepository(BaseRepository[Oferta]):
    def __init__(self, db: Session):
        super().__init__(Oferta, db)

    def update(self, oferta: Oferta, **cambios) -> Oferta:
        """Aplica solo los campos presentes en 'cambios' a la oferta y guarda."""
        for campo, valor in cambios.items():
            setattr(oferta, campo, valor)
        self.db.commit()
        self.db.refresh(oferta)
        return oferta

    # Orden util para listados: las de fecha de inicio mas reciente primero
    # (las sin fecha quedan al final), desempatando por fecha de creacion.
    _orden = (Oferta.fecha_inicio.desc().nullslast(), Oferta.created_at.desc())

    def listar_todas(self) -> list[Oferta]:
        """Todas las ofertas (para el panel), ordenadas por fecha."""
        stmt = select(Oferta).order_by(*self._orden)
        return list(self.db.scalars(stmt).all())

    def get_activas(self) -> list[Oferta]:
        """Ofertas con activa=True y vigentes hoy, ordenadas por fecha.

        Una fecha NULL no restringe: sin fecha_inicio vale desde siempre, sin
        fecha_fin vale para siempre. Se compara contra la fecha actual de la base.
        """
        hoy = func.current_date()
        stmt = (
            select(Oferta)
            .where(Oferta.activa.is_(True))
            .where(or_(Oferta.fecha_inicio.is_(None), Oferta.fecha_inicio <= hoy))
            .where(or_(Oferta.fecha_fin.is_(None), Oferta.fecha_fin >= hoy))
            .order_by(*self._orden)
        )
        return list(self.db.scalars(stmt).all())
