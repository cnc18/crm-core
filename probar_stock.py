"""Prueba manual del servicio de stock.

Muestra cuantas unidades se pueden fabricar de los productos demo,
segun el stock actual de materias primas.

Ejecutar:  python probar_stock.py
"""

import json

from app.db.session import SessionLocal
from app.repositories.producto_repo import ProductoRepository
from app.services.stock_service import calcular_unidades_disponibles


def main() -> None:
    db = SessionLocal()
    try:
        repo = ProductoRepository(db)
        for nombre in ("Invictus 100ml", "Sauvage 50ml"):
            # Buscar el producto por nombre para no depender de ids fijos.
            encontrados = repo.buscar_por_nombre(nombre)
            if not encontrados:
                print(f"[!] No encontre el producto '{nombre}'")
                continue

            producto = encontrados[0]
            resultado = calcular_unidades_disponibles(producto.id, db)
            print(json.dumps(resultado, default=str, ensure_ascii=False, indent=2))
    finally:
        db.close()


if __name__ == "__main__":
    main()
