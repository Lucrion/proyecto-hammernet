#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de migración para agregar la columna 'activo' a la tabla usuarios
"""

import sqlite3
import os
import sys

def migrate_add_activo_column():
    """Agrega la columna 'activo' a la tabla usuarios si no existe"""
    
    # Ruta de la base de datos
    db_path = os.path.join(os.path.dirname(__file__), 'ferreteria.db')
    
    if not os.path.exists(db_path):
        print("❌ Base de datos no encontrada")
        return False
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si la columna 'activo' ya existe
        cursor.execute("PRAGMA table_info(usuarios)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'activo' in columns:
            print("✅ La columna 'activo' ya existe en la tabla usuarios")
            return True
        
        # Agregar la columna 'activo' con valor por defecto TRUE
        cursor.execute("ALTER TABLE usuarios ADD COLUMN activo BOOLEAN DEFAULT 1")
        
        # Actualizar todos los usuarios existentes para que estén activos
        cursor.execute("UPDATE usuarios SET activo = 1 WHERE activo IS NULL")
        
        conn.commit()
        print("✅ Columna 'activo' agregada exitosamente a la tabla usuarios")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en la migración: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    print("🔄 Iniciando migración de base de datos...")
    if migrate_add_activo_column():
        print("✅ Migración completada exitosamente")
    else:
        print("❌ Error en la migración")
        sys.exit(1)