"""Acceso a datos de productos (hereda el CRUD generico de BaseRepository)."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.producto import Producto
from app.repositories.base_repo import BaseRepository


class ProductoRepository(BaseRepository[Producto]):
    # crear() y get_by_id() vienen heredados de BaseRepository (create / get_by_id).

    def __init__(self, db: Session):
        super().__init__(Producto, db)

    def actualizar(self, producto: Producto, **cambios) -> Producto:
        """Aplica solo los campos presentes en 'cambios' al producto y guarda."""
        for campo, valor in cambios.items():
            setattr(producto, campo, valor)
        self.db.commit()
        self.db.refresh(producto)
        return producto

    def desactivar(self, producto: Producto) -> Producto:
        """Borrado SUAVE: marca activo=false, no elimina de la base."""
        return self.actualizar(producto, activo=False)

    def buscar_por_nombre(self, nombre: str) -> list[Producto]:
        """Busca productos ACTIVOS cuyo nombre contenga el texto, sin distinguir mayusculas.

        - ilike + comodines (%texto%) => coincidencia parcial e insensible a mayusculas.
        - activo=True => no devuelve productos dados de baja (lo consulta el agente).
        - joinedload(receta) => trae la receta ya cargada, evitando consultas extra despues.
        """
        stmt = (
            select(Producto)
            .where(Producto.activo.is_(True))
            .where(Producto.nombre.ilike(f"%{nombre}%"))
            .options(joinedload(Producto.receta))
            .order_by(func.lower(Producto.nombre))  # alfabetico, sin distinguir mayusculas
        )
        return list(self.db.scalars(stmt).all())

    def listar_activos(self) -> list[Producto]:
        """Lista solo productos activos (los dados de baja no se muestran al agente)."""
        stmt = (
            select(Producto)
            .where(Producto.activo.is_(True))
            .options(joinedload(Producto.receta))
            .order_by(func.lower(Producto.nombre))  # orden alfabetico util
        )
        return list(self.db.scalars(stmt).all())
