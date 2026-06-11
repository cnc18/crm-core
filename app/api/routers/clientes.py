"""Endpoints de clientes y leads."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas.cliente import ClienteCreate, ClienteOut, ClienteUpdate
from app.db.session import get_db
from app.errors import NotFoundError
from app.repositories.cliente_repo import ClienteRepository
from app.services.cliente_service import actualizar_cliente, registrar_o_actualizar_lead

router = APIRouter(prefix="/clientes", tags=["clientes"])


@router.post("", response_model=ClienteOut)
def crear_cliente(datos: ClienteCreate, db: Session = Depends(get_db)):
    """Registra un lead nuevo o devuelve el existente (segun su telefono)."""
    return registrar_o_actualizar_lead(
        datos.telefono, db, nombre=datos.nombre, canal=datos.canal_origen
    )


@router.get("", response_model=list[ClienteOut])
def listar_clientes(db: Session = Depends(get_db)):
    """Lista todos los clientes/leads con su estado_lead (para el pipeline)."""
    return ClienteRepository(db).get_all()


@router.get("/{telefono}", response_model=ClienteOut)
def obtener_cliente(telefono: str, db: Session = Depends(get_db)):
    """Devuelve los datos de un cliente buscandolo por su telefono."""
    cliente = ClienteRepository(db).get_by_telefono(telefono)
    if cliente is None:  # no existe -> 404 uniforme
        raise NotFoundError(f"No existe un cliente con telefono {telefono}")
    return cliente


@router.put("/{telefono}", response_model=ClienteOut)
def editar_cliente(telefono: str, datos: ClienteUpdate, db: Session = Depends(get_db)):
    """Actualiza un cliente (p. ej. cambia estado_lead). Solo toca los campos enviados."""
    cambios = datos.model_dump(exclude_unset=True)
    return actualizar_cliente(telefono, db, cambios)
