#!/usr/bin/env python3
import requests
import json

# URL del endpoint
url = "http://localhost:8000/api/productos/"

# Datos del producto de prueba
producto_data = {
    "nombre": "Producto Test",
    "descripcion": "Descripcion test",
    "id_categoria": 1,
    "precio_venta": 1000.0,
    "cantidad_actual": 10,
    "stock_minimo": 5,
    "costo_bruto": 500.0,
    "costo_neto": 500.0,
    "porcentaje_utilidad": 100.0,
    "utilidad_pesos": 500.0
}

# Headers
headers = {
    "Content-Type": "application/json"
}

try:
    print("Enviando solicitud POST...")
    print(f"URL: {url}")
    print(f"Datos: {json.dumps(producto_data, indent=2)}")
    
    response = requests.post(url, json=producto_data, headers=headers)
    
    print(f"\nRespuesta:")
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    if response.status_code == 200 or response.status_code == 201:
        print("✅ Producto creado exitosamente")
        print(f"Respuesta: {response.json()}")
    else:
        print("❌ Error al crear producto")
        try:
            error_data = response.json()
            print(f"Error: {json.dumps(error_data, indent=2)}")
        except:
            print(f"Error text: {response.text}")
            
except requests.exceptions.ConnectionError:
    print("❌ Error de conexión - El servidor no está disponible")
except Exception as e:
    print(f"❌ Error inesperado: {e}")