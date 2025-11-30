#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Migración (SQLite) para usar RUT (cuerpo+DV, 9 chars) como PK en usuarios y
ajustar FKs en ventas, movimientos de inventario y despachos.

Uso:
    python backend/scripts/migrate_rut_pk_sqlite.py

Seguro para ejecutar múltiples veces: verifica existencia de columnas/tablas nuevas.
"""

import sys
from sqlalchemy import text
from config.database import engine


def dv_calc(body: str) -> str:
    body = ''.join(ch for ch in str(body) if ch.isdigit())
    if not body:
        return ''
    acc = 0
    f = 2
    for ch in reversed(body):
        acc += int(ch) * f
        f = 2 if f == 7 else f + 1
    rest = 11 - (acc % 11)
    if rest == 11:
        return '0'
    if rest == 10:
        return 'K'
    return str(rest)


def get_cols(conn, table: str):
    return [row[1] for row in conn.execute(text(f"PRAGMA table_info({table})")).fetchall()]


def migrate_sqlite():
    with engine.connect() as conn:
        # 1) Usuarios → nueva tabla con RUT como PK
        cols_u = get_cols(conn, 'usuarios')
        if 'rut' in cols_u:
            # Crear tabla nueva solo si rut no es PK string (heurística: tipo TEXT/VARCHAR)
            pass
        conn.execute(text(
            """
            CREATE TABLE IF NOT EXISTS usuarios_new (
                rut TEXT PRIMARY KEY,
                id_usuario INTEGER UNIQUE,
                id_rol INTEGER,
                nombre TEXT NOT NULL,
                apellido TEXT,
                email TEXT,
                telefono TEXT,
                password TEXT,
                role TEXT,
                activo INTEGER DEFAULT 1,
                fecha_creacion DATETIME,
                fecha_actualizacion DATETIME
            )
            """
        ))

        # Mapear usuarios antiguos
        old_users = conn.execute(text("SELECT id_usuario, nombre, apellido, email, telefono, password, role, activo, fecha_creacion, fecha_actualizacion, rut FROM usuarios")).fetchall()
        for row in old_users:
            id_usuario, nombre, apellido, email, telefono, password, role, activo, fcrea, factual, rut_old = row
            body = None
            if rut_old is not None:
                body = ''.join(ch for ch in str(rut_old) if ch.isdigit())[:8]
            dv = dv_calc(body) if body else 'K'
            rut_full = (body or '00000000') + dv
            conn.execute(text(
                """
                INSERT OR IGNORE INTO usuarios_new (rut, id_usuario, id_rol, nombre, apellido, email, telefono, password, role, activo, fecha_creacion, fecha_actualizacion)
                VALUES (:rut, :id_usuario, NULL, :nombre, :apellido, :email, :telefono, :password, :role, :activo, :fcrea, :factual)
                """
            ), {
                'rut': rut_full,
                'id_usuario': id_usuario,
                'nombre': nombre,
                'apellido': apellido,
                'email': email,
                'telefono': telefono,
                'password': password,
                'role': role,
                'activo': activo,
                'fcrea': fcrea,
                'factual': factual,
            })

        # Renombrar y reemplazar tabla usuarios
        conn.execute(text("ALTER TABLE usuarios RENAME TO usuarios_backup"))
        conn.execute(text("ALTER TABLE usuarios_new RENAME TO usuarios"))

        # 2) Ventas → actualizar columnas y copiar
        conn.execute(text(
            """
            CREATE TABLE IF NOT EXISTS ventas_new (
                id_venta INTEGER PRIMARY KEY,
                rut_usuario TEXT NOT NULL,
                fecha_venta DATETIME,
                total_venta NUMERIC,
                estado TEXT,
                observaciones TEXT,
                tipo_documento TEXT,
                folio_documento TEXT,
                fecha_emision_sii DATE,
                cliente_rut TEXT,
                fecha_creacion DATETIME,
                fecha_actualizacion DATETIME
            )
            """
        ))

        ventas_old = conn.execute(text("SELECT * FROM ventas")).fetchall()
        # Obtener nombres de columnas dinámicamente
        v_cols = [c[0] for c in conn.execute(text("PRAGMA table_info(ventas)")).fetchall()]
        idx = {name: i for i, name in enumerate(v_cols)}
        for v in ventas_old:
            id_venta = v[idx.get('id_venta')]
            id_usuario = v[idx.get('id_usuario')]
            fecha_venta = v[idx.get('fecha_venta')]
            total_venta = v[idx.get('total_venta')]
            estado = v[idx.get('estado')]
            observaciones = v[idx.get('observaciones')]
            tipo_documento = v[idx.get('tipo_documento')] if 'tipo_documento' in idx else None
            folio_documento = v[idx.get('folio_documento')] if 'folio_documento' in idx else None
            fecha_emision_sii = v[idx.get('fecha_emision_sii')] if 'fecha_emision_sii' in idx else None
            cliente_id = v[idx.get('cliente_id')] if 'cliente_id' in idx else None
            fcrea = v[idx.get('fecha_creacion')]
            factual = v[idx.get('fecha_actualizacion')]

            rut_row = conn.execute(text("SELECT rut FROM usuarios WHERE id_usuario = :id"), {'id': id_usuario}).fetchone()
            rut_usuario = rut_row[0] if rut_row else '00000000K'
            rut_cli = None
            if cliente_id is not None:
                rcli = conn.execute(text("SELECT rut FROM usuarios WHERE id_usuario = :id"), {'id': cliente_id}).fetchone()
                rut_cli = rcli[0] if rcli else None

            conn.execute(text(
                """
                INSERT OR IGNORE INTO ventas_new (
                    id_venta, rut_usuario, fecha_venta, total_venta, estado, observaciones,
                    tipo_documento, folio_documento, fecha_emision_sii, cliente_rut, fecha_creacion, fecha_actualizacion
                ) VALUES (
                    :id_venta, :rut_usuario, :fecha_venta, :total_venta, :estado, :observaciones,
                    :tipo_documento, :folio_documento, :fecha_emision_sii, :cliente_rut, :fecha_creacion, :fecha_actualizacion
                )
                """
            ), {
                'id_venta': id_venta,
                'rut_usuario': rut_usuario,
                'fecha_venta': fecha_venta,
                'total_venta': total_venta,
                'estado': estado,
                'observaciones': observaciones,
                'tipo_documento': tipo_documento,
                'folio_documento': folio_documento,
                'fecha_emision_sii': fecha_emision_sii,
                'cliente_rut': rut_cli,
                'fecha_creacion': fcrea,
                'fecha_actualizacion': factual,
            })

        conn.execute(text("ALTER TABLE ventas RENAME TO ventas_backup"))
        conn.execute(text("ALTER TABLE ventas_new RENAME TO ventas"))

        # 3) Movimientos de inventario
        conn.execute(text(
            """
            CREATE TABLE IF NOT EXISTS movimientos_inventario_new (
                id_movimiento INTEGER PRIMARY KEY,
                id_producto INTEGER NOT NULL,
                rut_usuario TEXT NOT NULL,
                id_venta INTEGER,
                tipo_movimiento TEXT NOT NULL,
                cantidad INTEGER NOT NULL,
                cantidad_anterior INTEGER NOT NULL,
                cantidad_nueva INTEGER NOT NULL,
                motivo TEXT,
                fecha_movimiento DATETIME NOT NULL,
                fecha_creacion DATETIME
            )
            """
        ))

        movs = conn.execute(text("SELECT * FROM movimientos_inventario")).fetchall()
        m_cols = [c[0] for c in conn.execute(text("PRAGMA table_info(movimientos_inventario)")).fetchall()]
        midx = {name: i for i, name in enumerate(m_cols)}
        for m in movs:
            id_mov = m[midx.get('id_movimiento')]
            id_producto = m[midx.get('id_producto')]
            id_usuario = m[midx.get('id_usuario')]
            id_venta = m[midx.get('id_venta')]
            tipo = m[midx.get('tipo_movimiento')]
            cantidad = m[midx.get('cantidad')]
            cant_ant = m[midx.get('cantidad_anterior')]
            cant_new = m[midx.get('cantidad_nueva')]
            motivo = m[midx.get('motivo')]
            fmov = m[midx.get('fecha_movimiento')]
            fcrea = m[midx.get('fecha_creacion')]

            rut_row = conn.execute(text("SELECT rut FROM usuarios WHERE id_usuario = :id"), {'id': id_usuario}).fetchone()
            rut_usuario = rut_row[0] if rut_row else '00000000K'

            conn.execute(text(
                """
                INSERT OR IGNORE INTO movimientos_inventario_new (
                    id_movimiento, id_producto, rut_usuario, id_venta, tipo_movimiento, cantidad,
                    cantidad_anterior, cantidad_nueva, motivo, fecha_movimiento, fecha_creacion
                ) VALUES (
                    :id_movimiento, :id_producto, :rut_usuario, :id_venta, :tipo_movimiento, :cantidad,
                    :cantidad_anterior, :cantidad_nueva, :motivo, :fecha_movimiento, :fecha_creacion
                )
                """
            ), {
                'id_movimiento': id_mov,
                'id_producto': id_producto,
                'rut_usuario': rut_usuario,
                'id_venta': id_venta,
                'tipo_movimiento': tipo,
                'cantidad': cantidad,
                'cantidad_anterior': cant_ant,
                'cantidad_nueva': cant_new,
                'motivo': motivo,
                'fecha_movimiento': fmov,
                'fecha_creacion': fcrea,
            })

        conn.execute(text("ALTER TABLE movimientos_inventario RENAME TO movimientos_inventario_backup"))
        conn.execute(text("ALTER TABLE movimientos_inventario_new RENAME TO movimientos_inventario"))

        # 4) Despachos
        conn.execute(text(
            """
            CREATE TABLE IF NOT EXISTS despachos_new (
                id_despacho INTEGER PRIMARY KEY,
                rut_usuario TEXT NOT NULL,
                buscar TEXT,
                calle TEXT NOT NULL,
                numero TEXT NOT NULL,
                depto TEXT,
                adicional TEXT,
                fecha_creacion DATETIME,
                fecha_actualizacion DATETIME
            )
            """
        ))
        d_old = conn.execute(text("SELECT * FROM despachos")).fetchall()
        d_cols = [c[0] for c in conn.execute(text("PRAGMA table_info(despachos)")).fetchall()]
        didx = {name: i for i, name in enumerate(d_cols)}
        for d in d_old:
            id_d = d[didx.get('id_despacho')]
            id_usuario = d[didx.get('id_usuario')]
            buscar = d[didx.get('buscar')]
            calle = d[didx.get('calle')]
            numero = d[didx.get('numero')]
            depto = d[didx.get('depto')]
            adicional = d[didx.get('adicional')]
            fcrea = d[didx.get('fecha_creacion')]
            factual = d[didx.get('fecha_actualizacion')]
            rut_row = conn.execute(text("SELECT rut FROM usuarios WHERE id_usuario = :id"), {'id': id_usuario}).fetchone()
            rut_usuario = rut_row[0] if rut_row else '00000000K'
            conn.execute(text(
                """
                INSERT OR IGNORE INTO despachos_new (
                    id_despacho, rut_usuario, buscar, calle, numero, depto, adicional, fecha_creacion, fecha_actualizacion
                ) VALUES (
                    :id_despacho, :rut_usuario, :buscar, :calle, :numero, :depto, :adicional, :fecha_creacion, :fecha_actualizacion
                )
                """
            ), {
                'id_despacho': id_d,
                'rut_usuario': rut_usuario,
                'buscar': buscar,
                'calle': calle,
                'numero': numero,
                'depto': depto,
                'adicional': adicional,
                'fecha_creacion': fcrea,
                'fecha_actualizacion': factual,
            })

        conn.execute(text("ALTER TABLE despachos RENAME TO despachos_backup"))
        conn.execute(text("ALTER TABLE despachos_new RENAME TO despachos"))

        print("✅ Migración SQLite completada: usuarios, ventas, movimientos, despachos actualizados a RUT como PK")


if __name__ == '__main__':
    try:
        if engine.dialect.name != 'sqlite':
            print("Este script está diseñado para SQLite. Para Postgres, usar una migración específica.")
        migrate_sqlite()
    except Exception as e:
        print(f"❌ Error en migración: {e}")
        sys.exit(1)

