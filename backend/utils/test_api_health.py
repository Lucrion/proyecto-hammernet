#!/usr/bin/env python3
"""
Script para probar la salud de la API y debuggear conexiones
"""

import requests
import json

def test_api_health():
    """Prueba la salud de la API"""
    
    base_url = "http://localhost:8000"
    
    print("Probando conexión a la API...")
    print("=" * 50)
    
    # Probar endpoint de salud
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        print(f"Health Check - Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ API funcionando: {response.json()}")
        else:
            print(f"❌ API con problemas: {response.text}")
    except Exception as e:
        print(f"❌ Error conectando a /api/health: {e}")
    
    # Probar endpoint de usuarios
    try:
        response = requests.get(f"{base_url}/api/usuarios/7", timeout=5)
        print(f"\nUsuario 7 - Status: {response.status_code}")
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Usuario encontrado: {user_data.get('nombre', 'N/A')}")
        else:
            print(f"❌ Usuario no encontrado: {response.text}")
    except Exception as e:
        print(f"❌ Error consultando usuario: {e}")
    
    # Probar endpoint de productos
    try:
        response = requests.get(f"{base_url}/api/productos/1", timeout=5)
        print(f"\nProducto 1 - Status: {response.status_code}")
        if response.status_code == 200:
            product_data = response.json()
            print(f"✅ Producto encontrado: {product_data.get('nombre', 'N/A')}")
            print(f"   Stock: {product_data.get('cantidad_disponible', 'N/A')}")
        else:
            print(f"❌ Producto no encontrado: {response.text}")
    except Exception as e:
        print(f"❌ Error consultando producto: {e}")
    
    # Probar endpoint de ventas con GET
    try:
        response = requests.get(f"{base_url}/api/ventas/", timeout=5)
        print(f"\nListar ventas - Status: {response.status_code}")
        if response.status_code == 200:
            ventas = response.json()
            print(f"✅ Endpoint ventas funciona. Total ventas: {len(ventas)}")
        else:
            print(f"❌ Error listando ventas: {response.text}")
    except Exception as e:
        print(f"❌ Error consultando ventas: {e}")

if __name__ == "__main__":
    test_api_health()