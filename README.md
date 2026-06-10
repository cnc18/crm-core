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
│   ├── routers/       # clientes, productos, materias_primas, ofertas, recetas
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

## API para el frontend

Referencia completa de **todos** los endpoints para construir el frontend.
Base URL: `http://localhost:8000`. Las docs interactivas (`/docs`) siempre reflejan
el estado real.

### Convenciones generales

- **Formato de error uniforme**: todo error responde `{ "detail": "<mensaje>" }` con su código HTTP:
  - `404` — recurso no encontrado (siempre la misma forma).
  - `400` — dato inválido por regla de negocio (ej. stock quedaría negativo).
  - `409` — conflicto (restricción de la base, ej. duplicado).
  - `422` — validación del body/params (Pydantic); el `detail` es una **lista** de errores por campo.
- **Borrado suave**: `DELETE` nunca elimina de la base; marca `activo=false` (materias/productos) o `activa=false` (ofertas). Los listados solo muestran activos.
- **Montos y cantidades** (`precio`, `stock_actual`, `cantidad`) viajan como **string** (tipo `Decimal`), ej. `"90000.00"`.
- **Fechas**: `fecha_inicio`/`fecha_fin` en formato `YYYY-MM-DD`; `created_at` es datetime ISO.
- **CORS** habilitado para `http://localhost:3000` (React) y `http://localhost:5173` (Vite).

---

### Salud

#### `GET /`
No recibe nada. Devuelve `200`:
```json
{ "status": "crm-core activo" }
```

---

### Clientes

#### `POST /clientes`
Registra un lead nuevo o devuelve el existente (por `telefono`). Idempotente.

**Recibe** (body):

| Campo | Tipo | Obligatorio | Default |
|-------|------|-------------|---------|
| `telefono` | string (no vacío) | sí | — |
| `nombre` | string \| null | no | `null` |
| `canal_origen` | string | no | `"whatsapp"` |

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

#### `GET /clientes/{telefono}`
**Recibe**: `telefono` en la ruta. **Devuelve** `200` el cliente (misma forma) o `404`.

---

### Productos

Forma de salida (`ProductoSalida`):
```json
{
  "id": 1,
  "nombre": "Invictus 100ml",
  "precio": "90000.00",
  "activo": true,
  "receta_id": 1,
  "created_at": "2026-06-03T18:56:47.907601"
}
```

#### `POST /productos`
**Recibe** (body):

| Campo | Tipo | Obligatorio |
|-------|------|-------------|
| `nombre` | string (no vacío) | sí |
| `precio` | number > 0 | sí |
| `receta_id` | int (la receta debe existir) | sí |

**Devuelve** `200` el producto creado. `404` si la `receta_id` no existe.

#### `GET /productos`
No recibe nada. **Devuelve** `200` — lista de productos **activos**, ordenada por nombre:
```json
[
  { "id": 1, "nombre": "Invictus 100ml", "precio": "90000.00", "activo": true, "receta_id": 1, "created_at": "2026-06-03T18:56:47.907601" }
]
```

#### `GET /productos/buscar?nombre=...`
**Recibe**: query param `nombre` (string, obligatorio). **Devuelve** `200` — lista de productos activos cuyo nombre contiene el texto (parcial, sin distinguir mayúsculas), ordenada por nombre. `[]` si no hay coincidencias.

#### `GET /productos/{producto_id}/disponibilidad`
Cuántas unidades se pueden fabricar con el stock actual (el insumo más escaso manda; una materia inactiva lo deja en 0).

**Recibe**: `producto_id` en la ruta. **Devuelve** `200`:
```json
{
  "encontrado": true,
  "nombre": "Invictus 100ml",
  "precio": "90000.00",
  "unidades_disponibles": 10,
  "disponible": true,
  "motivo": null
}
```
`404` si el producto no existe.

#### `PUT /productos/{producto_id}`
Edita el producto. Todos los campos opcionales (solo se aplican los enviados).

**Recibe** (body): `nombre` (string no vacío), `precio` (number > 0), `activo` (bool) — todos opcionales.
**Devuelve** `200` el producto actualizado. `404` si no existe. (Para reactivar: `{ "activo": true }`.)

#### `DELETE /productos/{producto_id}`
Borrado suave (`activo=false`). **Devuelve** `200` el producto con `activo: false`. `404` si no existe.

---

### Materias primas

Forma de salida (`MateriaPrimaSalida`):
```json
{
  "id": 3,
  "nombre": "Esencia Invictus",
  "tipo": "esencia",
  "stock_actual": "500.00",
  "unidad": "ml",
  "activo": true,
  "created_at": "2026-06-03T18:56:47.907601"
}
```

#### `POST /materias-primas`
**Recibe** (body):

| Campo | Tipo | Obligatorio |
|-------|------|-------------|
| `nombre` | string (no vacío) | sí |
| `tipo` | string (no vacío) | sí |
| `stock_actual` | number ≥ 0 | sí |
| `unidad` | `"ml"` \| `"gramos"` \| `"unidad"` | sí |

**Devuelve** `200` la materia creada.

#### `GET /materias-primas`
No recibe nada. **Devuelve** `200` — lista de materias **activas**, ordenada por nombre.

#### `GET /materias-primas/{id}`
**Recibe**: `id` en la ruta. **Devuelve** `200` la materia o `404`.

#### `PUT /materias-primas/{id}`
Edita la materia. **Recibe** (body, todos opcionales): `nombre` (no vacío), `tipo` (no vacío), `stock_actual` (≥ 0), `unidad`. **Devuelve** `200` la materia actualizada. `404` si no existe.

#### `DELETE /materias-primas/{id}`
Borrado suave (`activo=false`). **Devuelve** `200` la materia con `activo: false`. `404` si no existe.

#### `PATCH /materias-primas/{id}/stock`
Ajusta el stock. **Enviar exactamente uno** de los dos campos:

| Campo | Tipo | Efecto |
|-------|------|--------|
| `stock_actual` | number ≥ 0 | fija el stock a ese valor (reemplaza) |
| `cantidad` | number (+ o −) | suma/resta sobre el stock actual |

```json
{ "cantidad": -50 }
```
**Devuelve** `200` la materia con el stock actualizado. `404` si no existe; `400` si el resultado quedaría negativo.

---

### Ofertas

Forma de salida (`OfertaSalida`):
```json
{
  "id": 7,
  "titulo": "2x1 en cítricos",
  "descripcion": "Llevá 2 y pagá 1",
  "activa": true,
  "producto_id": null,
  "fecha_inicio": "2026-06-01",
  "fecha_fin": "2026-06-30",
  "creada_por": "manual",
  "created_at": "2026-06-09T12:00:00.000000"
}
```

#### `POST /ofertas`
**Recibe** (body):

| Campo | Tipo | Obligatorio | Default |
|-------|------|-------------|---------|
| `titulo` | string (no vacío) | sí | — |
| `descripcion` | string (no vacío) | sí | — |
| `producto_id` | int \| null (si va, debe existir) | no | `null` |
| `fecha_inicio` | date \| null | no | `null` |
| `fecha_fin` | date \| null (≥ `fecha_inicio`) | no | `null` |
| `creada_por` | string | no | `"manual"` |

**Devuelve** `200` la oferta creada. `404` si `producto_id` no existe; `422` si `fecha_fin < fecha_inicio`.

#### `GET /ofertas`
No recibe nada. **Devuelve** `200` — **todas** las ofertas (para el panel), ordenadas por `fecha_inicio` desc (las sin fecha al final).

#### `GET /ofertas/activas`
No recibe nada. **Devuelve** `200` — solo ofertas `activa=true` y **vigentes hoy** (lo consulta ventas), mismo orden.

#### `PUT /ofertas/{id}`
Edita la oferta. **Recibe** (body, todos opcionales): `titulo`, `descripcion`, `producto_id`, `fecha_inicio`, `fecha_fin`, `activa`. **Devuelve** `200` la oferta actualizada. `404` si no existe.

#### `DELETE /ofertas/{id}`
Borrado suave (`activa=false`). **Devuelve** `200` la oferta con `activa: false`. `404` si no existe.

#### `PATCH /ofertas/{id}/estado`
Activa/desactiva. **Recibe** (body): `{ "activa": true }` o `{ "activa": false }`. **Devuelve** `200` la oferta. `404` si no existe.

---

### Recetas

La receta pertenece a un producto. Editarla **cambia el cálculo de disponibilidad**
de ese producto.

Forma de salida (`RecetaSalida`):
```json
{
  "producto_id": 1,
  "producto_nombre": "Invictus 100ml",
  "receta_id": 1,
  "nombre": "Receta Invictus",
  "rinde_unidades": 1,
  "insumos": [
    { "materia_prima_id": 3, "nombre": "Esencia Invictus", "cantidad": "50.00", "unidad": "ml" },
    { "materia_prima_id": 5, "nombre": "Alcohol", "cantidad": "50.00", "unidad": "ml" }
  ]
}
```

#### `GET /productos/{producto_id}/receta`
**Recibe**: `producto_id` en la ruta. **Devuelve** `200` la receta (forma de arriba). `404` si el producto o su receta no existen.

#### `PUT /productos/{producto_id}/receta`
Reemplaza **toda** la receta por la lista enviada.

**Recibe** (body):
```json
{
  "insumos": [
    { "materia_prima_id": 3, "cantidad": 50, "unidad": "ml" },
    { "materia_prima_id": 5, "cantidad": 50, "unidad": "ml" }
  ]
}
```
Cada insumo: `materia_prima_id` (int, debe existir), `cantidad` (number > 0), `unidad` (`ml`/`gramos`/`unidad`).
**Devuelve** `200` la receta actualizada. `404` si el producto o alguna materia no existen.

#### `POST /productos/{producto_id}/receta/insumos`
Agrega un insumo. **Recibe** (body): un insumo (`materia_prima_id`, `cantidad` > 0, `unidad`). **Devuelve** `200` la receta **completa** actualizada. `404` si el producto o la materia no existen.

#### `DELETE /receta-insumos/{insumo_id}`
Quita una línea de la receta (borrado real de esa línea, no suave). **Recibe**: `insumo_id` en la ruta (el `materia_prima_id` **no** sirve aquí; es el id de la línea). **Devuelve** `200`:
```json
{ "detail": "Insumo 12 eliminado de la receta" }
```
`404` si no existe ese insumo.

> Nota: `RecetaSalida` aún **no** expone el `id` de cada línea de insumo, que es el que necesita este `DELETE`. Si el frontend va a borrar insumos, conviene agregarlo a `InsumoSalida`.

## Tests

```bash
pytest
```
