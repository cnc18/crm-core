"""Entorno de Alembic: conecta las migraciones con la app (DATABASE_URL y modelos)."""

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# --- Integracion con la app -------------------------------------------------
# (1) DATABASE_URL leida desde .env (via config.py), NO escrita en alembic.ini.
from app.config import settings

# (2) Base declarativa + import EXPLICITO de todos los modelos. Cada import registra
#     sus tablas en Base.metadata. Sin esto, `--autogenerate` saldria vacio.
from app.models.base import Base
from app.models import cliente  # noqa: F401  (tabla clientes)
from app.models import materia_prima  # noqa: F401  (tabla materias_primas)
from app.models import producto  # noqa: F401  (tabla productos)
from app.models import receta  # noqa: F401  (tablas recetas y receta_insumos)

# ---------------------------------------------------------------------------

# Objeto de configuracion de Alembic (lee alembic.ini).
config = context.config

# Inyecta la URL real de la base de datos en la configuracion de Alembic.
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Configura el logging segun el alembic.ini.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata objetivo: lo que Alembic compara contra la base real para autogenerar.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Genera el SQL sin conectarse (modo 'offline')."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Se conecta a la base de datos real y aplica las migraciones (modo 'online')."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
