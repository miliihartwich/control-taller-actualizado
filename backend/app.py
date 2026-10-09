from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import timedelta
import os
from routes import register_blueprints
from pathlib import Path

# Detectar entorno (si no está, asumimos production)
FLASK_ENV = os.getenv("FLASK_ENV", "production").lower()

if FLASK_ENV in ("dev", "development"):
    dotenv_path = Path(__file__).parent / ".env.development"
    if dotenv_path.exists():
        load_dotenv(dotenv_path=dotenv_path, override=False)

app = Flask(__name__, static_folder='dist')

@app.get("/__routes__")
def __routes__():
    rutas = []
    for rule in app.url_map.iter_rules():
        rutas.append({"rule": str(rule), "methods": sorted(rule.methods)})
    return jsonify(sorted(rutas, key=lambda r: r["rule"]))

APP_ENV = os.environ.get("APP_ENV", "local").lower()

# ===== Flag para modo dev sin auth =====
DEV_NO_AUTH = os.getenv("DEV_NO_AUTH", "0") == "1"

# ===== JWT: access + refresh en cookies (híbrido) =====
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY") or (_ for _ in ()).throw(RuntimeError("Falta JWT_SECRET_KEY"))
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]  # sigue aceptando Authorization si ya lo usás
app.config["JWT_ACCESS_TOKEN_EXPIRES"]  = timedelta(hours=12)   # token corto/mediano
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)    # refresh persistente

# Cookies (ajustá en prod HTTPS)
app.config["JWT_COOKIE_SECURE"]      = os.getenv("JWT_COOKIE_SECURE", "False") == "True"  # True en prod con HTTPS
app.config["JWT_COOKIE_SAMESITE"]    = os.getenv("JWT_COOKIE_SAMESITE", "Lax")
app.config["JWT_COOKIE_CSRF_PROTECT"] = False  # para simplificar fetch/axios

jwt = JWTManager(app)

# ===== CORS =====
FRONT_ORIGIN = os.getenv("FRONT_ORIGIN", "http://localhost:5173")
CORS(
    app,
    resources={r"/*": {"origins": [FRONT_ORIGIN]}},
    supports_credentials=True,  # <- necesario para que viajen cookies
    allow_headers=["Content-Type", "Authorization"],
)


# Healthcheck
@app.get("/health")
def health():
    return jsonify({"ok": True, "env": APP_ENV}), 200

register_blueprints(app)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
