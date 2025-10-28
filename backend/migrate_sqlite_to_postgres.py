#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de migración de datos desde SQLite (local) a PostgreSQL (Render)

Uso:
  - Variables de entorno:
      DATABASE_URL: DSN de Postgres de destino (Render)
  - Opcionales:
      SQLITE_PATH: ruta al archivo SQLite local (por defecto backend/ferreteria.db)

  Ejemplo:
    set SQLITE_PATH=c:\Users\darky\Desktop\proyecto\backend\ferreteria.db
    set DATABASE_URL=postgresql://user:pass@host:port/db
    python backend/scripts/migrate_sqlite_to_postgres.py

Este script:
  1) Conecta a SQLite y Postgres
  2) Crea las tablas en Postgres si no existen
  3) Copia datos de todas las tablas principales conservando IDs
  4) Ajusta las secuencias de Postgres para coincidir con los IDs insertados
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Asegurar imports de backend
BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BACKEND_ROOT)

from config.database import Base  # metadata
from models.usuario import UsuarioDB
from models.producto import ProductoDB
from models.categoria import CategoriaDB
from models.proveedor import ProveedorDB
from models.mensaje import MensajeContactoDB
from models.venta import VentaDB, DetalleVentaDB, MovimientoInventarioDB
from models.despacho import DespachoDB


def row_to_dict(sa_obj):
    d = {k: v for k, v in sa_obj.__dict__.items() if not k.startswith('_sa_')}
    return d


def create_session(engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)()


def ensure_tables(pg_engine):
    Base.metadata.create_all(pg_engine)


def bulk_copy_table(sql_session, pg_session, model, table_name=None):
    name = table_name or model.__tablename__
    print(f"Copiando tabla: {name}...")
    # Si la tabla destino ya tiene datos, evitar duplicar (idempotente)
    try:
        existing = pg_session.execute(text(f"SELECT 1 FROM {name} LIMIT 1")).first()
        if existing:
            print(f"  - Tabla destino {name} ya tiene datos; se omite copia.")
            return 0
    except SQLAlchemyError as e:
        print(f"  ! No se pudo verificar datos existentes en {name}: {e}")
    rows = sql_session.query(model).all()
    if not rows:
        print(f"  - No hay datos en {name}, omitido.")
        return 0
    # Insertar usando INSERT directo para preservar IDs
    data = [row_to_dict(r) for r in rows]
    try:
        pg_session.execute(model.__table__.insert(), data)
        pg_session.commit()
        print(f"  - Insertados {len(data)} registros en {name}")
        return len(data)
    except SQLAlchemyError as e:
        pg_session.rollback()
        print(f"  ! Error insertando en {name}: {e}")
        return 0


def reset_sequence(pg_engine, model):
    table = model.__table__
    pk_cols = list(table.primary_key.columns)
    if len(pk_cols) != 1:
        return
    pk_col = pk_cols[0].name
    table_name = table.name
    sql = text(
        "SELECT setval(pg_get_serial_sequence(:tname, :pk), COALESCE((SELECT MAX(" + pk_col + ") FROM " + table_name + "), 1), true)"
    )
    with pg_engine.connect() as conn:
        try:
            conn.execute(sql, {"tname": table_name, "pk": pk_col})
            print(f"  - Secuencia ajustada para {table_name}.{pk_col}")
        except SQLAlchemyError as e:
            print(f"  ! No se pudo ajustar secuencia de {table_name}: {e}")


def main():
    load_dotenv()
    sqlite_path = os.getenv('SQLITE_PATH')
    if not sqlite_path:
        sqlite_path = os.path.join(BACKEND_ROOT, 'ferreteria.db')
    pg_url = os.getenv('DATABASE_URL')

    if not os.path.isfile(sqlite_path):
        print(f"Error: no se encuentra SQLite en {sqlite_path}")
        return
    if not pg_url or 'postgres' not in pg_url:
        print("Error: DATABASE_URL debe apuntar a PostgreSQL")
        return

    print(f"SQLite: {sqlite_path}")
    print(f"Postgres: {pg_url}")

    sql_engine = create_engine(f"sqlite:///{sqlite_path}")
    pg_engine = create_engine(pg_url)

    sql_session = create_session(sql_engine)
    pg_session = create_session(pg_engine)

    # 1) Asegurar tablas en Postgres
    print("Creando tablas en Postgres (si faltan)...")
    ensure_tables(pg_engine)

    # 2) Copiar en orden lógico para respetar FKs
    total = 0
    total += bulk_copy_table(sql_session, pg_session, CategoriaDB)
    total += bulk_copy_table(sql_session, pg_session, ProveedorDB)
    total += bulk_copy_table(sql_session, pg_session, UsuarioDB)
    total += bulk_copy_table(sql_session, pg_session, ProductoDB)
    total += bulk_copy_table(sql_session, pg_session, VentaDB)
    total += bulk_copy_table(sql_session, pg_session, DetalleVentaDB)
    total += bulk_copy_table(sql_session, pg_session, MovimientoInventarioDB)
    total += bulk_copy_table(sql_session, pg_session, MensajeContactoDB)
    total += bulk_copy_table(sql_session, pg_session, DespachoDB)

    print(f"Copiados {total} registros en total.")

    # 3) Ajustar secuencias
    print("Ajustando secuencias...")
    for model in [CategoriaDB, ProveedorDB, UsuarioDB, ProductoDB, VentaDB, DetalleVentaDB, MovimientoInventarioDB, MensajeContactoDB, DespachoDB]:
        reset_sequence(pg_engine, model)

    print("Migración completada.")

    # Cerrar sesiones
    try:
        sql_session.close()
        pg_session.close()
    except Exception:
        pass


if __name__ == '__main__':
    main()