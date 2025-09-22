#!/usr/bin/env python3
import sqlite3

def update_codigo_interno():
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect('ferreteria.db')
        cursor = conn.cursor()
        
        # Obtener todos los productos sin código interno
        cursor.execute("""
            SELECT id_producto, nombre
            FROM productos
            WHERE codigo_interno IS NULL
            ORDER BY id_producto
        """)
        
        productos = cursor.fetchall()
        
        if not productos:
            print("No hay productos sin código interno")
            return
        
        print(f"Actualizando códigos internos para {len(productos)} productos...")
        
        # Generar códigos internos únicos
        for i, (id_producto, nombre) in enumerate(productos, 1):
            # Generar código interno: PROD + número de 4 dígitos
            codigo_interno = f"PROD{i:04d}"
            
            # Actualizar el producto
            cursor.execute(
                "UPDATE productos SET codigo_interno = ? WHERE id_producto = ?",
                (codigo_interno, id_producto)
            )
            
            print(f"Producto {id_producto} ({nombre}): {codigo_interno}")
        
        conn.commit()
        print(f"\n✅ Se actualizaron {len(productos)} productos exitosamente")
        
        # Verificar los cambios
        cursor.execute("""
            SELECT id_producto, nombre, codigo_interno
            FROM productos
            WHERE codigo_interno IS NOT NULL
            ORDER BY id_producto
        """)
        
        productos_actualizados = cursor.fetchall()
        
        print("\n=== PRODUCTOS CON CÓDIGO INTERNO ACTUALIZADO ===")
        for producto in productos_actualizados:
            id_prod, nombre, codigo_interno = producto
            print(f"ID: {id_prod} | Nombre: {nombre} | Código: {codigo_interno}")
        
    except Exception as e:
        print(f"Error al actualizar códigos internos: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    update_codigo_interno()