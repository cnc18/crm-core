"""Logica de negocio: alta/actualizacion de lead y cambio de estado."""

from sqlalchemy.orm import Session

from app.models.cliente import Cliente
from app.repositories.cliente_repo import ClienteRepository


def registrar_o_actualizar_lead(
    telefono: str, db: Session, nombre: str | None = None, canal: str = "whatsapp"
) -> Cliente:
    """Registra el lead si es nuevo, o devuelve el existente (segun su telefono)."""
    repo = ClienteRepository(db)
    return repo.crear_o_actualizar(telefono, nombre, canal)


def cambiar_estado_lead(telefono: str, nuevo_estado: str, db: Session) -> Cliente:
    """Cambia el estado_lead de un cliente (ej: nuevo -> contactado -> cliente)."""
    repo = ClienteRepository(db)
    cliente = repo.get_by_telefono(telefono)
    if cliente is None:
        raise ValueError(f"No existe un cliente con telefono {telefono}")

    cliente.estado_lead = nuevo_estado
    db.commit()
    db.refresh(cliente)  # recarga el cliente con el cambio ya guardado
    return cliente
