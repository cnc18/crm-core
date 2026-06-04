"""Arranca FastAPI, monta routers y middleware."""

from fastapi import FastAPI

app = FastAPI(title="crm-core")


@app.get("/")
def raiz():
    """Endpoint de salud: confirma que la API esta corriendo."""
    return {"status": "crm-core activo"}
