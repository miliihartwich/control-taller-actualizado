from flask import Blueprint, request, jsonify
from db import get_db_connection


servicios_bp = Blueprint('servicios_bp', __name__)

#registrar servicio
@servicios_bp.route('/registrar_servicio', methods=['POST'])
def registrar_servicio():
    try:
        data = request.get_json()

        # Obtener datos del request
        proveedor_rut_ci = data.get('proveedor_rut_ci')
        numero_factura = data.get('numero_factura')
        fecha = data.get('fecha')
        moneda = data.get('moneda')
        importe = data.get('importe')
        tipo_iva = data.get('tipo_iva')
        tipo_cambio = data.get('tipo_cambio', 1)  # Valor por defecto 1
        importe_pesos = data.get('importe_pesos', importe)  # Si no envían, se usa importe
        descripcion = data.get('descripcion_servicio')
        division_nombre = data.get('division')
        tipo_nombre = data.get('tipo')
        descripcion_nombre = data.get('descripcion')

        # Validar que los campos obligatorios estén presentes
        required_fields = ['proveedor_rut_ci', 'numero_factura', 'fecha', 'moneda', 'importe', 'tipo_iva', 'descripcion']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"El campo {field} es obligatorio"}), 400

        # Conectar a la base de datos
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM division_opciones WHERE nombre = %s', (division_nombre,))
        result = cursor.fetchone()
        if not result:
            return jsonify({'error': f'División "{division_nombre}" no encontrada.'}), 400
        id_division = result[0]

        cursor.execute('SELECT id FROM tipo_opciones WHERE nombre = %s', (tipo_nombre,))
        result = cursor.fetchone()
        if not result:
            return jsonify({'error': f'Tipo "{tipo_nombre}" no encontrado.'}), 400
        id_tipo = result[0]

        cursor.execute('''
            SELECT id_descripcion
            FROM descripcion_opciones
            WHERE nombre_descripcion = %s AND id_tipo = %s
        ''', (descripcion_nombre, id_tipo))
        result = cursor.fetchone()
        if not result:
            return jsonify({'error': f'Descripción "{descripcion_nombre}" no encontrada para el tipo seleccionado.'}), 400
        id_descripcion = result[0]

        # Obtener ID de orden
        cursor.execute('''
            SELECT numero_orden
            FROM ordenes
            WHERE division_id = %s AND tipo_id = %s AND descripcion_id = %s
        ''', (id_division, id_tipo, id_descripcion))
        result = cursor.fetchone()

        if not result:
            return jsonify({'error': 'No se encontró un número de orden para la intervención.'}), 400

        numero_orden = result[0]

        # Insertar en la base de datos
        cursor.execute("""
            INSERT INTO servicios (rut_ci_proveedor, numero_factura, fecha, moneda, importe, tipo_iva, tipo_cambio, importe_pesos, descripcion, numero_orden)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (proveedor_rut_ci, numero_factura, fecha, moneda, importe, tipo_iva, tipo_cambio, importe_pesos, descripcion, numero_orden))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Servicio registrado exitosamente"}), 201

    except Exception as e:
        servicios_bp.logger.error(f"Error al registrar servicio: {e}")
        return jsonify({"error": str(e)}), 500
    
#obtener listado de servicios    
@servicios_bp.route('/get_servicios', methods=['GET'])
def get_servicios():
    try:
        # Conectar a la base de datos
        conn = get_db_connection()
        cursor = conn.cursor()

        # Ejecutar la consulta para obtener los datos
        cursor.execute("""
            SELECT numero_factura, rut_ci_proveedor, fecha, moneda, importe,
                   tipo_iva, tipo_cambio, importe_pesos, descripcion, numero_orden
            FROM servicios;
        """)

        # Obtener todos los registros de la consulta
        rows = cursor.fetchall()

        # Crear una lista de diccionarios con los resultados
        servicios_data = []
        for row in rows:
            servicios_data.append({
                "numero_factura": row[0],
                "rut_ci_proveedor": row[1],
                "fecha": row[2].isoformat() if row[2] else None,  # Asegura formato fecha
                "moneda": row[3],
                "importe": row[4],
                "tipo_iva": row[5],
                "tipo_cambio": row[6],
                "importe_pesos": row[7],
                "descripcion": row[8],
                "numero_orden": row[9]
            })

        # Cerrar la conexión
        cursor.close()
        conn.close()

        # Retornar los resultados como JSON
        return jsonify(servicios_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
