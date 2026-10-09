from flask import Blueprint, request, jsonify
from db import get_db_connection
import psycopg2.extras


proveedor_bp = Blueprint('proveedor_bp', __name__)

#crear proveedor
@proveedor_bp.route('/proveedor', methods=['POST'])
def create_proveedor():
    try:
        # Obtener los datos del request
        data = request.get_json()
        rut_ci = data['rut_ci']
        nombre = data['nombre']
        alias = data['alias']
        telefono = data['telefono']
        whatsapp = data['whatsapp']
        mail = data['mail']
        departamento_nombre = data['departamento']  # Recibe el nombre del departamento
        localidad_nombre = data['localidad']       # Recibe el nombre de la localidad
        direccion = data['direccion']
        rubro_nombre = data['rubro']               # Recibe el nombre del rubro
        comentarios = data['comentarios']
        calificacion = data['calificacion']

        # Conectar con el cursor de tipo diccionario
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)  # Configurar el cursor como diccionario

        # Obtener el ID del departamento a partir de su nombre
        cursor.execute('SELECT departamento_id FROM departamentos WHERE departamento_nombre = %s', (departamento_nombre,))
        departamento_row = cursor.fetchone()
        if not departamento_row:
            return jsonify({'error': f'El departamento "{departamento_nombre}" no existe'}), 400
        departamento_id = departamento_row['departamento_id']

        # Obtener el ID de la localidad a partir de su nombre
        cursor.execute('SELECT localidad_id FROM localidades WHERE localidad_nombre = %s', (localidad_nombre,))
        localidad_row = cursor.fetchone()
        if not localidad_row:
            return jsonify({'error': f'La localidad "{localidad_nombre}" no existe'}), 400
        localidad_id = localidad_row['localidad_id']

        # Obtener el ID del rubro a partir de su nombre
        cursor.execute('SELECT rubro_id FROM rubro WHERE rubro_nombre = %s', (rubro_nombre,))
        rubro_row = cursor.fetchone()
        if not rubro_row:
            return jsonify({'error': f'El rubro "{rubro_nombre}" no existe'}), 400
        rubro_id = rubro_row['rubro_id']

        # Insertar el nuevo proveedor con los IDs obtenidos
        query = '''
        INSERT INTO proveedor (
            rut_ci, nombre, alias, telefono, whatsapp, mail,
            departamento_id, localidad_id, direccion, rubro_id,
            calificacion, comentarios
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        cursor.execute(query, (
            rut_ci, nombre, alias, telefono, whatsapp, mail,
            departamento_id, localidad_id, direccion, rubro_id,
            calificacion, comentarios
        ))

        # Confirmar los cambios y cerrar la conexión
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'Proveedor creado exitosamente!'}), 201

    except Exception as e:
        print("Error en create_proveedor:", str(e))  # Agregar este print para ver el error en los logs
        return jsonify({'error': str(e)}), 500


#obtener listado proveedores
@proveedor_bp.route('/proveedores', methods=['GET'])
def get_proveedores():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(" SELECT nombre, rut_ci FROM proveedor WHERE estado='Activo'")
    proveedores = cursor.fetchall()
    conn.close()
    return jsonify(proveedores)

#obtener todo de proveedor
print(">>> Cargando función todo proveedor()")
@proveedor_bp.route('/get_proveedor', methods=['GET'])
def get_proveedor():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Hacemos un JOIN entre proveedor, localidad, departamento y rubro para obtener los nombres
    cursor.execute('''
        SELECT
            p.rut_ci,
            p.nombre,
            p.alias,
            p.telefono,
            p.whatsapp,
            p.mail,
            r.rubro_nombre AS rubro,
            p.direccion,
            l.localidad_nombre AS localidades,
            d.departamento_nombre AS departamentos,
            p.calificacion,
            p.comentarios,
            p.estado
        FROM proveedor p
        LEFT JOIN localidades l ON p.localidad_id = l.localidad_id
        LEFT JOIN departamentos d ON p.departamento_id = d.departamento_id
        LEFT JOIN rubro r ON p.rubro_id = r.rubro_id
    ''')

    rows = cursor.fetchall()
    conn.close()

    # Mapeo de columnas a un formato JSON amigable para el frontend
    proveedores = [
        {
            'rut_ci': row[0],
            'nombre': row[1],
            'alias': row[2],
            'telefono': row[3],
            'whatsapp': row[4],
            'mail': row[5],
            'rubro': row[6],
            'direccion': row[7],
            'localidad_nombre': row[8],
            'departamento_nombre': row[9],
            'calificacion': row[10],
            'comentarios': row[11],
            'estado': row[12],
        }
        for row in rows
    ]

    return jsonify(proveedores)

#editar proveedores
@proveedor_bp.route('/update_proveedor/<rut_ci>', methods=['PUT'])  # rut_ci como string
def update_proveedor(rut_ci):
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()

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

        # Obtener rubro_id a partir del nombre
        cur.execute("SELECT rubro_id FROM rubro WHERE rubro_nombre = %s", (data['rubro'],))
        rubro = cur.fetchone()
        if rubro is None:
            return jsonify({"error": "Rubro no encontrado"}), 400
        rubro_id = rubro[0]

        # Actualizar el proveedor
        cur.execute("""
            UPDATE proveedor SET
                nombre=%s, alias=%s, telefono=%s, whatsapp=%s, mail=%s, rubro_id=%s,
                direccion=%s, localidad_id=%s, departamento_id=%s, calificacion=%s,
                comentarios=%s, estado=%s
            WHERE rut_ci=%s
        """, (data['nombre'], data['alias'], data['telefono'], data['whatsapp'], data['mail'],
              rubro_id, data['direccion'], localidad_id, departamento_id,
              data['calificacion'], data['comentarios'], data['estado'], str(rut_ci)))  # Convertir rut_ci a string

        conn.commit()
        return jsonify({"mensaje": "Proveedor actualizado"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()

# Crear nuevo rubro
@proveedor_bp.route('/rubroscrear', methods=['POST'])
def crear_rubro():
    try:
        data = request.get_json()

        if not data or 'rubro_nombre' not in data:
            return jsonify({'mensaje': 'Nombre del rubro es requerido.'}), 400

        rubro_nombre = data['rubro_nombre']

        # Conectar a la base de datos
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar si el rubro ya existe
        cursor.execute("SELECT rubro_id FROM rubro WHERE rubro_nombre = %s", (rubro_nombre,))
        rubro_existente = cursor.fetchone()

        if rubro_existente:
            return jsonify({'mensaje': 'El rubro ya existe.'}), 400

        # Insertar nuevo rubro
        cursor.execute("INSERT INTO rubro (rubro_nombre) VALUES (%s) RETURNING rubro_id", (rubro_nombre,))
        nuevo_rubro_id = cursor.fetchone()[0]

        # Confirmar los cambios y cerrar la conexión
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'mensaje': 'Rubro creado exitosamente.', 'rubro_id': nuevo_rubro_id, 'rubro_nombre': rubro_nombre}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
#obtener rubros
@proveedor_bp.route('/rubros', methods=['GET'])
def obtener_rubros():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Conectar con el cursor de tipo diccionario
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)  # Configurar el cursor como diccionario

        cursor.execute('SELECT rubro_id, rubro_nombre FROM rubro')
        rubros = [{'id': row['rubro_id'], 'nombre': row['rubro_nombre']} for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return jsonify({'rubros': rubros}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
