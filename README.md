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

## API para el agente

Contrato de los endpoints disponibles (Etapa 1). Base URL: `http://localhost:8000`.
Esta es la interfaz que el agente consumirá en la Etapa 2.

### `GET /`
Salud del servicio. No recibe nada.

```json
{ "status": "crm-core activo" }
```

---

### `POST /clientes`
Registra un lead nuevo o devuelve el existente (identificado por `telefono`).
Es idempotente: si el teléfono ya existe, devuelve ese cliente sin duplicar.

**Recibe** (JSON body):

| Campo | Tipo | Obligatorio | Default |
|-------|------|-------------|---------|
| `telefono` | string | sí | — |
| `nombre` | string \| null | no | `null` |
| `canal_origen` | string | no | `"whatsapp"` |

```json
{ "telefono": "+573001234567", "nombre": "Cliente de Prueba", "canal_origen": "whatsapp" }
```

**Devuelve** `200` — el cliente:

```json
{
  "id": 4,
  "telefono": "+573001234567",
  "nombre": "Cliente de Prueba",
  "estado_lead": "nuevo",
  "canal_origen": "whatsapp",
  "created_at": "2026-06-03T18:56:47.907601"
}
```

---

### `GET /clientes/{telefono}`
Devuelve los datos de un cliente por su teléfono.

**Recibe**: `telefono` en la ruta (ej. `/clientes/+573001234567`).

**Devuelve** `200` — el cliente (misma forma que arriba). Si no existe, `404`:

```json
{ "detail": "No existe un cliente con telefono +570000000000" }
```

---

### `GET /productos/buscar?nombre=...`
Busca productos cuyo nombre contenga el texto (parcial, sin distinguir mayúsculas).

**Recibe**: query param `nombre` (string, obligatorio). Ej: `/productos/buscar?nombre=invictus`

**Devuelve** `200` — lista de productos (vacía `[]` si no hay coincidencias):

```json
[
  {
    "id": 1,
    "nombre": "Invictus 100ml",
    "precio": "90000.00",
    "activo": true,
    "receta_id": 1,
    "created_at": "2026-06-03T18:56:47.907601"
  }
]
```

---

### `GET /productos/{producto_id}/disponibilidad`
Calcula cuántas unidades del producto se pueden fabricar con el stock actual de
materias primas (el insumo más escaso limita la producción).

**Recibe**: `producto_id` en la ruta (entero). Ej: `/productos/1/disponibilidad`

**Devuelve** `200`:

```json
{
  "nombre": "Invictus 100ml",
  "precio": "90000.00",
  "unidades_disponibles": 10,
  "disponible": true
}
```

Si el producto no existe, `404`:

```json
{ "detail": "No existe un producto con id 9999" }
```

## Tests

```bash
pytest
```
