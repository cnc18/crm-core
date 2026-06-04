"""Acceso a datos de clientes (hereda el CRUD generico de BaseRepository)."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cliente import Cliente
from app.repositories.base_repo import BaseRepository


class ClienteRepository(BaseRepository[Cliente]):
    def __init__(self, db: Session):
        super().__init__(Cliente, db)

    def get_by_telefono(self, telefono: str) -> Cliente | None:
        """Busca un cliente por su telefono (campo unico). None si no existe."""
        return self.db.scalar(select(Cliente).where(Cliente.telefono == telefono))

    def crear_o_actualizar(
        self, telefono: str, nombre: str | None = None, canal: str = "whatsapp"
    ) -> Cliente:
        """Devuelve el cliente con ese telefono; si no existe, lo crea.

        Util para WhatsApp: ante un mensaje entrante, garantiza que el cliente exista
        sin arriesgar un telefono duplicado.
        """
        cliente = self.get_by_telefono(telefono)
        if cliente is None:
            cliente = self.create(telefono=telefono, nombre=nombre, canal_origen=canal)
        return cliente
