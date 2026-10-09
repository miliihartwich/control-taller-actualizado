from flask import Blueprint, request, jsonify
from db import get_db_connection
import psycopg2.extras
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
import traceback
import math


intervencion_bp = Blueprint('intervencion_bp', __name__)


# POST /intervenciones/registrar
@intervencion_bp.post("/intervenciones/registrar")
@jwt_required()
def registrar_intervencion_admin():
    data = request.get_json() or {}
    identidad = get_jwt_identity()

    conn = get_db_connection(); cur = conn.cursor()
    try:
        # validar rol
        cur.execute('SELECT rol FROM usuario WHERE usuario=%s', (identidad,))
        r = cur.fetchone()
        if not r: return jsonify({'error':'Usuario no encontrado'}), 404
        rol = r[0]
        if rol not in ('administrador','propietario'):
            return jsonify({'error':'Solo administración puede registrar manualmente'}), 403

        # empleado (por nombre o cédula)
        empleado_nombre = data.get('empleado')
        empleado_cedula = data.get('cedula')
        if empleado_nombre and not empleado_cedula:
            cur.execute('SELECT cedula FROM empleado WHERE nombre=%s', (empleado_nombre,))
            r = cur.fetchone()
            if not r: return jsonify({'error': f'Empleado "{empleado_nombre}" no encontrado'}), 400
            empleado_cedula = r[0]
        if not empleado_cedula:
            return jsonify({'error':'Falta cedula de empleado'}), 400

        # fecha/hora provistas
        fecha = data.get('fecha')
        hora_inicio = data.get('hora_inicio')
        hora_fin = data.get('hora_fin')
        if not (fecha and hora_inicio and hora_fin):
            return jsonify({'error':'Faltan fecha/hora_inicio/hora_fin'}), 400

        # resolver número de orden
        division = data.get('division'); tipo = data.get('tipo'); descripcion = data.get('descripcion')
        if not (division and tipo and descripcion):
            return jsonify({'error':'Faltan division/tipo/descripcion'}), 400

        cur.execute('SELECT id FROM division_opciones WHERE nombre=%s', (division,))
        r = cur.fetchone(); 
        if not r: return jsonify({'error':f'División "{division}" no encontrada'}), 400
        id_div = r[0]

        cur.execute('SELECT id FROM tipo_opciones WHERE nombre=%s AND id_division=%s', (tipo, id_div))

        r = cur.fetchone(); 
        if not r: return jsonify({'error':f'Tipo "{tipo}" no encontrado'}), 400
        id_tipo = r[0]

        cur.execute('SELECT id_descripcion FROM descripcion_opciones WHERE nombre_descripcion=%s AND id_tipo=%s', (descripcion, id_tipo))
        r = cur.fetchone(); 
        if not r: return jsonify({'error':f'Descripción "{descripcion}" no encontrada para el tipo'}), 400
        id_desc = r[0]

        cur.execute('SELECT numero_orden FROM ordenes WHERE division_id=%s AND tipo_id=%s AND descripcion_id=%s', (id_div, id_tipo, id_desc))
        r = cur.fetchone(); 
        if not r: return jsonify({'error':'No se encontró número de orden'}), 400
        numero_orden = r[0]

        # insertar YA cerrada y marcada por administración
        cur.execute("""
            INSERT INTO intervenciones (empleado_cedula, numero_orden, fecha, hora_inicio, hora_fin, cerrado_por)
            VALUES (%s, %s, %s, %s, %s, 'administracion')
        """, (empleado_cedula, numero_orden, fecha, hora_inicio, hora_fin))
        conn.commit()
        return jsonify({'message':'Intervención registrada por administración'}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close(); conn.close()

# iniciar intervencion por operario
@intervencion_bp.post("/intervenciones/iniciar")
@jwt_required()
def iniciar_intervencion():
    data = request.get_json() or {}
    identidad = get_jwt_identity()

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # rol + cédula del usuario
        cur.execute('SELECT rol, cedula FROM usuario WHERE usuario=%s', (identidad,))
        row = cur.fetchone()
        if not row:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        rol, cedula = row
        if rol != 'operario':
            return jsonify({'error': 'Solo operario puede iniciar aquí'}), 403
        if not cedula:
            return jsonify({'error': 'Operario sin cédula asociada'}), 400

        # 0) si ya hay una abierta para ese operario, opcionalmente evitar duplicados
        # (si querés mantener el comportamiento actual, podés comentar esto)
        cur.execute("""
            SELECT 1
              FROM intervenciones
             WHERE empleado_cedula = %s
               AND hora_fin IS NULL
             LIMIT 1
        """, (cedula,))
        if cur.fetchone():
            return jsonify({'error': 'Ya existe una intervención abierta para este operario'}), 409

        numero_orden = data.get('numero_orden')

        # 1) si viene numero_orden directo, lo usamos
        if numero_orden:
            cur.execute("SELECT 1 FROM ordenes WHERE numero_orden=%s", (numero_orden,))
            if not cur.fetchone():
                return jsonify({'error': f'La orden {numero_orden} no existe'}), 400

        else:
            # 2) intentar por IDs (nuevo front)
            division_id = data.get('division_id')
            tipo_id = data.get('tipo_id')
            descripcion_id = data.get('descripcion_id')

            if division_id and tipo_id and descripcion_id:
                cur.execute("""
                    SELECT numero_orden
                      FROM ordenes
                     WHERE division_id=%s AND tipo_id=%s AND descripcion_id=%s
                """, (division_id, tipo_id, descripcion_id))
                r = cur.fetchone()
                if not r:
                    return jsonify({'error': 'No se encontró número de orden para la intervención (IDs)'}), 400
                numero_orden = r[0]

            else:
                # 3) fallback legacy por nombres (pero bien: tipo acotado por división)
                division = (data.get('division') or '').strip()
                tipo = (data.get('tipo') or '').strip()
                descripcion = (data.get('descripcion') or '').strip()

                if not division or not tipo or not descripcion:
                    return jsonify({'error': 'Faltan division/tipo/descripcion o IDs/numero_orden'}), 400

                # división -> id
                cur.execute('SELECT id FROM division_opciones WHERE nombre=%s', (division,))
                r = cur.fetchone()
                if not r:
                    return jsonify({'error': f'División "{division}" no encontrada'}), 400
                id_div = r[0]

                # tipo -> id (ACOTADO por división, esta es la clave)
                cur.execute('SELECT id FROM tipo_opciones WHERE nombre=%s AND id_division=%s', (tipo, id_div))
                r = cur.fetchone()
                if not r:
                    return jsonify({'error': f'Tipo "{tipo}" no encontrado para la división "{division}"'}), 400
                id_tipo = r[0]

                # descripción -> id (por tipo)
                cur.execute("""
                    SELECT id_descripcion
                      FROM descripcion_opciones
                     WHERE nombre_descripcion=%s AND id_tipo=%s
                """, (descripcion, id_tipo))
                r = cur.fetchone()
                if not r:
                    return jsonify({'error': f'Descripción "{descripcion}" no encontrada para el tipo "{tipo}"'}), 400
                id_desc = r[0]

                # orden por ids
                cur.execute("""
                    SELECT numero_orden
                      FROM ordenes
                     WHERE division_id=%s AND tipo_id=%s AND descripcion_id=%s
                """, (id_div, id_tipo, id_desc))
                r = cur.fetchone()
                if not r:
                    return jsonify({'error': 'No se encontró número de orden para la intervención'}), 400
                numero_orden = r[0]

        # insertar abierta (fecha y hora_inicio consistentes - Montevideo)
        cur.execute("""
            INSERT INTO intervenciones (empleado_cedula, numero_orden, fecha, hora_inicio, hora_fin, cerrado_por)
            VALUES (
                %s,
                %s,
                (now() AT TIME ZONE 'America/Montevideo')::date,
                (now() AT TIME ZONE 'America/Montevideo')::time,
                NULL,
                'pendiente'
            )
        """, (cedula, numero_orden))

        conn.commit()
        return jsonify({'message': 'Intervención iniciada', 'numero_orden': numero_orden}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()



# cerrar intervencion por operario
@intervencion_bp.route('/intervenciones/cerrar', methods=['PUT'])
@jwt_required()
def cerrar_intervencion():
    data = request.get_json(silent=True) or {}
    numero_orden = data.get('numero_orden')  # opcional

    identidad = get_jwt_identity()
    if not identidad:
        return jsonify({'error': 'No autorizado'}), 401

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # obtener cédula del usuario autenticado
        cur.execute('SELECT cedula FROM usuario WHERE usuario = %s', (identidad,))
        row = cur.fetchone()
        if not row:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        cedula = row[0]

        if numero_orden:
            # cerrar la abierta de esa orden para ese empleado
            cur.execute("""
                UPDATE intervenciones
                   SET hora_fin    = (now() AT TIME ZONE 'America/Montevideo')::time,
                       cerrado_por = 'operario'
                 WHERE empleado_cedula = %s
                   AND numero_orden    = %s
                   AND hora_fin IS NULL
            """, (cedula, numero_orden))
        else:
            # cerrar la última abierta para ese empleado
            cur.execute("""
                WITH t AS (
                    SELECT empleado_cedula, numero_orden, fecha, hora_inicio
                      FROM intervenciones
                     WHERE empleado_cedula = %s
                       AND hora_fin IS NULL
                  ORDER BY fecha DESC, hora_inicio DESC
                     LIMIT 1
                )
                UPDATE intervenciones i
                   SET hora_fin    = (now() AT TIME ZONE 'America/Montevideo')::time,
                       cerrado_por = 'operario'
                  FROM t
                 WHERE i.empleado_cedula = t.empleado_cedula
                   AND i.numero_orden     = t.numero_orden
                   AND i.fecha            = t.fecha
                   AND i.hora_inicio      = t.hora_inicio
            """, (cedula,))  # ✅ ojo: solo un parámetro

        if cur.rowcount == 0:
            conn.rollback()
            return jsonify({'error': 'No hay intervención abierta para cerrar.'}), 404

        conn.commit()
        return jsonify({
            'message': 'Intervención cerrada',
            'cerrado_por': 'operario'
        }), 200

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()


#cerrar intervenciones abiertas a las 20hs (cierre automatico)
def close_today_at_20():
    conn = get_db_connection(); cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE intervenciones
               SET hora_fin   = NOW()::time,
                   cerrado_por = 'sistema'
             WHERE hora_fin IS NULL
               AND fecha = CURRENT_DATE
        """)
        conn.commit()

        return cur.rowcount
    finally:
        cur.close(); conn.close()

# obtener intervenciones por empleado
@intervencion_bp.route('/get_intervenciones', methods=['GET'])
def get_intervenciones():
    try:
        empleado_id = request.args.get('empleado_id')
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')

        if not empleado_id:
            return jsonify({"error": "El parámetro 'empleado_id' es obligatorio"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cursor.execute("SELECT remuneracion FROM empleado WHERE cedula = %s", (empleado_id,))
        empleado = cursor.fetchone()
        if not empleado:
            return jsonify({"error": "Empleado no encontrado"}), 404
        remuneracion = float(empleado["remuneracion"])

        cursor.execute("""
            SELECT clave, valor
            FROM configuraciones
            WHERE clave IN ('factor_fijo', 'costo_fijo_por_hora')
        """)
        configuraciones = cursor.fetchall()
        config_dict = {row["clave"]: float(row["valor"]) for row in configuraciones}

        if "factor_fijo" not in config_dict or "costo_fijo_por_hora" not in config_dict:
            return jsonify({"error": "Configuraciones incompletas"}), 500

        factor_fijo = config_dict["factor_fijo"]
        costo_fijo_hora = config_dict["costo_fijo_por_hora"]

        costo_hora = (remuneracion * factor_fijo) + costo_fijo_hora

        query = """
            SELECT
                i.empleado_cedula,
                i.numero_orden,
                d.nombre AS division,
                t.nombre AS tipo,
                descripcion_op.nombre_descripcion AS descripcion,
                SUM(EXTRACT(EPOCH FROM (i.hora_fin - i.hora_inicio)) / 3600) AS horas_trabajadas
            FROM intervenciones i
            JOIN ordenes o ON i.numero_orden = o.numero_orden
            JOIN division_opciones d ON o.division_id = d.id
            JOIN tipo_opciones t ON o.tipo_id = t.id
            JOIN descripcion_opciones descripcion_op
                ON o.descripcion_id = descripcion_op.id_descripcion
            WHERE i.empleado_cedula = %s
              AND i.hora_fin IS NOT NULL
        """

        parametros = [empleado_id]

        if fecha_desde:
            query += " AND i.fecha >= %s"
            parametros.append(fecha_desde)

        if fecha_hasta:
            query += " AND i.fecha <= %s"
            parametros.append(fecha_hasta)


        query += """
            GROUP BY
                i.empleado_cedula,
                i.numero_orden,
                d.nombre,
                t.nombre,
                descripcion_op.nombre_descripcion
            ORDER BY i.numero_orden
        """

        cursor.execute(query, tuple(parametros))
        resultados = cursor.fetchall()

        intervenciones = []
        total_minutos = 0
        total_costo = 0.0

        for row in resultados:
            horas = float(row["horas_trabajadas"] or 0.0)

            # ✅ minuto empezado (ceil) -> minutos cobrables
            minutos_cobrables = math.ceil(horas * 60)

            # ✅ costo coherente con minutos cobrables
            horas_cobrables = minutos_cobrables / 60.0
            costo_intervencion = horas_cobrables * costo_hora

            horas_int = minutos_cobrables // 60
            minutos = minutos_cobrables % 60
            horas_formateadas = f"{horas_int:02}:{minutos:02}"

            intervenciones.append({
                "empleado_cedula": row["empleado_cedula"],
                "numero_orden": row["numero_orden"],
                "division": row["division"],
                "tipo": row["tipo"],
                "descripcion": row["descripcion"],
                "horas_trabajadas": horas_formateadas,
                "costo_intervencion": round(costo_intervencion, 2)
            })

            total_minutos += minutos_cobrables
            total_costo += costo_intervencion

        total_horas_int = total_minutos // 60
        total_minutos_rest = total_minutos % 60
        total_horas_formateadas = f"{total_horas_int:02}:{total_minutos_rest:02}"

        return jsonify({
            "intervenciones": intervenciones,
            "total_horas": total_horas_formateadas,
            "total_costo": round(total_costo, 2)
        }), 200

    except Exception as e:
        print("❌ Error en /get_intervenciones:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

    finally:
        if 'conn' in locals():
            conn.close()

# GET /intervenciones/abierta -> última abierta del usuario autenticado
@intervencion_bp.route('/intervenciones/abierta', methods=['GET'])
@jwt_required()
def abierta_por_usuario():
    identidad = get_jwt_identity()
    if not identidad:
        return jsonify({'error': 'No autorizado'}), 401

    conn = get_db_connection(); cur = conn.cursor()
    try:
        # 1) usuario -> cédula
        cur.execute('SELECT cedula FROM usuario WHERE usuario = %s', (identidad,))
        row = cur.fetchone()
        if not row:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        cedula = row[0]

        # 2) última intervención abierta de ese empleado
        cur.execute("""
            SELECT
            i.numero_orden,
            d.nombre AS division,
            t.nombre AS tipo,
            des.nombre_descripcion AS descripcion,
            i.fecha,
            i.hora_inicio
            FROM intervenciones i
            JOIN ordenes o ON o.numero_orden = i.numero_orden
            JOIN division_opciones d ON d.id = o.division_id
            JOIN tipo_opciones t ON t.id = o.tipo_id
            JOIN descripcion_opciones des ON des.id_descripcion = o.descripcion_id
            WHERE i.empleado_cedula = %s
            AND i.hora_fin IS NULL
            ORDER BY i.fecha DESC, i.hora_inicio DESC
            LIMIT 1
        """, (cedula,))

        r = cur.fetchone()

        if not r:
            return jsonify({'abierta': None}), 200

        no, div, tip, desc, fec, hi = r
        return jsonify({
            'abierta': {
                'numero_orden': no,
                'division': div,
                'tipo': tip,
                'descripcion': desc,
                'fecha': str(fec),
                'hora_inicio': str(hi),
            }
        }), 200
        


    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close(); conn.close()

# listar TODAS las intervenciones (sin filtros)
@intervencion_bp.route('/intervenciones/todas', methods=['GET'])
@jwt_required()
def intervenciones_todas():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        query = """
            SELECT
                d.nombre AS division,
                t.nombre AS tipo,
                des.nombre_descripcion AS descripcion,
                i.fecha,
                i.hora_inicio,
                i.hora_fin,
                i.empleado_cedula,
                e.nombre AS empleado_nombre,
                i.numero_orden
            FROM intervenciones i
            JOIN ordenes o ON o.numero_orden = i.numero_orden
            JOIN division_opciones d ON d.id = o.division_id
            JOIN tipo_opciones t ON t.id = o.tipo_id
            LEFT JOIN descripcion_opciones des ON des.id_descripcion = o.descripcion_id
            JOIN empleado e ON e.cedula = i.empleado_cedula
            ORDER BY i.fecha DESC, i.hora_inicio DESC;
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        data = []
        for r in rows:
            data.append({
                "division": r["division"],
                "tipo": r["tipo"],
                "descripcion": r["descripcion"],
                "fecha": r["fecha"].isoformat() if r["fecha"] else None,
                "hora_inicio": str(r["hora_inicio"]) if r["hora_inicio"] else None,
                "hora_fin": str(r["hora_fin"]) if r["hora_fin"] else None,
                "empleado_cedula": r["empleado_cedula"],
                "empleado_nombre": r["empleado_nombre"],
                "numero_orden": r["numero_orden"],
            })

        return jsonify({"intervenciones": data}), 200

    except Exception as e:
        print("❌ Error en /intervenciones/todas:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()


