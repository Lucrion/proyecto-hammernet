#!/usr/bin/env python3
import sqlite3
from datetime import datetime

def create_inventario_data():
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect('ferreteria.db')
        cursor = conn.cursor()
        
        # Verificar si ya hay datos de inventario
        cursor.execute("SELECT COUNT(*) FROM inventario")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"Ya existen {count} registros de inventario")
            return
        
        # Obtener productos existentes
        cursor.execute("SELECT id_producto, nombre FROM productos LIMIT 5")
        productos = cursor.fetchall()
        
        if not productos:
            print("No hay productos en la base de datos")
            return
        
        # Crear registros de inventario para los primeros productos
        inventario_data = [
            (productos[0][0], 50, 1840.00, datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            (productos[1][0], 30, 2200.00, datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            (productos[2][0], 25, 1500.00, datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ]
        
        # Insertar datos de inventario
        cursor.executemany(
            "INSERT INTO inventario (id_producto, cantidad, precio, fecha_registro) VALUES (?, ?, ?, ?)",
            inventario_data
        )
        
        conn.commit()
        print(f"Se crearon {len(inventario_data)} registros de inventario exitosamente")
        
        # Mostrar los registros creados
        cursor.execute("""
            SELECT i.id_inventario, p.nombre, i.cantidad, i.precio, i.fecha_registro
            FROM inventario i
            JOIN productos p ON i.id_producto = p.id_producto
        """)
        
        registros = cursor.fetchall()
        print("\nRegistros de inventario creados:")
        for registro in registros:
            print(f"ID: {registro[0]}, Producto: {registro[1]}, Cantidad: {registro[2]}, Precio: ${registro[3]}, Fecha: {registro[4]}")
        
    except Exception as e:
        print(f"Error al crear datos de inventario: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_inventario_data()