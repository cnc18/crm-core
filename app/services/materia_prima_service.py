"""Logica de negocio de materias primas: alta, edicion, baja suave y ajuste de stock."""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.errors import InvalidDataError, NotFoundError
from app.models.materia_prima import MateriaPrima
from app.repositories.materia_prima_repo import MateriaPrimaRepository


def _get_o_404(repo: MateriaPrimaRepository, materia_id: int) -> MateriaPrima:
    """Resuelve id -> objeto, o lanza NotFoundError (404)."""
    materia = repo.get_by_id(materia_id)
    if materia is None:
        raise NotFoundError(f"No existe una materia prima con id {materia_id}")
    return materia


def crear_materia(
    db: Session, nombre: str, tipo: str, stock_actual: Decimal, unidad: str
) -> MateriaPrima:
    """Crea una materia prima nueva (activa por default segun el modelo)."""
    return MateriaPrimaRepository(db).create(
        nombre=nombre, tipo=tipo, stock_actual=stock_actual, unidad=unidad
    )


def listar_materias(db: Session) -> list[MateriaPrima]:
    """Lista solo las materias primas activas."""
    return MateriaPrimaRepository(db).listar_activas()


def obtener_materia(db: Session, materia_id: int) -> MateriaPrima:
    """Devuelve una materia prima por id (404 si no existe)."""
    return _get_o_404(MateriaPrimaRepository(db), materia_id)


def editar_materia(db: Session, materia_id: int, **cambios) -> MateriaPrima:
    """Edita campos de una materia existente. Ignora claves con valor None."""
    repo = MateriaPrimaRepository(db)
    materia = _get_o_404(repo, materia_id)
    cambios = {k: v for k, v in cambios.items() if v is not None}
    return repo.actualizar(materia, **cambios)


def desactivar_materia(db: Session, materia_id: int) -> MateriaPrima:
    """Borrado SUAVE: marca activo=false (no se elimina de la base)."""
    repo = MateriaPrimaRepository(db)
    materia = _get_o_404(repo, materia_id)
    return repo.desactivar(materia)


def ajustar_stock(
    db: Session,
    materia_id: int,
    stock_actual: Decimal | None = None,
    cantidad: Decimal | None = None,
) -> MateriaPrima:
    """Ajusta el stock por valor absoluto (stock_actual) o por delta (cantidad).

    El resultado no puede quedar negativo.
    """
    repo = MateriaPrimaRepository(db)
    materia = _get_o_404(repo, materia_id)

    if stock_actual is not None:
        nuevo = stock_actual  # reemplaza el valor
    else:
        nuevo = materia.stock_actual + cantidad  # suma/resta sobre lo actual

    if nuevo < 0:
        raise InvalidDataError("El stock no puede quedar negativo")
    return repo.ajustar_stock(materia, nuevo)
