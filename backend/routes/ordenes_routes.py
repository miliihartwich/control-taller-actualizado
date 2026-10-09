from flask import Blueprint, request, jsonify
from db import get_db_connection
import psycopg2.extras


ordenes_bp = Blueprint('ordenes_bp', __name__)

#crear orden
@ordenes_bp.route('/ordenes', methods=['POST'])
def create_orden():
    try:
        data = request.get_json()
        print("Datos recibidos en /ordenes:", data)  # Depuración

        nombre_division = data["division"]  # Nombre de la división
        nombre_tipo = data["tipo"]  # Nombre del tipo
        cliente_rut = data["cliente"]  # Cliente (rut_ci)
        descripcion_nombre = data["descripcion"]
        fecha_inicio = data["fecha_inicio"]
        fecha_fin = data.get("fecha_fin")  # Obtener fecha_fin (puede no estar)

        # Si fecha_fin es una cadena vacía, asignar None para que sea NULL en la BD
        if fecha_fin == "":
            fecha_fin = None

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # 🔍 Buscar el ID de la división
        cursor.execute("SELECT id FROM division_opciones WHERE nombre = %s", (nombre_division,))
        division_row = cursor.fetchone()

        if division_row is None:
            conn.close()
            return jsonify({"error": f"División no encontrada: {nombre_division}"}), 404

        id_division = division_row["id"]

        # 🔍 Buscar el ID del tipo basado en el nombre Y la división
        cursor.execute(
            """
            SELECT id 
            FROM tipo_opciones 
            WHERE nombre = %s 
            AND id_division = %s
            """,
            (nombre_tipo, id_division)
        )
        tipo_row = cursor.fetchone()

        if tipo_row is None:
            conn.close()
            return jsonify({
                "error": f"Tipo no encontrado: {nombre_tipo} para la división {nombre_division}"
            }), 404

        id_tipo = tipo_row["id"]
        # 🔍 Verificar si la descripción ya existe
        cursor.execute(
            "SELECT id_descripcion FROM descripcion_opciones WHERE nombre_descripcion = %s AND id_tipo = %s",
            (descripcion_nombre, id_tipo),
        )
        descripcion = cursor.fetchone()

        if descripcion is None:
            cursor.execute(
                "INSERT INTO descripcion_opciones (nombre_descripcion, id_tipo) VALUES (%s, %s) RETURNING id_descripcion",
                (descripcion_nombre, id_tipo),
            )
            descripcion_id = cursor.fetchone()["id_descripcion"]
        else:
            descripcion_id = list(descripcion.values())[0]

        # 🔍 Obtener el ID del cliente (rut_ci)
        cursor.execute("SELECT rut_ci FROM cliente WHERE rut_ci = %s", (cliente_rut,))
        cliente_row = cursor.fetchone()

        if cliente_row is None:
            conn.close()
            return jsonify({"error": f"Cliente no encontrado: {cliente_rut}"}), 404

        rut_ci = cliente_row["rut_ci"]

        # ✅ Insertar la orden con los IDs
        cursor.execute(
    "INSERT INTO ordenes (division_id, tipo_id, descripcion_id, rut_ci, fecha_inicio, fecha_fin) VALUES (%s, %s, %s, %s, %s, %s)",
    (id_division, id_tipo, descripcion_id, rut_ci, fecha_inicio, fecha_fin if fecha_fin else None),
)

        conn.commit()
        conn.close()

        return jsonify({"message": "Orden creada exitosamente!"}), 201

    except Exception as e:
        print("Error en /ordenes:", str(e))  # Mostrar el error exacto en la terminal
        return jsonify({"error": "Error interno del servidor"}), 500

@ordenes_bp.route('/ordenes_listado', methods=['GET'])
def get_ordenes():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("""
    SELECT
        o.numero_orden,
        d.nombre AS division,
        t.nombre AS tipo,
        desc_opc.nombre_descripcion AS descripcion,
        c.rut_ci AS rut_ci,
        c.nombre AS cliente,
        o.fecha_inicio,
        o.fecha_fin,
        o.estado
    FROM ordenes o
    JOIN division_opciones d ON o.division_id = d.id
    JOIN tipo_opciones t ON o.tipo_id = t.id
    JOIN descripcion_opciones desc_opc ON o.descripcion_id = desc_opc.id_descripcion
    JOIN cliente c ON o.rut_ci = c.rut_ci
    ORDER BY o.fecha_inicio DESC;
""")


        ordenes = cursor.fetchall()
        conn.close()

        return jsonify(ordenes), 200

    except Exception as e:
        print("Error en /ordenes_listado:", str(e))
        return jsonify({"error": "Error interno del servidor"}), 500


#obtener todo de ordenes
@ordenes_bp.route('/get_orden', methods=['GET'])
def get_orden():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ordenes')
    rows = cursor.fetchall()
    conn.close()
    return jsonify(rows)

#modificar orden
@ordenes_bp.route('/update_orden/<int:numero_orden>', methods=['PUT'])
def update_orden(numero_orden):
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Obtener division_id a partir del nombre
        cur.execute("SELECT division_id FROM division_opciones WHERE division_nombre = %s", (data['division'],))
        division = cur.fetchone()
        if division is None:
            return jsonify({"error": "División no encontrada"}), 400
        division_id = division[0]

        # Obtener tipo_id a partir del nombre
        cur.execute("SELECT tipo_id FROM tipo_opcion WHERE tipo_nombre = %s", (data['tipo'],))
        tipo = cur.fetchone()
        if tipo is None:
            return jsonify({"error": "Tipo no encontrado"}), 400
        tipo_id = tipo[0]

        # Obtener descripcion_id a partir del nombre
        cur.execute("SELECT descripcion_id FROM descripcion_opciones WHERE descripcion_nombre = %s", (data['descripcion'],))
        descripcion = cur.fetchone()
        if descripcion is None:
            return jsonify({"error": "Descripción no encontrada"}), 400
        descripcion_id = descripcion[0]

        # Validar que el estado sea uno de los permitidos
        estados_permitidos = ["Activa", "En pausa", "Finalizada"]
        if data['estado'] not in estados_permitidos:
            return jsonify({"error": "Estado no válido"}), 400

        # Actualizar la orden
        cur.execute("""
            UPDATE ordenes SET
                division_id=%s, tipo_id=%s, descripcion_id=%s, cliente=%s,
                fecha_inicio=%s, fecha_fin=%s, estado=%s
            WHERE numero_orden=%s
        """, (division_id, tipo_id, descripcion_id, data['cliente'],
              data['fecha_inicio'], data['fecha_fin'], data['estado'], numero_orden))

        conn.commit()
        return jsonify({"mensaje": "Orden actualizada correctamente"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()

#obtener detalle de orden
@ordenes_bp.route('/ordenes/detalle', methods=['GET'])
def obtener_detalle_orden():
    division_nombre = request.args.get('division')
    tipo_nombre = request.args.get('tipo')
    descripcion_nombre = request.args.get('descripcion')

    if not all([division_nombre, tipo_nombre, descripcion_nombre]):
        return jsonify({"error": "division, tipo y descripcion son obligatorios"}), 400

    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            # Obtener los IDs
            cursor.execute("SELECT id FROM division_opciones WHERE nombre = %s", (division_nombre,))
            division_row = cursor.fetchone()
            if not division_row:
                return jsonify({"error": f'La división "{division_nombre}" no existe'}), 404
            division_id = division_row[0]

            cursor.execute("SELECT id FROM tipo_opciones WHERE nombre = %s", (tipo_nombre,))
            tipo_row = cursor.fetchone()
            if not tipo_row:
                return jsonify({"error": f'El tipo "{tipo_nombre}" no existe'}), 404
            tipo_id = tipo_row[0]

            cursor.execute("SELECT id_descripcion FROM descripcion_opciones WHERE nombre_descripcion = %s", (descripcion_nombre,))
            descripcion_row = cursor.fetchone()
            if not descripcion_row:
                return jsonify({"error": f'La descripción "{descripcion_nombre}" no existe'}), 404
            descripcion_id = descripcion_row[0]

            # Consultar la orden
            cursor.execute("""
                SELECT numero_orden, rut_ci, fecha_inicio, fecha_fin
                FROM ordenes
                WHERE division_id = %s AND tipo_id = %s AND descripcion_id = %s
            """, (division_id, tipo_id, descripcion_id))
            orden = cursor.fetchone()

            if not orden:
                return jsonify({"error": "No se encontró la orden especificada"}), 404

            numero_orden, rut_ci, fecha_inicio, fecha_fin = orden

            # Obtener el nombre del cliente
            cursor.execute("SELECT nombre FROM cliente WHERE rut_ci = %s", (rut_ci,))
            cliente_row = cursor.fetchone()
            if not cliente_row:
                return jsonify({"error": f'No se encontró el cliente con rut_ci {rut_ci}'}), 404
            cliente_nombre = cliente_row["nombre"]

            # Obtener información de compras
            cursor.execute("""
                SELECT m.nombre_material, p.nombre AS proveedor, c.numero_factura, m.precio AS importe
                FROM materiales m
                JOIN compras c ON m.nro_factura = c.numero_factura
                JOIN proveedor p ON c.proveedor_rut_ci = p.rut_ci
                WHERE m.id_orden = %s
            """, (numero_orden,))
            compras = cursor.fetchall()

            compras_detalle = [
                {
                    "material": compra["nombre_material"],
                    "proveedor": compra["proveedor"],
                    "numero_factura": compra["numero_factura"],
                    "importe": "{:.2f}".format(compra["importe"])
                }
                for compra in compras
            ]

            # Calcular el importe total de las compras
            total_compras = sum(compra["importe"] for compra in compras)
            total_compras = "{:.2f}".format(total_compras)

            # Obtener configuraciones
            cursor.execute("SELECT clave, valor FROM configuraciones")
            configuraciones = {row["clave"]: float(row["valor"]) for row in cursor.fetchall()}

            factor_fijo = configuraciones.get('factor_fijo', 0)
            costo_fijo_por_hora = configuraciones.get('costo_fijo_por_hora', 0)

            # Consultar empleados y horas trabajadas
            cursor.execute("""
                SELECT e.nombre, ht.total_horas_trabajadas,
                       (ht.total_horas_trabajadas * (e.remuneracion * %s + %s)) AS costo_total
                FROM empleado e
                JOIN horas_trabajadas ht ON e.cedula = ht.empleado_cedula
                WHERE ht.numero_orden = %s
            """, (factor_fijo, costo_fijo_por_hora, numero_orden))
            empleados = cursor.fetchall()

            total_horas = sum(emp["total_horas_trabajadas"] for emp in empleados)
            horas = int(total_horas)  # Parte entera son las horas
            minutos = int((total_horas - horas) * 60)  # Parte decimal convertida a minutos
            total_horas_formateado = f"{horas:02d}:{minutos:02d}"

            costo_total_mano_obra = sum(emp["costo_total"] for emp in empleados)
            costo_total_mano_obra = "{:.2f}".format(costo_total_mano_obra)

            empleados_detalle = [
                {
                    "nombre": emp["nombre"],
                    "total_horas_trabajadas": f"{int(emp['total_horas_trabajadas']):02d}:{int((emp['total_horas_trabajadas'] - int(emp['total_horas_trabajadas'])) * 60):02d}",
                    "costo_total": "{:.2f}".format(emp["costo_total"])
                }
                for emp in empleados
            ]

            # Calcular el costo total (compras + mano de obra)
            costo_total_orden = float(total_compras) + float(costo_total_mano_obra)
            costo_total_orden = "{:.2f}".format(costo_total_orden)

            # Recolectar la respuesta con todos los detalles
            respuesta = {
                "numero_orden": numero_orden,
                "cliente_nombre": cliente_nombre,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "costo_total_orden": costo_total_orden,
                "mano de obra": empleados_detalle,
                "total_horas": total_horas_formateado,
                "costo_total_mano_obra": costo_total_mano_obra,
                "compras": compras_detalle,
                "total_compras": total_compras,
                "configuraciones": configuraciones
            }

        return jsonify(respuesta), 200

    except Exception as e:
        return jsonify({"error": f"Ocurrió un error inesperado: {str(e)}"}), 500

    finally:
        conn.close()