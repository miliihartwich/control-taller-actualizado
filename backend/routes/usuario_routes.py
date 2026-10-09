from flask import Blueprint, request, jsonify
from db import get_db_connection
from flask_jwt_extended import jwt_required, get_jwt_identity
import os

usuario_bp = Blueprint('usuario_bp', __name__)

DEV_NO_AUTH = os.getenv("DEV_NO_AUTH", "0") == "1"

@usuario_bp.route('/users/me', methods=['GET'])
def me():
    if not DEV_NO_AUTH:
        # Solo requerir JWT si no es modo dev
        jwt_required()
        uid = get_jwt_identity()
    else:
        # En modo dev, obtener usuario de algún lado, o mock
        uid = request.args.get('usuario') or 'dev_user'  # o algo, pero como no se llama, dejar simple

    # si querés, podés traer rol/cedula:
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT rol, cedula FROM usuario WHERE usuario = %s", (uid,))
        row = cur.fetchone()
        if not row:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        rol, cedula = row
        return jsonify(usuario=uid, rol=rol, cedula=cedula), 200
    finally:
        cur.close()
        conn.close()

# Ruta para registrar usuarios
@usuario_bp.route('/registrar_usuario', methods=['POST'])
def registrar_usuario():
    try:
        data = request.get_json()
        usuario = data.get('usuario')
        cedula = data.get('cedula')
        contrasena = data.get('contrasena')
        rol = data.get('rol')  # Asegurar que se envía el rol

        if not usuario or not cedula or not contrasena or not rol:
            return jsonify({'error': 'Faltan datos'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO usuario (usuario, cedula, contrasena, rol) VALUES (%s, %s, %s, %s)",
                       (usuario, cedula, contrasena, rol))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({'message': 'Usuario registrado exitosamente'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

#editar rol
@usuario_bp.route('/editar_rol', methods=['PUT'])
def editar_rol():
    data = request.get_json()
    usuario = data.get('usuario')
    nuevo_rol = data.get('nuevo_rol')

    if not usuario or not nuevo_rol:
        return jsonify({'error': 'Usuario y nuevo rol son obligatorios.'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Verificar si el usuario existe
        cursor.execute('SELECT usuario FROM usuario WHERE usuario = %s', (usuario,))
        if not cursor.fetchone():
            return jsonify({'error': 'Usuario no encontrado.'}), 404

        # Actualizar el rol del usuario
        cursor.execute('UPDATE usuario SET rol = %s WHERE usuario = %s', (nuevo_rol, usuario))
        conn.commit()

        return jsonify({'success': True, 'message': 'Rol actualizado correctamente.'}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()

#obtener usuarios
@usuario_bp.route('/obtener_todos_usuarios', methods=['GET'])
def obtener_todos_usuarios():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT u.usuario, u.rol, e.nombre
            FROM usuario u
            JOIN empleado e ON u.cedula = e.cedula
        """)
        usuarios = cursor.fetchall()

        resultado = []
        for usuario in usuarios:
            resultado.append({
                'usuario': usuario[0],
                'rol': usuario[1],
                'nombre_empleado': usuario[2]
            })

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()
