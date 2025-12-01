#!/usr/bin/env python3
"""
Script para verificar la estructura de las tablas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

def main():
    # Cargar variables de entorno
    load_dotenv()
    
    # Configurar conexión directa
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if DATABASE_URL and "postgres" in DATABASE_URL:
        engine = create_engine(DATABASE_URL)
    else:
        # SQLite local
        backend_root = os.path.dirname(os.path.dirname(__file__))
        db_path = os.path.join(backend_root, 'ferreteria.db')
        engine = create_engine(f"sqlite:///{db_path}")
    
    print("Verificando estructura de tablas...")
    print("=" * 50)
    
    with engine.connect() as conn:
        # Verificar estructura de tabla usuarios
        print("ESTRUCTURA TABLA USUARIOS:")
        try:
            result = conn.execute(text("PRAGMA table_info(usuarios)"))
            columns = result.fetchall()
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
        except Exception as e:
            print(f"Error: {e}")
        
        print("\n" + "=" * 30)
        
        # Verificar estructura de tabla productos
        print("ESTRUCTURA TABLA PRODUCTOS:")
        try:
            result = conn.execute(text("PRAGMA table_info(productos)"))
            columns = result.fetchall()
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
        except Exception as e:
            print(f"Error: {e}")
        
        print("\n" + "=" * 30)
        
        # Verificar estructura de tabla ventas
        print("ESTRUCTURA TABLA VENTAS:")
        try:
            result = conn.execute(text("PRAGMA table_info(ventas)"))
            columns = result.fetchall()
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
        except Exception as e:
            print(f"Error: {e}")
        
        print("\n" + "=" * 30)
        
        # Verificar estructura de tabla detalles_venta
        print("ESTRUCTURA TABLA DETALLES_VENTA:")
        try:
            result = conn.execute(text("PRAGMA table_info(detalles_venta)"))
            columns = result.fetchall()
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()