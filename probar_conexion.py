"""Script de prueba: intenta conectarse a la base de datos crm_dev y reporta el resultado."""

from sqlalchemy import text

from app.db.session import engine


def main():
    try:
        # Abre una conexion y ejecuta una consulta minima ("SELECT 1").
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("conexion OK")
        print(f"Conectado a: {engine.url}")
    except Exception as error:
        print("ERROR de conexion:")
        print(error)


if __name__ == "__main__":
    main()
