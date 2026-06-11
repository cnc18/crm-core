"""Paquete de modelos. Importa la Base y todos los modelos en un solo lugar.

Asi, al importar `app.models`, todas las tablas quedan registradas en `Base.metadata`
(necesario para que Alembic las detecte en autogenerate).
"""

from app.models.base import Base
from app.models.cliente import Cliente
from app.models.materia_prima import MateriaPrima
from app.models.oferta import Oferta
from app.models.pedido import Pedido, PedidoItem
from app.models.producto import Producto
from app.models.receta import Receta, RecetaInsumo

__all__ = [
    "Base",
    "Cliente",
    "MateriaPrima",
    "Oferta",
    "Pedido",
    "PedidoItem",
    "Producto",
    "Receta",
    "RecetaInsumo",
]
