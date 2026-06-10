"""Endpoints de materias primas: inventario de insumos (CRUD con borrado suave)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas.materia_prima import (
    AjusteStock,
    MateriaPrimaCrear,
    MateriaPrimaEditar,
    MateriaPrimaSalida,
)
from app.db.session import get_db
from app.services.materia_prima_service import (
    ajustar_stock,
    crear_materia,
    desactivar_materia,
    editar_materia,
    listar_materias,
    obtener_materia,
)

router = APIRouter(prefix="/materias-primas", tags=["materias-primas"])


@router.post("", response_model=MateriaPrimaSalida)
def agregar(datos: MateriaPrimaCrear, db: Session = Depends(get_db)):
    """Agrega una materia prima nueva."""
    return crear_materia(
        db,
        nombre=datos.nombre,
        tipo=datos.tipo,
        stock_actual=datos.stock_actual,
        unidad=datos.unidad,
    )


@router.get("", response_model=list[MateriaPrimaSalida])
def listar(db: Session = Depends(get_db)):
    """Lista solo las materias primas activas."""
    return listar_materias(db)


@router.get("/{materia_id}", response_model=MateriaPrimaSalida)
def ver(materia_id: int, db: Session = Depends(get_db)):
    """Devuelve una materia prima por id."""
    return obtener_materia(db, materia_id)


@router.put("/{materia_id}", response_model=MateriaPrimaSalida)
def editar(materia_id: int, datos: MateriaPrimaEditar, db: Session = Depends(get_db)):
    """Edita campos de una materia (nombre, unidad, etc.)."""
    return editar_materia(db, materia_id, **datos.model_dump(exclude_unset=True))


@router.delete("/{materia_id}", response_model=MateriaPrimaSalida)
def borrar(materia_id: int, db: Session = Depends(get_db)):
    """Borrado SUAVE: marca activo=false, no elimina de la base."""
    return desactivar_materia(db, materia_id)


@router.patch("/{materia_id}/stock", response_model=MateriaPrimaSalida)
def ajustar(materia_id: int, datos: AjusteStock, db: Session = Depends(get_db)):
    """Ajusta el stock: valor absoluto (stock_actual) o delta (cantidad +/-)."""
    # Errores (no existe -> 404, stock negativo -> 400) los maneja el handler global.
    return ajustar_stock(
        db, materia_id, stock_actual=datos.stock_actual, cantidad=datos.cantidad
    )
