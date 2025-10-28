#!/usr/bin/env python3
"""
Script para probar la creación de ventas con usuarios y productos existentes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
from datetime import datetime

def test_sale_creation():
    """Prueba la creación de una venta usando la API"""
    
    # URL base de la API
    base_url = "http://localhost:8000/api"
    
    print("Probando creación de venta...")
    print("=" * 50)
    
    # Datos de la venta de prueba
    # Usuario ID 7 (Jhan) y Producto ID 1 (Martillo) que tiene stock 133
    venta_data = {
        "id_usuario": 7,
        "total_venta": 2000.00,
        "estado": "completada",
        "observaciones": "Venta de prueba desde script",
        "detalles": [
            {
                "id_producto": 1,
                "cantidad": 1,
                "precio_unitario": 2000.00
            }
        ]
    }
    
    print("Datos de la venta:")
    print(json.dumps(venta_data, indent=2, ensure_ascii=False))
    print("\n" + "=" * 30)
    
    try:
        # Realizar la petición POST
        response = requests.post(
            f"{base_url}/ventas/",
            json=venta_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200 or response.status_code == 201:
            print("✅ VENTA CREADA EXITOSAMENTE!")
            response_data = response.json()
            print("Respuesta del servidor:")
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
            
            # Verificar que se guardó en la base de datos
            print("\n" + "=" * 30)
            print("Verificando en base de datos...")
            verify_sale_in_db(response_data.get('id_venta'))
            
        else:
            print("❌ ERROR AL CREAR LA VENTA")
            print(f"Respuesta del servidor: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se pudo conectar al servidor")
        print("Asegúrate de que el backend esté ejecutándose en http://localhost:8000")
    except Exception as e:
        print(f"❌ ERROR INESPERADO: {e}")

def verify_sale_in_db(venta_id=None):
    """Verifica que la venta se haya guardado en la base de datos"""
    
    from sqlalchemy import create_engine, text
    from dotenv import load_dotenv
    
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
    
    with engine.connect() as conn:
        # Contar ventas totales
        ventas_count = conn.execute(text("SELECT COUNT(*) FROM ventas")).fetchone()[0]
        detalles_count = conn.execute(text("SELECT COUNT(*) FROM detalles_venta")).fetchone()[0]
        
        print(f"Total ventas en BD: {ventas_count}")
        print(f"Total detalles en BD: {detalles_count}")
        
        if venta_id:
            # Verificar la venta específica
            result = conn.execute(text("SELECT * FROM ventas WHERE id_venta = :id"), {"id": venta_id})
            venta = result.fetchone()
            if venta:
                print(f"✅ Venta {venta_id} encontrada en BD")
                print(f"   Usuario: {venta[1]}, Total: ${venta[3]}, Estado: {venta[4]}")
            else:
                print(f"❌ Venta {venta_id} NO encontrada en BD")
        
        # Mostrar últimas ventas
        print("\nÚltimas ventas:")
        result = conn.execute(text("SELECT id_venta, id_usuario, total_venta, estado, fecha_venta FROM ventas ORDER BY fecha_venta DESC LIMIT 3"))
        ventas = result.fetchall()
        for venta in ventas:
            print(f"  ID: {venta[0]}, Usuario: {venta[1]}, Total: ${venta[2]}, Estado: {venta[3]}, Fecha: {venta[4]}")

if __name__ == "__main__":
    test_sale_creation()