from flask import Blueprint, request, jsonify
from db import get_db_connection
import psycopg2.extras
import logging

clasificacion_ordenes_bp = Blueprint('clasificacion_ordenes_bp', __name__)

#obtener listado de divisiones
@clasificacion_ordenes_bp.route('/divisiones', methods=['GET'])
def get_divisiones():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Obtener todos los nombres de la tabla division
    cursor.execute('SELECT nombre FROM division_opciones')
    divisiones = cursor.fetchall()

    conn.close()
    return jsonify([div[0] for div in divisiones])

#tipo segun la division seleccionada
@clasificacion_ordenes_bp.route('/tipos_por_division/<string:nombre_division>', methods=['GET'])
def get_tipos_por_division(nombre_division):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Buscar el ID de la división a partir del nombre
    cursor.execute('SELECT id FROM division_opciones WHERE nombre = %s', (nombre_division,))
    division = cursor.fetchone()

    if not division:
        return jsonify({"error": "División no encontrada"}), 404

    # Obtener los tipos basados en el ID de la división encontrada
    cursor.execute('SELECT nombre FROM tipo_opciones WHERE id_division = %s', (division[0],))
    tipos = cursor.fetchall()

    conn.close()
    return jsonify([tipo[0] for tipo in tipos])


#descripcion segun el tipo seleccionado
@clasificacion_ordenes_bp.route('/descripcion_por_tipo/<string:nombre_tipo>', methods=['GET'])
def get_descripcion_por_tipo(nombre_tipo):
        conn = get_db_connection()
        cursor = conn.cursor()

        # Buscar el ID del tipo a partir del nombre
        cursor.execute('SELECT id FROM tipo_opciones WHERE nombre = %s', (nombre_tipo,))
        tipo = cursor.fetchone()

        if not tipo:
            return jsonify({"error": "Tipo no encontrado"}), 404

        # Obtener las descripciones basadas en el ID del tipo encontrado
        cursor.execute('SELECT nombre_descripcion FROM descripcion_opciones WHERE id_tipo = %s', (tipo[0],))
        descripciones = cursor.fetchall()

        conn.close()
        return jsonify([descripcion[0] for descripcion in descripciones])

#agregar nueva division
@clasificacion_ordenes_bp.route('/agregar_division', methods=['POST'])
def agregar_division():
    data = request.get_json()
    if not data or 'nombre' not in data:
        return jsonify({'error': 'Falta el campo nombre'}), 400

    nombre = data['nombre'].strip()
    if not nombre:
        return jsonify({'error': 'El nombre no puede estar vacío'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("SELECT id FROM division_opciones WHERE nombre = %s", (nombre,))
            if cursor.fetchone():
                return jsonify({'error': 'La división ya existe'}), 409

            cursor.execute("INSERT INTO division_opciones (nombre) VALUES (%s) RETURNING id", (nombre,))
            new_id = cursor.fetchone()[0]
            conn.commit()

        return jsonify({'message': 'División agregada exitosamente', 'id': new_id}), 201
    except Exception as e:
        conn.rollback()
        print("Error al agregar división:", e)
        return jsonify({'error': 'Error interno del servidor'}), 500
    finally:
        conn.close()

#agregar nuevo tipo
# Configuración del logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
@clasificacion_ordenes_bp.route('/agregar_tipo', methods=['POST'])
def agregar_tipo():
    data = request.get_json()  # Obtener los datos enviados por el cliente (nombre del tipo y nombre de la división)

    nombre_tipo = data.get('nombre')  # Nombre del nuevo tipo
    nombre_division = data.get('division')  # Nombre de la división asociada

    if not nombre_tipo or not nombre_division:
        logger.error('Faltan parámetros: nombre del tipo o división')
        return jsonify({'error': 'Faltan parámetros, asegúrese de enviar el nombre del tipo y la división'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Log de los datos recibidos
        logger.info(f"Recibiendo solicitud para agregar tipo: {nombre_tipo} a la división: {nombre_division}")
        logger.info(f"Valor de nombre_division: '{nombre_division}'")

        # Obtener el id de la división a partir de su nombre
        cursor.execute("SELECT id FROM division_opciones WHERE nombre = %s", (nombre_division,))
        division_id = cursor.fetchone()

        # Log de la consulta de la división
        logger.info(f"División encontrada: {division_id}")

        if not division_id:
            logger.warning(f"La división '{nombre_division}' no existe en la base de datos.")
            return jsonify({'error': 'La división no existe'}), 404

        # Insertar el nuevo tipo en la tabla tipo_opciones
        cursor.execute('INSERT INTO tipo_opciones (nombre, id_division) VALUES (%s, %s)',
                       (nombre_tipo, division_id[0]))
        conn.commit()
        conn.close()

        logger.info(f"Nuevo tipo '{nombre_tipo}' agregado exitosamente a la división '{nombre_division}'")
        return jsonify({'mensaje': 'Tipo guardado exitosamente'}), 200

    except Exception as e:
        conn.rollback()  # En caso de error, revertir la transacción
        conn.close()
        logger.error(f"Error al guardar el tipo: {e}")
        return jsonify({'error': str(e)}), 500

@clasificacion_ordenes_bp.route('/divisiones_id', methods=['GET'])
def get_divisiones_id():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute('SELECT id, nombre FROM division_opciones ORDER BY nombre')
    rows = cursor.fetchall()

    conn.close()
    return jsonify([{"id": r["id"], "nombre": r["nombre"]} for r in rows]), 200

@clasificacion_ordenes_bp.route('/tipos_por_division_id/<int:division_id>', methods=['GET'])
def get_tipos_por_division_id(division_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute('SELECT id, nombre FROM tipo_opciones WHERE id_division = %s ORDER BY nombre', (division_id,))
    rows = cursor.fetchall()

    conn.close()
    return jsonify([{"id": r["id"], "nombre": r["nombre"]} for r in rows]), 200

@clasificacion_ordenes_bp.route('/descripcion_por_tipo_id/<int:tipo_id>', methods=['GET'])
def get_descripcion_por_tipo_id(tipo_id):
    division_id = request.args.get('division_id')

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    try:
        if division_id:
            cursor.execute('''
                SELECT
                    d.id_descripcion,
                    d.nombre_descripcion
                FROM descripcion_opciones d
                JOIN tipo_opciones t ON d.id_tipo = t.id
                WHERE d.id_tipo = %s
                AND t.id_division = %s
                ORDER BY d.nombre_descripcion
            ''', (tipo_id, division_id))
        else:
            cursor.execute('''
                SELECT
                    id_descripcion,
                    nombre_descripcion
                FROM descripcion_opciones
                WHERE id_tipo = %s
                ORDER BY nombre_descripcion
            ''', (tipo_id,))

        rows = cursor.fetchall()

        return jsonify([
            {
                "id_descripcion": r["id_descripcion"],
                "nombre_descripcion": r["nombre_descripcion"]
            }
            for r in rows
        ]), 200

    finally:
        cursor.close()
        conn.close()
