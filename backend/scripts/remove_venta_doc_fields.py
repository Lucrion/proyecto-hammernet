#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import text
import os
from config.database import engine

def drop_columns_postgres():
    with engine.begin() as conn:
        conn.execute(text(
            "ALTER TABLE ventas DROP COLUMN IF EXISTS tipo_documento"
        ))
        conn.execute(text(
            "ALTER TABLE ventas DROP COLUMN IF EXISTS folio_documento"
        ))
        conn.execute(text(
            "ALTER TABLE ventas DROP COLUMN IF EXISTS fecha_emision_sii"
        ))

def drop_columns_sqlite():
    with engine.begin() as conn:
        cols = [row[1] for row in conn.execute(text("PRAGMA table_info(ventas)")).fetchall()]
        targets = {'tipo_documento','folio_documento','fecha_emision_sii'}
        if not (set(cols) & targets):
            _log("[DB] columnas ya ausentes: nada que hacer")
            return
        conn.execute(text("PRAGMA foreign_keys=OFF"))
        conn.execute(text(
            """
            CREATE TABLE ventas_new (
                id_venta INTEGER PRIMARY KEY,
                rut_usuario TEXT,
                cliente_rut TEXT,
                fecha_venta DATETIME,
                total_venta NUMERIC,
                estado TEXT,
                observaciones TEXT,
                fecha_creacion DATETIME,
                fecha_actualizacion DATETIME
            )
            """
        ))
        conn.execute(text(
            """
            INSERT INTO ventas_new (id_venta, rut_usuario, cliente_rut, fecha_venta, total_venta, estado, observaciones, fecha_creacion, fecha_actualizacion)
            SELECT id_venta, rut_usuario, cliente_rut, fecha_venta, total_venta, estado, observaciones, fecha_creacion, fecha_actualizacion FROM ventas
            """
        ))
        conn.execute(text("ALTER TABLE ventas RENAME TO ventas_backup"))
        conn.execute(text("ALTER TABLE ventas_new RENAME TO ventas"))
        # Re-crear índices principales
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_ventas_fecha_venta ON ventas (fecha_venta)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_ventas_estado ON ventas (estado)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_ventas_usuario ON ventas (rut_usuario)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_ventas_cliente ON ventas (cliente_rut)"))
        conn.execute(text("PRAGMA foreign_keys=ON"))
        _log("[DB] columnas eliminadas en SQLite: tipo_documento, folio_documento, fecha_emision_sii")

def _log(msg: str):
    try:
        path = os.path.join(os.path.dirname(__file__), '..', 'remove_columns_result.txt')
        path = os.path.abspath(path)
        with open(path, 'a', encoding='utf-8') as f:
            f.write(msg + "\n")
    except Exception:
        pass

def main():
    if engine.dialect.name == 'sqlite':
        drop_columns_sqlite()
    else:
        drop_columns_postgres()
        _log("[DB] columnas eliminadas en Postgres (si existían)")

if __name__ == '__main__':
    main()
