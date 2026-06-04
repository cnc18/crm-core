"""Endpoints del catalogo de productos."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.schemas.producto import ProductoOut
from app.api.schemas.stock import DisponibilidadOut
from app.db.session import get_db
from app.repositories.producto_repo import ProductoRepository
from app.services.stock_service import calcular_unidades_disponibles

router = APIRouter(prefix="/productos", tags=["productos"])


@router.get("/buscar", response_model=list[ProductoOut])
def buscar_productos(nombre: str = Query(..., description="Texto a buscar en el nombre"),
                     db: Session = Depends(get_db)):
    """Busca productos cuyo nombre contenga el texto (parcial, sin distinguir mayusculas)."""
    return ProductoRepository(db).buscar_por_nombre(nombre)


@router.get("/{producto_id}/disponibilidad", response_model=DisponibilidadOut)
def disponibilidad_producto(producto_id: int, db: Session = Depends(get_db)):
    """Devuelve cuantas unidades del producto se pueden fabricar con el stock actual."""
    resultado = calcular_unidades_disponibles(producto_id, db)
    if not resultado["encontrado"]:  # producto inexistente -> 404
        raise HTTPException(status_code=404, detail=resultado["motivo"])
    return resultado
