"""Acceso a datos de pedidos (hereda el CRUD generico de BaseRepository)."""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.pedido import Pedido, PedidoItem
from app.repositories.base_repo import BaseRepository


class PedidoRepository(BaseRepository[Pedido]):
    def __init__(self, db: Session):
        super().__init__(Pedido, db)

    def crear(self, cliente_id: int, total: Decimal, items: list[dict]) -> Pedido:
        """Crea un pedido con sus items en una sola operacion.

        Cada item: {'producto_id', 'cantidad', 'precio_unitario'}.
        """
        pedido = Pedido(
            cliente_id=cliente_id,
            total=total,
            items=[
                PedidoItem(
                    producto_id=it["producto_id"],
                    cantidad=it["cantidad"],
                    precio_unitario=it["precio_unitario"],
                )
                for it in items
            ],
        )
        self.db.add(pedido)
        self.db.commit()
        self.db.refresh(pedido)
        return pedido

    def get_con_items(self, pedido_id: int) -> Pedido | None:
        """Devuelve el pedido con sus items y el producto de cada uno ya cargados."""
        stmt = (
            select(Pedido)
            .where(Pedido.id == pedido_id)
            .options(joinedload(Pedido.items).joinedload(PedidoItem.producto))
        )
        return self.db.scalars(stmt).unique().one_or_none()

    def listar(self, estado: str | None = None) -> list[Pedido]:
        """Lista pedidos, opcionalmente filtrados por estado. Mas nuevos primero."""
        stmt = select(Pedido).order_by(Pedido.created_at.desc())
        if estado is not None:
            stmt = stmt.where(Pedido.estado == estado)
        return list(self.db.scalars(stmt).all())

    def actualizar_estado(self, pedido: Pedido, estado: str) -> Pedido:
        """Cambia el estado del pedido y guarda."""
        pedido.estado = estado
        self.db.commit()
        self.db.refresh(pedido)
        return pedido

    def marcar_descontado(self, pedido: Pedido, descontado: bool) -> Pedido:
        """Marca si las materias primas del pedido ya fueron descontadas del stock."""
        pedido.descontado = descontado
        self.db.commit()
        self.db.refresh(pedido)
        return pedido
