"""Endpoints de recetas: ver y editar la receta (insumos) de un producto.

Nota: editar la receta cambia el calculo de disponibilidad del producto, porque
las unidades fabricables dependen de los insumos y sus cantidades.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas.receta import RecetaEditar, RecetaInsumoEntrada, RecetaSalida
from app.db.session import get_db
from app.services.receta_service import (
    agregar_insumo_a_producto,
    quitar_insumo,
    reemplazar_receta_de_producto,
    ver_receta_de_producto,
)

router = APIRouter(tags=["recetas"])


@router.get("/productos/{producto_id}/receta", response_model=RecetaSalida)
def ver_receta(producto_id: int, db: Session = Depends(get_db)):
    """Devuelve la receta del producto: insumos con nombre, cantidad y unidad."""
    return ver_receta_de_producto(db, producto_id)


@router.put("/productos/{producto_id}/receta", response_model=RecetaSalida)
def reemplazar_receta(producto_id: int, datos: RecetaEditar, db: Session = Depends(get_db)):
    """Reemplaza la receta completa del producto por la lista de insumos enviada."""
    insumos = [i.model_dump() for i in datos.insumos]
    return reemplazar_receta_de_producto(db, producto_id, insumos)


@router.post("/productos/{producto_id}/receta/insumos", response_model=RecetaSalida)
def agregar_insumo(producto_id: int, datos: RecetaInsumoEntrada, db: Session = Depends(get_db)):
    """Agrega un insumo a la receta del producto y devuelve la receta actualizada."""
    return agregar_insumo_a_producto(
        db,
        producto_id,
        materia_prima_id=datos.materia_prima_id,
        cantidad=datos.cantidad,
        unidad=datos.unidad,
    )


@router.delete("/receta-insumos/{insumo_id}")
def borrar_insumo(insumo_id: int, db: Session = Depends(get_db)):
    """Quita un insumo de su receta (borra esa linea)."""
    quitar_insumo(db, insumo_id)
    return {"detail": f"Insumo {insumo_id} eliminado de la receta"}
