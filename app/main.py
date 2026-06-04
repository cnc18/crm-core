"""Arranca FastAPI, monta routers y middleware."""

from fastapi import FastAPI

from app.api.routers import clientes, productos

app = FastAPI(title="crm-core")

# Monta los endpoints por area.
app.include_router(productos.router)
app.include_router(clientes.router)


@app.get("/")
def raiz():
    """Endpoint de salud: confirma que la API esta corriendo."""
    return {"status": "crm-core activo"}
