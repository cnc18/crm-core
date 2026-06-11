"""Endpoints del catalogo de productos."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.schemas.producto import ProductoCrear, ProductoEditar, ProductoSalida
from app.api.schemas.stock import DisponibilidadOut
from app.db.session import get_db
from app.errors import NotFoundError
from app.repositories.producto_repo import ProductoRepository
from app.services.producto_service import (
    crear_producto,
    desactivar_producto,
    editar_producto,
    listar_productos,
)
from app.services.stock_service import calcular_unidades_disponibles

router = APIRouter(prefix="/productos", tags=["productos"])


@router.post("", response_model=ProductoSalida)
def agregar(datos: ProductoCrear, db: Session = Depends(get_db)):
    """Agrega un producto nuevo; se le crea una receta vacia automaticamente."""
    return crear_producto(db, nombre=datos.nombre, precio=datos.precio)


@router.get("", response_model=list[ProductoSalida])
def listar(db: Session = Depends(get_db)):
    """Lista solo los productos activos."""
    return listar_productos(db)


@router.put("/{producto_id}", response_model=ProductoSalida)
def editar(producto_id: int, datos: ProductoEditar, db: Session = Depends(get_db)):
    """Edita campos de un producto (nombre, precio, activo)."""
    return editar_producto(db, producto_id, **datos.model_dump(exclude_unset=True))


@router.delete("/{producto_id}", response_model=ProductoSalida)
def borrar(producto_id: int, db: Session = Depends(get_db)):
    """Borrado SUAVE: marca activo=false, no elimina de la base."""
    return desactivar_producto(db, producto_id)


@router.get("/buscar", response_model=list[ProductoSalida])
def buscar_productos(nombre: str = Query(..., description="Texto a buscar en el nombre"),
                     db: Session = Depends(get_db)):
    """Busca productos cuyo nombre contenga el texto (parcial, sin distinguir mayusculas)."""
    return ProductoRepository(db).buscar_por_nombre(nombre)


@router.get("/{producto_id}/disponibilidad", response_model=DisponibilidadOut)
def disponibilidad_producto(producto_id: int, db: Session = Depends(get_db)):
    """Devuelve cuantas unidades del producto se pueden fabricar con el stock actual."""
    resultado = calcular_unidades_disponibles(producto_id, db)
    if not resultado["encontrado"]:  # producto inexistente -> 404 uniforme
        raise NotFoundError(resultado["motivo"])
    return resultado
