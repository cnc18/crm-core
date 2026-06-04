"""Endpoints de clientes y leads."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas.cliente import ClienteCreate, ClienteOut
from app.db.session import get_db
from app.repositories.cliente_repo import ClienteRepository
from app.services.cliente_service import registrar_o_actualizar_lead

router = APIRouter(prefix="/clientes", tags=["clientes"])


@router.post("", response_model=ClienteOut)
def crear_cliente(datos: ClienteCreate, db: Session = Depends(get_db)):
    """Registra un lead nuevo o devuelve el existente (segun su telefono)."""
    return registrar_o_actualizar_lead(
        datos.telefono, db, nombre=datos.nombre, canal=datos.canal_origen
    )


@router.get("/{telefono}", response_model=ClienteOut)
def obtener_cliente(telefono: str, db: Session = Depends(get_db)):
    """Devuelve los datos de un cliente buscandolo por su telefono."""
    cliente = ClienteRepository(db).get_by_telefono(telefono)
    if cliente is None:  # no existe -> 404
        raise HTTPException(status_code=404, detail=f"No existe un cliente con telefono {telefono}")
    return cliente
