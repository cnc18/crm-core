"""Acceso a datos de productos (hereda el CRUD generico de BaseRepository)."""

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.producto import Producto
from app.repositories.base_repo import BaseRepository


class ProductoRepository(BaseRepository[Producto]):
    def __init__(self, db: Session):
        super().__init__(Producto, db)

    def buscar_por_nombre(self, nombre: str) -> list[Producto]:
        """Busca productos cuyo nombre contenga el texto, sin distinguir mayusculas.

        - ilike + comodines (%texto%) => coincidencia parcial e insensible a mayusculas.
        - joinedload(receta) => trae la receta ya cargada, evitando consultas extra despues.
        """
        stmt = (
            select(Producto)
            .where(Producto.nombre.ilike(f"%{nombre}%"))
            .options(joinedload(Producto.receta))
        )
        return list(self.db.scalars(stmt).all())
