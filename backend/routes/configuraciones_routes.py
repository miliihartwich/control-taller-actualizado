from flask import Blueprint, request, jsonify
from db import get_db_connection
import psycopg2.extras

configuraciones_bp = Blueprint('configuraciones_bp', __name__)

#obtener configuraciones
@configuraciones_bp.route('/configuraciones', methods=['GET'])
def obtener_configuraciones():
    query = "SELECT clave, valor FROM configuraciones"
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(query)
            configuraciones = {row["clave"]: row["valor"] for row in cursor.fetchall()}
        return jsonify(configuraciones)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


# Actualizar una configuración específica
@configuraciones_bp.route('/configuraciones/<clave>', methods=['PUT'])
def actualizar_configuracion(clave):
    datos = request.json
    nuevo_valor = datos.get("valor")

    if nuevo_valor is None:
        return jsonify({"error": "Se requiere un valor para actualizar"}), 400

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            query = """
                UPDATE configuraciones
                SET valor = %s, fecha_modificacion = CURRENT_TIMESTAMP
                WHERE clave = %s
            """
            cursor.execute(query, (nuevo_valor, clave))
            if cursor.rowcount == 0:
                return jsonify({"error": f"No se encontró la configuración con clave {clave}"}), 404

            conn.commit()  # Confirmar la actualización en la base de datos

        return jsonify({"mensaje": f"Configuración {clave} actualizada exitosamente"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()