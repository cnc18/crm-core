"""Endpoints de estadisticas: datos agregados para el dashboard del frontend."""

from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import estadisticas_service

router = APIRouter(prefix="/estadisticas", tags=["estadisticas"])


@router.get("/ping")
def ping():
    """Prueba: confirma que el router quedo montado."""
    return {"ok": True}


@router.get("/resumen")
def resumen(db: Session = Depends(get_db)):
    """Numeros clave para las tarjetas de arriba del dashboard."""
    return estadisticas_service.resumen(db)


@router.get("/ventas-periodo")
def ventas_periodo(
    periodo: Literal["dia", "semana", "mes"] = "mes",
    db: Session = Depends(get_db),
):
    """Serie de ingresos por periodo (ultimos 12 puntos) para la grafica de lineas/barras."""
    return estadisticas_service.ventas_por_periodo(db, periodo)


@router.get("/leads-estado")
def leads_estado(db: Session = Depends(get_db)):
    """Conteo de clientes por estado_lead, para la grafica de dona/barras."""
    return estadisticas_service.leads_por_estado(db)


@router.get("/top-productos")
def top_productos(
    limite: int = Query(5, ge=1, le=50, description="Cuantos productos devolver"),
    db: Session = Depends(get_db),
):
    """Productos mas vendidos (cantidad e ingreso) para la lista/grafica."""
    return estadisticas_service.top_productos(db, limite)
