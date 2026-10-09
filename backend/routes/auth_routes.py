from flask import Blueprint, request, jsonify
from db import get_db_connection
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    set_access_cookies, set_refresh_cookies,
    jwt_required, get_jwt_identity, unset_jwt_cookies
)
import os

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')

DEV_NO_AUTH = os.getenv("DEV_NO_AUTH", "0") == "1"

# POST /auth/login
@auth_bp.post('/login')
def login():
    data = request.get_json(silent=True) or {}
    usuario = data.get('usuario')
    contrasena = data.get('contrasena')
    if not usuario or not contrasena:
        return jsonify({'error': 'Faltan datos obligatorios (usuario, contrasena).'}), 400

    conn = get_db_connection(); cur = conn.cursor()
    try:
        cur.execute('SELECT contrasena, rol, cedula FROM usuario WHERE usuario=%s', (usuario,))
        row = cur.fetchone()
        if not row:
            return jsonify({'error': 'Usuario no encontrado.'}), 404
        pass_db, rol, cedula = row
        if pass_db != contrasena:
            return jsonify({'error': 'Contraseña incorrecta.'}), 401

        payload = {'usuario': usuario, 'rol': rol, 'cedula': cedula}

        if DEV_NO_AUTH:
            # Modo dev: devolver payload sin JWT
            return jsonify(payload), 200
        else:
            # Modo prod: flujo con tokens/cookies
            access_token  = create_access_token(identity=usuario)
            refresh_token = create_refresh_token(identity=usuario)

            resp = jsonify(rol=rol, cedula=cedula)
            # cookie de acceso (vida corta) + cookie de refresh (30 días)
            set_access_cookies(resp, access_token)
            set_refresh_cookies(resp, refresh_token)
            return resp, 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        cur.close(); conn.close()

# POST /auth/refresh  (usa cookie refresh)
@auth_bp.post('/refresh')
@jwt_required(refresh=True)
def refresh():
    uid = get_jwt_identity()
    new_access = create_access_token(identity=uid)
    resp = jsonify(ok=True)
    set_access_cookies(resp, new_access)
    return resp, 200

# POST /auth/logout  (borra ambas cookies)
@auth_bp.post('/logout')
@jwt_required(optional=True)
def logout():
    resp = jsonify(ok=True)
    unset_jwt_cookies(resp)
    return resp, 200
