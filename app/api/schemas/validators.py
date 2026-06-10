"""Validadores reutilizables para los schemas (mensajes claros y en español)."""

from typing import Annotated

from pydantic import AfterValidator


def _no_vacio(v: str) -> str:
    """Rechaza texto vacio o solo espacios; devuelve el texto sin espacios sobrantes."""
    if not v.strip():
        raise ValueError("no puede estar vacío")
    return v.strip()


# Texto obligatorio: no admite "" ni "   ". Usar tal cual en campos requeridos,
# o como `TextoObligatorio | None = None` en campos opcionales (valida solo si viene).
TextoObligatorio = Annotated[str, AfterValidator(_no_vacio)]
