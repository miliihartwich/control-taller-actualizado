from flask import Blueprint, request, jsonify
from db import get_db_connection

compras_bp = Blueprint('compras_bp', __name__)

#crear compra
@compras_bp.route('/compras', methods=['POST'])
def create_compra():
    data = request.get_json()
    proveedor_rut_ci = data['proveedor_rut_ci']
    numero_factura = data['numero_factura']
    fecha = data['fecha']
    moneda = data['moneda']
    importe = data['importe']
    tipo_iva = data['tipo_iva']
    tipo_cambio = data['tipo_cambio']
    importe_pesos = data['importe_pesos']

    bienes = data.get('bienes', [])  # Lista de bienes a insertar

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Verificar si el proveedor existe en la base de datos
        cursor.execute("SELECT COUNT(*) FROM proveedor WHERE rut_ci = %s", (proveedor_rut_ci,))
        proveedor_existe = cursor.fetchone()[0]

        if not proveedor_existe:
            return jsonify({'error': 'El proveedor ingresado no existe en la base de datos'}), 400

        # Iniciar transacción
        cursor.execute("BEGIN;")

        # Insertar la compra
        cursor.execute(
            '''INSERT INTO compras
            (proveedor_rut_ci, numero_factura, fecha, moneda, importe, tipo_iva, tipo_cambio, importe_pesos)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
            (proveedor_rut_ci, numero_factura, fecha, moneda, importe, tipo_iva, tipo_cambio, importe_pesos)
        )

        # Insertar cada bien asociado a la compra y actualizar stock
        for bien in bienes:
            nombre_bien = bien['nombre']
            costo_unitario = bien['costo_unitario']
            cantidad = bien['cantidad']
            unidad = bien['unidad']  # Se usa solo si es nuevo
            moneda = bien['moneda']

            # Insertar en detalle_compras
            cursor.execute(
                '''INSERT INTO detalle_compras (nombre_bien, costo_unitario, cantidad, moneda, numero_factura)
                VALUES (%s, %s, %s, %s, %s)''',
                (nombre_bien, costo_unitario, cantidad, moneda, numero_factura)
            )

            # Verificar si el bien ya existe en stock
            cursor.execute("SELECT costo_unitario, unidades_disponibles, unidad FROM stock WHERE nombre_bien = %s", (nombre_bien,))
            stock_item = cursor.fetchone()

             # Asegurarse de que la cantidad se trata como float, y reemplazar comas por puntos
            cantidad_float = float(str(cantidad).replace(',', '.'))

            if stock_item:
                # Extraer valores de la BD
                unidades_actuales = stock_item[1]  # Suponiendo que stock_item es un tuple y la cantidad de unidades está en el índice 1

                               # Sumar cantidad ingresada
                unidades_actualizadas = unidades_actuales + cantidad_float

                # Reemplazar el costo unitario por el nuevo
                cursor.execute(
                    '''UPDATE stock
                    SET costo_unitario = %s, unidades_disponibles = %s, moneda = %s
                    WHERE nombre_bien = %s''',
                    (costo_unitario, unidades_actualizadas, moneda, nombre_bien)
                )
            else:
                # Si el bien no existe, insertarlo en la tabla
                cursor.execute(
                    '''INSERT INTO stock (nombre_bien, costo_unitario, unidades_disponibles, unidad, moneda)
                    VALUES (%s, %s, %s, %s, %s)''',
                    (nombre_bien, costo_unitario, cantidad_float, unidad, moneda)
                )


        # Confirmar la transacción
        conn.commit()
        return jsonify({'message': 'Compra y bienes ingresados exitosamente!'}), 201

    except Exception as e:
        conn.rollback()  # Revertir si hay error
        return jsonify({'error': str(e)}), 500

    finally:
        conn.close()


#obtener nombre de bienes
@compras_bp.route('/bienes-nombres', methods=['GET'])
def obtener_nombres_materiales():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT nombre_bien, unidad FROM stock')
    bienes = cursor.fetchall()

    conn.close()

    # Devolver una lista de diccionarios con nombre y unidad
    return jsonify([{"nombre": bien[0], "unidad": bien[1]} for bien in bienes]), 200

#obtener listado stock
@compras_bp.route('/get_stock', methods=['GET'])
def get_stock():
    try:
        # Conectar a la base de datos
        conn = get_db_connection()
        cursor = conn.cursor()

        # Ejecutar la consulta para obtener los datos
        cursor.execute("""
            SELECT nombre_bien, costo_unitario, unidades_disponibles, unidad, moneda
            FROM stock;
        """)

        # Obtener todos los registros de la consulta
        rows = cursor.fetchall()

        # Crear una lista de diccionarios con los resultados
        stock_data = []
        for row in rows:
            stock_data.append({
                "nombre_bien": row[0],
                "costo_unitario": row[1],
                "unidades_disponibles": row[2],
                "unidad": row[3],
                "moneda": row[4]
            })

        # Cerrar la conexión
        cursor.close()
        conn.close()

        # Retornar los resultados como JSON
        return jsonify(stock_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
