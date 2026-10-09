from flask import Blueprint, request, jsonify
from db import get_db_connection
import psycopg2.extras


ubicaciones_bp = Blueprint('ubicaciones_bp', __name__)

#listado localidades
@ubicaciones_bp.route('/localidades', methods=['GET'])
def obtener_localidades():
    departamento_nombre = request.args.get('departamento')
    if not departamento_nombre:
        return jsonify({'error': 'El nombre del departamento es requerido.'}), 400


        # Conectar con el cursor de tipo diccionario
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)  # Configurar el cursor como diccionario

    cursor.execute('SELECT l.localidad_nombre FROM localidades l JOIN departamentos d ON l.departamento_id = d.departamento_id WHERE d.departamento_nombre = %s', (departamento_nombre,))
    localidades = [row['localidad_nombre'] for row in cursor.fetchall()]
    cursor.close()
    conn.close()

    return jsonify({'localidades': localidades})

#listado departamentos
@ubicaciones_bp.route('/departamentos', methods=['GET'])
def obtener_departamentos():
    try:
        # Conexión a la base de datos
        conn = get_db_connection()
        cursor = conn.cursor()
        # Conectar con el cursor de tipo diccionario
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)  # Configurar el cursor como diccionario

        # Consulta para obtener los nombres de los departamentos
        cursor.execute('SELECT departamento_nombre FROM departamentos')
        departamentos = [row['departamento_nombre'] for row in cursor.fetchall()]

        cursor.close()
        conn.close()

        return jsonify({'departamentos': departamentos}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500