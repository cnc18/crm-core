"""Motor y sesion de SQLAlchemy: engine, fabrica de sesiones y dependencia get_db()."""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings

# Engine: la conexion al motor de PostgreSQL, usando la URL leida del .env.
engine = create_engine(settings.DATABASE_URL)

# Fabrica de sesiones: cada SessionLocal() abre una nueva sesion de trabajo.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Iterator[Session]:
    """Dependencia de FastAPI: entrega una sesion y la cierra siempre al terminar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
