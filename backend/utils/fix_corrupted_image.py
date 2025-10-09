#!/usr/bin/env python3
import sqlite3

def fix_corrupted_image():
    try:
        # Conectar a la base de datos SQLite
        conn = sqlite3.connect('ferreteria.db')
        cursor = conn.cursor()
        
        print("=== CORRIGIENDO IMAGEN CORRUPTA ===")
        
        # Verificar el producto con imagen corrupta
        cursor.execute("""
            SELECT id_producto, nombre, imagen_url 
            FROM productos 
            WHERE id_producto = 2
        """)
        
        producto = cursor.fetchone()
        if producto:
            print(f"Producto encontrado: {producto[1]} (ID: {producto[0]})")
            print(f"Imagen actual: {len(str(producto[2]))} caracteres")
            
            # Limpiar la imagen corrupta
            cursor.execute("""
                UPDATE productos 
                SET imagen_url = NULL 
                WHERE id_producto = 2
            """)
            
            conn.commit()
            print("✅ Imagen corrupta limpiada exitosamente")
            
            # Verificar el cambio
            cursor.execute("""
                SELECT id_producto, nombre, imagen_url 
                FROM productos 
                WHERE id_producto = 2
            """)
            
            producto_actualizado = cursor.fetchone()
            print(f"Estado después de la corrección:")
            print(f"  - Nombre: {producto_actualizado[1]}")
            print(f"  - Imagen URL: {producto_actualizado[2] or 'NULL (corregido)'}")
            
        else:
            print("Producto no encontrado")
        
        conn.close()
        
    except Exception as e:
        print(f"Error al corregir la imagen: {e}")

if __name__ == "__main__":
    fix_corrupted_image()