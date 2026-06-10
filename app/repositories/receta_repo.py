"""Acceso a datos de recetas y sus insumos (hereda el CRUD generico de BaseRepository)."""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.receta import Receta, RecetaInsumo
from app.repositories.base_repo import BaseRepository


class RecetaRepository(BaseRepository[Receta]):
    def __init__(self, db: Session):
        super().__init__(Receta, db)

    def get_con_insumos(self, receta_id: int) -> Receta | None:
        """Devuelve la receta con sus insumos y la materia prima de cada uno ya cargados."""
        stmt = (
            select(Receta)
            .where(Receta.id == receta_id)
            .options(joinedload(Receta.insumos).joinedload(RecetaInsumo.materia_prima))
        )
        return self.db.scalars(stmt).unique().one_or_none()

    def reemplazar_insumos(self, receta: Receta, items: list[dict]) -> Receta:
        """Reemplaza TODOS los insumos de la receta por la lista dada.

        cascade delete-orphan: vaciar la lista borra los insumos viejos al hacer commit.
        Cada item: {'materia_prima_id', 'cantidad', 'unidad'}.
        """
        receta.insumos.clear()
        for it in items:
            receta.insumos.append(
                RecetaInsumo(
                    materia_prima_id=it["materia_prima_id"],
                    cantidad=it["cantidad"],
                    unidad=it["unidad"],
                )
            )
        self.db.commit()
        self.db.refresh(receta)
        return receta

    def agregar_insumo(
        self, receta: Receta, materia_prima_id: int, cantidad: Decimal, unidad: str
    ) -> RecetaInsumo:
        """Agrega un insumo a la receta y lo devuelve."""
        insumo = RecetaInsumo(
            receta_id=receta.id,
            materia_prima_id=materia_prima_id,
            cantidad=cantidad,
            unidad=unidad,
        )
        self.db.add(insumo)
        self.db.commit()
        self.db.refresh(insumo)
        return insumo

    def get_insumo(self, insumo_id: int) -> RecetaInsumo | None:
        """Busca un insumo (linea de receta) por su id."""
        return self.db.get(RecetaInsumo, insumo_id)

    def quitar_insumo(self, insumo: RecetaInsumo) -> None:
        """Elimina un insumo de la receta (borrado real de la fila intermedia)."""
        self.db.delete(insumo)
        self.db.commit()
