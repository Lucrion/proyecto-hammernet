#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from database import DATABASE_URL
import os

def migrate_proveedores():
    """Añadir nuevas columnas a la tabla proveedores"""
    # Usar la misma lógica que database.py
    if DATABASE_URL and "postgres" in DATABASE_URL:
        engine = create_engine(DATABASE_URL)
    else:
        db_path = os.path.join(os.path.dirname(__file__), 'ferreteria.db')
        engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    
    try:
        with engine.connect() as conn:
            # Lista de nuevas columnas a añadir
            nuevas_columnas = [
                "ALTER TABLE proveedores ADD COLUMN rut VARCHAR(20)",
                "ALTER TABLE proveedores ADD COLUMN razon_social VARCHAR(200)", 
                "ALTER TABLE proveedores ADD COLUMN sucursal VARCHAR(100)",
                "ALTER TABLE proveedores ADD COLUMN ciudad VARCHAR(100)",
                "ALTER TABLE proveedores ADD COLUMN celular VARCHAR(50)",
                "ALTER TABLE proveedores ADD COLUMN correo VARCHAR(100)"
            ]
            
            for sql in nuevas_columnas:
                try:
                    conn.execute(text(sql))
                    print(f"✅ Ejecutado: {sql}")
                except Exception as e:
                    if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                        print(f"⚠️  Columna ya existe: {sql}")
                    else:
                        print(f"❌ Error: {sql} - {e}")
            
            conn.commit()
            print("\n✅ Migración de proveedores completada exitosamente")
            
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        return False
    
    return True

if __name__ == "__main__":
    migrate_proveedores()