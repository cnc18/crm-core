"""Arranca FastAPI, monta routers y middleware."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import clientes, materias_primas, ofertas, productos, recetas
from app.errors import registrar_manejadores

app = FastAPI(title="crm-core")

# Handlers comunes: traducen errores de dominio a {"detail": ...} con su codigo.
registrar_manejadores(app)

# CORS: habilita que el frontend (otro origen) consuma la API desde el navegador.
# Origenes tipicos en desarrollo: React (3000) y Vite (5173).
# PRODUCCION: restringi allow_origins a los dominios reales del frontend
# (ej. ["https://mi-crm.com"]); NO uses "*" ni dejes localhost en produccion.
origenes_dev = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origenes_dev,
    allow_credentials=True,
    allow_methods=["*"],  # permite GET, POST, PUT, PATCH, DELETE, OPTIONS
    allow_headers=["*"],
)

# Monta los endpoints por area.
app.include_router(productos.router)
app.include_router(clientes.router)
app.include_router(ofertas.router)
app.include_router(materias_primas.router)
app.include_router(recetas.router)


@app.get("/")
def raiz():
    """Endpoint de salud: confirma que la API esta corriendo."""
    return {"status": "crm-core activo"}
