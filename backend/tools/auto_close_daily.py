#!/usr/bin/env python3
import os, sys

# Asegura que podamos importar db.py del backend
BASE_DIR = os.path.dirname(os.path.abspath(__file__))          # .../backend/tools
APP_DIR  = os.path.abspath(os.path.join(BASE_DIR, '..'))       # .../backend
sys.path.append(APP_DIR)

from db import get_db_connection

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

def clean_leftovers():
    conn = get_db_connection(); cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE intervenciones
               SET hora_fin   = TIME '20:00:00',
                   cerrado_por = 'sistema'
             WHERE hora_fin IS NULL
               AND fecha < CURRENT_DATE
        """)
        conn.commit()
        return cur.rowcount
    finally:
        cur.close(); conn.close()

if __name__ == "__main__":
    n1 = close_today_at_20()
    n2 = clean_leftovers()
    print(f"auto_close_20h: cerradas_hoy={n1}, rezagos_cerrados={n2}")

