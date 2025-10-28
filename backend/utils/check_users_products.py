#!/usr/bin/env python3
"""
Script para verificar usuarios y productos existentes en la base de datos
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
    
    print("Conectando a la base de datos...")
    print("=" * 50)
    
    with engine.connect() as conn:
        # Verificar usuarios
        print("USUARIOS EN LA BASE DE DATOS:")
        try:
            result = conn.execute(text("SELECT id_usuario, email, nombre, username, activo FROM usuarios"))
            usuarios = result.fetchall()
            if usuarios:
                for usuario in usuarios:
                    print(f"ID: {usuario[0]}, Email: {usuario[1]}, Nombre: {usuario[2]}, Username: {usuario[3]}, Activo: {usuario[4]}")
            else:
                print("No hay usuarios registrados")
        except Exception as e:
            print(f"Error consultando usuarios: {e}")
        
        print("\n" + "=" * 50)
        
        # Verificar productos
        print("PRODUCTOS EN LA BASE DE DATOS:")
        try:
            result = conn.execute(text("SELECT id_producto, nombre, cantidad_disponible, precio_venta, en_catalogo FROM productos LIMIT 5"))
            productos = result.fetchall()
            if productos:
                for producto in productos:
                    print(f"ID: {producto[0]}, Nombre: {producto[1]}, Stock: {producto[2]}, Precio: ${producto[3]}, En catálogo: {producto[4]}")
            else:
                print("No hay productos registrados")
        except Exception as e:
            print(f"Error consultando productos: {e}")
        
        print("\n" + "=" * 50)
        
        # Contar registros
        try:
            usuarios_count = conn.execute(text("SELECT COUNT(*) FROM usuarios")).fetchone()[0]
            productos_count = conn.execute(text("SELECT COUNT(*) FROM productos")).fetchone()[0]
            productos_con_stock = conn.execute(text("SELECT COUNT(*) FROM productos WHERE cantidad_disponible > 0")).fetchone()[0]
            
            print(f"Total usuarios: {usuarios_count}")
            print(f"Total productos: {productos_count}")
            print(f"Productos con stock disponible: {productos_con_stock}")
        except Exception as e:
            print(f"Error contando registros: {e}")

if __name__ == "__main__":
    main()