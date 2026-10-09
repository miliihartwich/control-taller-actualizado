from flask import Blueprint, request, jsonify
from db import get_db_connection
import psycopg2.extras

empleado_bp = Blueprint('empleado_bp', __name__)

# Crear un nuevo empleado
@empleado_bp.route('/empleado', methods=['POST'])
def create_empleado():
    try:
        data = request.get_json()

        # Extraer datos del JSON
        cedula = data.get('cedula')
        nombre = data.get('nombre')
        celular = data.get('celular')
        factor = data.get('factor')
        direccion = data.get('direccion')
        remuneracion = data.get('remuneracion')
        fecha_vencimiento_carnet = data.get('fecha_vencimiento_carnet')

        # Validación simple (puedes agregar más según sea necesario)
        if not all([cedula, nombre, celular, factor, direccion, remuneracion, fecha_vencimiento_carnet]):
            return jsonify({'message': 'Todos los campos son obligatorios.'}), 400

        # Conectar con la base de datos
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Insertar los datos del empleado en la tabla
        cursor.execute(
            'INSERT INTO empleado (cedula, nombre, celular, factor, direccion, remuneracion, fecha_vencimiento_carnet) '            'VALUES (%s, %s, %s, %s, %s, %s, %s)',
            (cedula, nombre, celular, factor, direccion, remuneracion, fecha_vencimiento_carnet)
        )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'Empleado creado exitosamente!'}), 201

    except Exception as e:
        print(f"Error al crear el empleado: {str(e)}")
        return jsonify({'message': 'Error al crear el empleado.', 'error': str(e)}), 500
    
from flask import jsonify, current_app

@empleado_bp.route('/obtener_empleados', methods=['GET'])
def get_empleados_listado():
    try:
        conn = get_db_connection()            # <-- si falla, tirará excepción
        cursor = conn.cursor()
        cursor.execute("""
            SELECT cedula, nombre
            FROM empleado
            WHERE estado ILIKE 'activo'       -- tolerante a may/min
        """)
        empleados = cursor.fetchall()
        return jsonify([{'cedula': e[0], 'nombre': e[1]} for e in empleados]), 200
    except Exception as e:
        # vas a ver el stack en la consola del server
        current_app.logger.exception("Error en /obtener_empleados")
        # devolvé JSON para que el front lo muestre bien
        return jsonify({"error": "No se pudo obtener empleados"}), 500
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass

# Obtener todo de empleado
@empleado_bp.route('/get_empleado', methods=['GET'])
def get_empleados():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT cedula, nombre, direccion, celular, remuneracion, factor, fecha_vencimiento_carnet, estado
        FROM empleado
    ''')
    rows = cursor.fetchall()
    conn.close()

    empleados = []
    for row in rows:
        empleados.append({
            'cedula': row[0],
            'nombre': row[1],
            'direccion': row[2],
            'celular': row[3],
            'remuneracion': row[4],
            'factor': row[5],
            'fecha_vencimiento_carnet': row[6],
            'estado': row[7],
        })

    return jsonify(empleados)

# Editar empleados
@empleado_bp.route('/update_empleado/<cedula>', methods=['PUT'])
def update_empleado(cedula):
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            UPDATE empleado SET
                nombre=%s, direccion=%s, celular=%s, remuneracion=%s, factor=%s,
                fecha_vencimiento_carnet=%s, estado=%s
            WHERE cedula=%s
        """, (
            data['nombre'], data['direccion'], data['celular'], data['remuneracion'], data['factor'],
            data['fecha_vencimiento_carnet'], data['estado'], cedula))

        conn.commit()
        return jsonify({"mensaje": "Empleado actualizado"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()
