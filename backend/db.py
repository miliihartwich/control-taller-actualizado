import os
import psycopg2
from dotenv import load_dotenv

# Cargar variables de entorno desde .env (en el mismo dir)
load_dotenv()

# ÚNICA fuente: DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("Falta DATABASE_URL en variables de entorno.")

# Normaliza esquema antiguo si aparece
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Decide sslmode:
# 1) Si viene en variables explícitas (PGSSLMODE/DB_SSLMODE/SSLMODE), úsalo.
# 2) Si no, usa APP_ENV: aws|production => require; si no => disable.
sslmode = os.getenv("PGSSLMODE") or os.getenv("DB_SSLMODE") or os.getenv("SSLMODE")
if not sslmode:
    APP_ENV = os.getenv("APP_ENV", "local").lower()
    sslmode = "require" if APP_ENV in ("aws", "production", "prod") else "disable"

def get_db_connection():
    """Devuelve conexión psycopg2. Respeta sslmode decidido arriba aun si DATABASE_URL no lo trae."""
    try:
        return psycopg2.connect(
            DATABASE_URL,
            sslmode=sslmode,
            connect_timeout=5,   # ✅ CLAVE: evita cuelgues y timeouts de gunicorn
        )
    except Exception as e:
        raise RuntimeError(f"Error al conectar a la base de datos: {e}")

