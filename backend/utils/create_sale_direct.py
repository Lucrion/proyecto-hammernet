#!/usr/bin/env python3
"""
Script para crear una venta directamente en la base de datos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from datetime import datetime
import os
from dotenv import load_dotenv

def create_sale_direct():
    """Crea una venta directamente en la base de datos"""
    
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
    
    print("Creando venta directamente en la base de datos...")
    print("=" * 50)
    
    with engine.connect() as conn:
        # Iniciar transacción
        trans = conn.begin()
        
        try:
            # Verificar usuario existe
            user_result = conn.execute(text("SELECT id_usuario, nombre FROM usuarios WHERE id_usuario = 7"))
            user = user_result.fetchone()
            if not user:
                print("❌ Usuario 7 no encontrado")
                return
            
            print(f"✅ Usuario encontrado: {user[1]} (ID: {user[0]})")
            
            # Verificar producto existe y tiene stock
            product_result = conn.execute(text("SELECT id_producto, nombre, cantidad_disponible, precio_venta FROM productos WHERE id_producto = 1"))
            product = product_result.fetchone()
            if not product:
                print("❌ Producto 1 no encontrado")
                return
            
            print(f"✅ Producto encontrado: {product[1]} (Stock: {product[2]}, Precio: ${product[3]})")
            
            if product[2] < 1:
                print("❌ Stock insuficiente")
                return
            
            # Crear la venta
            fecha_actual = datetime.now()
            total_venta = float(product[3])  # Precio del producto
            
            venta_result = conn.execute(text("""
                INSERT INTO ventas (id_usuario, fecha_venta, total_venta, estado, observaciones, fecha_creacion, fecha_actualizacion)
                VALUES (:id_usuario, :fecha_venta, :total_venta, :estado, :observaciones, :fecha_creacion, :fecha_actualizacion)
            """), {
                "id_usuario": user[0],
                "fecha_venta": fecha_actual,
                "total_venta": total_venta,
                "estado": "completada",
                "observaciones": "Venta creada directamente en BD - Prueba relación usuario-venta",
                "fecha_creacion": fecha_actual,
                "fecha_actualizacion": fecha_actual
            })
            
            # Obtener el ID de la venta creada
            venta_id = venta_result.lastrowid
            print(f"✅ Venta creada con ID: {venta_id}")
            
            # Crear el detalle de la venta
            subtotal = total_venta * 1  # cantidad = 1
            
            conn.execute(text("""
                INSERT INTO detalles_venta (id_venta, id_producto, cantidad, precio_unitario, subtotal, fecha_creacion)
                VALUES (:id_venta, :id_producto, :cantidad, :precio_unitario, :subtotal, :fecha_creacion)
            """), {
                "id_venta": venta_id,
                "id_producto": product[0],
                "cantidad": 1,
                "precio_unitario": total_venta,
                "subtotal": subtotal,
                "fecha_creacion": fecha_actual
            })
            
            print(f"✅ Detalle de venta creado")
            
            # Actualizar stock del producto
            nuevo_stock = product[2] - 1
            conn.execute(text("""
                UPDATE productos 
                SET cantidad_disponible = :nuevo_stock, fecha_actualizacion = :fecha_actualizacion
                WHERE id_producto = :id_producto
            """), {
                "nuevo_stock": nuevo_stock,
                "fecha_actualizacion": fecha_actual,
                "id_producto": product[0]
            })
            
            print(f"✅ Stock actualizado: {product[2]} → {nuevo_stock}")
            
            # Confirmar transacción
            trans.commit()
            
            print("\n" + "=" * 30)
            print("🎉 VENTA CREADA EXITOSAMENTE!")
            print(f"   ID Venta: {venta_id}")
            print(f"   Usuario: {user[1]} (ID: {user[0]})")
            print(f"   Producto: {product[1]}")
            print(f"   Total: ${total_venta}")
            print(f"   Fecha: {fecha_actual}")
            
            # Verificar la relación usuario-venta
            print("\n" + "=" * 30)
            print("Verificando relación usuario-venta:")
            
            result = conn.execute(text("""
                SELECT v.id_venta, v.total_venta, v.estado, v.fecha_venta,
                       u.nombre as usuario_nombre,
                       COUNT(dv.id_detalle) as num_detalles
                FROM ventas v
                JOIN usuarios u ON v.id_usuario = u.id_usuario
                LEFT JOIN detalles_venta dv ON v.id_venta = dv.id_venta
                WHERE v.id_venta = :venta_id
                GROUP BY v.id_venta, v.total_venta, v.estado, v.fecha_venta, u.nombre
            """), {"venta_id": venta_id})
            
            venta_info = result.fetchone()
            if venta_info:
                print(f"✅ Relación verificada:")
                print(f"   Venta ID: {venta_info[0]}")
                print(f"   Total: ${venta_info[1]}")
                print(f"   Estado: {venta_info[2]}")
                print(f"   Usuario: {venta_info[4]}")
                print(f"   Detalles: {venta_info[5]}")
            
        except Exception as e:
            trans.rollback()
            print(f"❌ Error creando venta: {e}")
            raise

if __name__ == "__main__":
    create_sale_direct()