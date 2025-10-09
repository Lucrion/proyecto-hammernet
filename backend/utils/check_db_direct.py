#!/usr/bin/env python3
import sqlite3
import json

def check_database():
    try:
        # Conectar a la base de datos SQLite
        conn = sqlite3.connect('ferreteria.db')
        cursor = conn.cursor()
        
        print("=== VERIFICACIÓN DE BASE DE DATOS ===")
        
        # Verificar productos catalogados
        print("\n1. Productos marcados como catalogados (en_catalogo = 1):")
        cursor.execute("""
            SELECT id_producto, nombre, descripcion, imagen_url, marca, caracteristicas, en_catalogo 
            FROM productos 
            WHERE en_catalogo = 1
        """)
        
        catalogados = cursor.fetchall()
        if catalogados:
            for producto in catalogados:
                print(f"  ID: {producto[0]}")
                print(f"  Nombre: {producto[1]}")
                print(f"  Descripción: {producto[2] or 'Sin descripción'}")
                print(f"  Imagen URL: {producto[3] or 'Sin imagen'}")
                print(f"  Marca: {producto[4] or 'Sin marca'}")
                print(f"  Características: {producto[5] or 'Sin características'}")
                print(f"  En catálogo: {producto[6]}")
                print("  ---")
        else:
            print("  No hay productos catalogados")
        
        # Verificar todos los productos
        print("\n2. Todos los productos en la base de datos:")
        cursor.execute("""
            SELECT id_producto, nombre, en_catalogo 
            FROM productos 
            ORDER BY id_producto
        """)
        
        todos = cursor.fetchall()
        for producto in todos:
            estado = "Catalogado" if producto[2] else "No catalogado"
            print(f"  ID: {producto[0]} - {producto[1]} - {estado}")
        
        # Verificar estructura de la tabla
        print("\n3. Estructura de la tabla productos:")
        cursor.execute("PRAGMA table_info(productos)")
        columnas = cursor.fetchall()
        for columna in columnas:
            print(f"  {columna[1]} ({columna[2]}) - NOT NULL: {bool(columna[3])}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error al verificar la base de datos: {e}")

if __name__ == "__main__":
    check_database()