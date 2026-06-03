# crm-core

CRM con arquitectura por capas (FastAPI + SQLAlchemy). Gestiona clientes/leads,
conversaciones con handoff a humano, pedidos y cálculo de stock a partir de recetas.

## Arquitectura

El flujo de una petición atraviesa las capas en un solo sentido. Cada capa solo
habla con la inmediatamente inferior:

```
API (routers + schemas)  →  Services (lógica)  →  Repositories (DB)  →  Models (tablas)
```

- **`api/`** — única puerta de entrada. Define endpoints y valida entrada/salida con Pydantic (`schemas/`). No contiene lógica de negocio.
- **`services/`** — la lógica de negocio. Orquesta repositorios, aplica reglas y emite eventos.
- **`repositories/`** — lo único que toca la base de datos. CRUD genérico en `base_repo.py`.
- **`models/`** — tablas SQLAlchemy.
- **`events/`** — publicación y manejo de eventos del dominio (p. ej. handoff a humano, stock bajo).
- **`db/`** — motor/sesión de SQLAlchemy y datos semilla.

> ★ El cálculo de receta en `services/stock_service.py` (cuántas unidades se
> pueden producir según las materias primas disponibles) es la pieza más crítica
> y la que más conviene cubrir con tests.

## Estructura

```
app/
├── main.py            # arranca FastAPI, monta routers, middleware
├── config.py          # settings (env vars, conexión DB, claves)
├── api/               # capa de API (la única puerta)
│   ├── deps.py
│   ├── routers/       # clientes, conversaciones, pedidos, productos, stock
│   └── schemas/       # modelos Pydantic (entrada/salida)
├── services/          # lógica de negocio
├── repositories/      # único acceso a la DB
├── models/            # tablas SQLAlchemy
├── events/            # emisor + handlers
└── db/                # session + init_db (semillas)
migrations/            # Alembic
tests/                 # pytest
scripts/               # utilidades sueltas
```

## Puesta en marcha

```bash
# 1. Entorno virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

# 2. Dependencias
pip install -r requirements.txt

# 3. Variables de entorno
copy .env.example .env        # Windows  (cp en Linux/Mac)
#    luego edita .env con tus credenciales

# 4. Migraciones (tras configurar migrations/env.py)
alembic upgrade head

# 5. Datos semilla (materias primas, recetas)
python -m app.db.init_db
```

## Ejecutar

```bash
uvicorn app.main:app --reload
```

Docs interactivas en http://localhost:8000/docs

## Tests

```bash
pytest
```
