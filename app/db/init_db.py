"""Datos semilla (seed): carga datos de prueba en la base.

Es idempotente: busca cada registro por su nombre/telefono antes de crearlo,
asi que se puede ejecutar varias veces sin duplicar datos.

Ejecutar:  python -m app.db.init_db
"""

from decimal import Decimal

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.cliente import Cliente
from app.models.materia_prima import MateriaPrima
from app.models.producto import Producto
from app.models.receta import Receta, RecetaInsumo

ALCOHOL = "Alcohol perfumeria"


def seed() -> None:
    db = SessionLocal()
    try:
        # ---------- Materias primas: (nombre, tipo, stock_actual, unidad) ----------
        datos_materias = [
            ("Esencia Invictus", "esencia", 300, "ml"),
            ("Esencia Sauvage", "esencia", 150, "ml"),
            (ALCOHOL, "alcohol", 5000, "ml"),
            ("Frasco 50ml", "frasco", 40, "unidad"),
            ("Frasco 100ml", "frasco", 20, "unidad"),
        ]
        materias = {}
        for nombre, tipo, stock, unidad in datos_materias:
            mp = db.scalar(select(MateriaPrima).where(MateriaPrima.nombre == nombre))
            if mp is None:  # solo crear si no existe
                mp = MateriaPrima(
                    nombre=nombre,
                    tipo=tipo,
                    stock_actual=Decimal(str(stock)),
                    unidad=unidad,
                )
                db.add(mp)
            materias[nombre] = mp
        db.flush()  # asigna IDs a las materias nuevas (para las FK de los insumos)

        # ---------- Recetas: nombre -> (rinde, [(materia, cantidad, unidad), ...]) ----------
        datos_recetas = {
            "Invictus 100ml": (1, [
                ("Esencia Invictus", 30, "ml"),
                (ALCOHOL, 70, "ml"),
                ("Frasco 100ml", 1, "unidad"),
            ]),
            "Sauvage 50ml": (1, [
                ("Esencia Sauvage", 15, "ml"),
                (ALCOHOL, 35, "ml"),
                ("Frasco 50ml", 1, "unidad"),
            ]),
        }
        recetas = {}
        for nombre, (rinde, insumos) in datos_recetas.items():
            receta = db.scalar(select(Receta).where(Receta.nombre == nombre))
            if receta is None:
                receta = Receta(nombre=nombre, rinde_unidades=rinde)
                for mat_nombre, cantidad, unidad in insumos:
                    receta.insumos.append(
                        RecetaInsumo(
                            materia_prima=materias[mat_nombre],
                            cantidad=Decimal(str(cantidad)),
                            unidad=unidad,
                        )
                    )
                db.add(receta)
            recetas[nombre] = receta
        db.flush()

        # ---------- Productos: (nombre, precio, nombre_receta) ----------
        datos_productos = [
            ("Invictus 100ml", 90000, "Invictus 100ml"),
            ("Sauvage 50ml", 55000, "Sauvage 50ml"),
        ]
        for nombre, precio, receta_nombre in datos_productos:
            prod = db.scalar(select(Producto).where(Producto.nombre == nombre))
            if prod is None:
                db.add(
                    Producto(
                        nombre=nombre,
                        precio=Decimal(str(precio)),
                        receta=recetas[receta_nombre],
                    )
                )

        # ---------- Clientes: (telefono, nombre) ----------
        datos_clientes = [
            ("+573001112233", "Cliente Demo Uno"),
            ("+573004445566", "Cliente Demo Dos"),
        ]
        for telefono, nombre in datos_clientes:
            cli = db.scalar(select(Cliente).where(Cliente.telefono == telefono))
            if cli is None:
                db.add(Cliente(telefono=telefono, nombre=nombre))

        db.commit()
        print("Seed completado: datos de prueba cargados (sin duplicar los que ya existian).")
    except Exception:
        db.rollback()  # si algo falla, no deja datos a medias
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
