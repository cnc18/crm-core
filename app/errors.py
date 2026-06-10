"""Errores de dominio y manejadores comunes para respuestas de error uniformes.

Toda respuesta de error sigue el formato {"detail": <mensaje>} con el codigo HTTP
correcto. Los servicios lanzan estas excepciones y los handlers (registrados en
main.py) las traducen a JSON, asi "no encontrado" siempre responde igual.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError


class AppError(Exception):
    """Error de dominio con un codigo HTTP asociado."""

    status_code = 400

    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class NotFoundError(AppError):
    """Recurso inexistente -> 404."""

    status_code = 404


class InvalidDataError(AppError):
    """Dato invalido por regla de negocio -> 400."""

    status_code = 400


class ConflictError(AppError):
    """Conflicto con el estado actual (ej. duplicado) -> 409."""

    status_code = 409


def registrar_manejadores(app: FastAPI) -> None:
    """Registra los handlers que devuelven {"detail": ...} con el codigo correcto."""

    @app.exception_handler(AppError)
    async def _app_error(request: Request, exc: AppError):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(IntegrityError)
    async def _integrity_error(request: Request, exc: IntegrityError):
        # Restriccion violada en la base (ej. unicidad) -> conflicto, no un 500.
        return JSONResponse(
            status_code=409,
            content={"detail": "Conflicto: la operacion viola una restriccion de la base"},
        )
