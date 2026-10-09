import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from psycopg2 import OperationalError

load_dotenv(Path(__file__).resolve().parent / ".env")


def test_db_connection():
    password = os.getenv("PGPASSWORD")
    if not password:
        raise RuntimeError("Falta PGPASSWORD en las variables de entorno o en .env")

    try:
        conn = psycopg2.connect(
            dbname=os.getenv("PGDATABASE", "base_de_datos_taller"),
            user=os.getenv("PGUSER", "postgres"),
            password=password,
            host=os.getenv("PGHOST", "localhost"),
            port=os.getenv("PGPORT", "5432"),
            client_encoding="utf8",
        )
        print("Conexion exitosa a la base de datos local")
        conn.close()
    except OperationalError as e:
        print(f"Error al conectar a la base de datos: {e}")


if __name__ == "__main__":
    test_db_connection()
