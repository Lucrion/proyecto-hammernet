#!/usr/bin/env python3
import sqlite3

def check_codigo_interno():
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect('ferreteria.db')
        cursor = conn.cursor()
        
        # Verificar los códigos internos de los productos
        cursor.execute("""
            SELECT id_producto, nombre, codigo_interno, codigo_barras
            FROM productos
            ORDER BY id_producto
        """)
        
        productos = cursor.fetchall()
        
        print("=== CÓDIGOS INTERNOS DE PRODUCTOS ===")
        print(f"Total productos: {len(productos)}")
        print()
        
        for producto in productos:
            id_prod, nombre, codigo_interno, codigo_barras = producto
            print(f"ID: {id_prod}")
            print(f"  Nombre: {nombre}")
            print(f"  Código Interno: {codigo_interno if codigo_interno else 'NULL'}")
            print(f"  Código Barras: {codigo_barras if codigo_barras else 'NULL'}")
            print()
        
        # Contar productos sin código interno
        cursor.execute("SELECT COUNT(*) FROM productos WHERE codigo_interno IS NULL")
        sin_codigo = cursor.fetchone()[0]
        
        print(f"Productos sin código interno: {sin_codigo}")
        
    except Exception as e:
        print(f"Error al verificar códigos internos: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_codigo_interno()