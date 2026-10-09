from flask import Blueprint, request, jsonify
from db import get_db_connection
import psycopg2.extras

cliente_bp = Blueprint('cliente_bp', __name__)

#editar clientes
@cliente_bp.route('/update_cliente/<string:rut_ci>', methods=['PUT'])
def update_cliente(rut_ci):
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    print("RUT recibido en la URL:", rut_ci)
    print("Datos recibidos:", data)

    # Verifica que los datos requeridos estén presentes
    campos_validos = ["nombre", "alias", "telefono", "whatsapp", "mail", "direccion", "departamento_nombre", "localidad_nombre", "estado"]
    valores = {campo: data.get(campo) for campo in campos_validos}

    if None in valores.values():
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    try:
        # Obtener localidad_id a partir del nombre
        cur.execute("SELECT localidad_id FROM localidades WHERE localidad_nombre = %s", (data['localidad_nombre'],))
        localidad = cur.fetchone()
        if localidad is None:
            return jsonify({"error": "Localidad no encontrada"}), 400
        localidad_id = localidad[0]

        # Obtener departamento_id a partir del nombre
        cur.execute("SELECT departamento_id FROM departamentos WHERE departamento_nombre = %s", (data['departamento_nombre'],))
        departamento = cur.fetchone()
        if departamento is None:
            return jsonify({"error": "Departamento no encontrado"}), 400
        departamento_id = departamento[0]

        # Asegurar que el estado solo sea "Activo" o "Inactivo"
        if valores["estado"] not in ["Activo", "Inactivo"]:
            return jsonify({"error": "Valor de estado no válido"}), 400

        # Consulta UPDATE
        cur.execute("""
            UPDATE cliente
            SET nombre = %s, alias = %s, telefono = %s, whatsapp = %s, mail = %s,
                direccion = %s, departamento_id = %s, localidad_id = %s, estado = %s
            WHERE rut_ci = %s
        """, (valores["nombre"], valores["alias"], valores["telefono"], valores["whatsapp"], valores["mail"],
              valores["direccion"], departamento_id, localidad_id, valores["estado"], rut_ci))

        # Verificar si realmente se actualizó
        if cur.rowcount == 0:
            return jsonify({"error": "Cliente no encontrado"}), 404

        conn.commit()
        print("Commit realizado exitosamente")
        return jsonify({"mensaje": "Cliente actualizado correctamente"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()



#listado clientes
@cliente_bp.route('/get_cliente', methods=['GET'])
def get_cliente():
    try:
        print(">>> Iniciando get_cliente()")  # Verifica que la función se ejecuta

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                c.rut_ci,
                c.nombre,
                c.alias,
                c.telefono,
                c.whatsapp,
                c.mail,
                c.direccion,
                l.localidad_nombre,
                d.departamento_nombre,
                c.estado
            FROM cliente c
            LEFT JOIN localidades l ON c.localidad_id = l.localidad_id
            LEFT JOIN departamentos d ON c.departamento_id = d.departamento_id
        ''')

        rows = cursor.fetchall()
        print(">>> Filas obtenidas:", rows)  # Muestra los datos obtenidos

        conn.close()

        clientes = [
            {
                'rut_ci': row[0],
                'nombre': row[1],
                'alias': row[2],
                'telefono': row[3],
                'whatsapp': row[4],
                'mail': row[5],
                'direccion': row[6],
                'localidad_nombre': row[7],
                'departamento_nombre': row[8],
                'estado': row[9],
            }
            for row in rows
        ]

        return jsonify(clientes)

    except Exception as e:
        print(">>> Error en get_cliente:", e)  #  Ver el error en la consola
        return jsonify({"error": "Error interno del servidor"}), 500
    
# Crear un nuevo cliente
@cliente_bp.route('/cliente', methods=['POST'])
def create_cliente():
    data = request.get_json()

    # Validar que todos los campos necesarios están presentes
    required_fields = ['rut_ci', 'nombre', 'alias', 'telefono', 'whatsapp', 'mail', 'departamento', 'localidad', 'direccion']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'El campo "{field}" es obligatorio.'}), 400

    # Datos del cliente desde el frontend
    rut_ci = data['rut_ci']
    nombre = data['nombre']
    alias = data['alias']
    telefono = data['telefono']
    whatsapp = data['whatsapp']
    mail = data['mail']
    departamento_nombre = data['departamento']
    localidad_nombre = data['localidad']
    direccion = data['direccion']

    # Conexión a la base de datos
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        # Obtener el ID del departamento
        cursor.execute('SELECT departamento_id FROM departamentos WHERE departamento_nombre = %s', (departamento_nombre,))
        departamento = cursor.fetchone()

        if not departamento:
            return jsonify({'error': f'El departamento "{departamento_nombre}" no existe.'}), 400

        departamento_id = departamento['departamento_id']

        # Obtener el ID de la localidad correspondiente al departamento
        cursor.execute('SELECT localidad_id FROM localidades WHERE localidad_nombre = %s AND departamento_id = %s',
                       (localidad_nombre, departamento_id))
        localidad = cursor.fetchone()

        if not localidad:
            return jsonify({'error': f'La localidad "{localidad_nombre}" no pertenece al departamento "{departamento_nombre}".'}), 400

        localidad_id = localidad['localidad_id']

        # Insertar el cliente en la base de datos
        cursor.execute(
            'INSERT INTO cliente (rut_ci, nombre, alias, telefono, whatsapp, mail, departamento_id, localidad_id, direccion) '
            'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
            (rut_ci, nombre, alias, telefono, whatsapp, mail, departamento_id, localidad_id, direccion)
        )
        conn.commit()

        return jsonify({'message': 'Cliente creado exitosamente!'}), 201

    except psycopg2.Error as db_error:
        conn.rollback()
        return jsonify({'error': 'Error en la base de datos', 'details': str(db_error)}), 500

    except Exception as e:
        conn.rollback()
        return jsonify({'error': 'Error inesperado', 'details': str(e)}), 500

    finally:
        cursor.close()
        conn.close()

#listado clientes
@cliente_bp.route('/clientes', methods=['GET'])
def get_clientes():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute("SELECT rut_ci, nombre FROM cliente WHERE estado='Activo'")
    clientes = cursor.fetchall()

    conn.close()
    return jsonify(clientes)  # Devuelve una lista de objetos con 'rut_ci' y 'nombre'