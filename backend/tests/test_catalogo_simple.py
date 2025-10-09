import requests
import json

try:
    response = requests.get('http://localhost:8000/api/productos/catalogo')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Productos en catálogo: {len(data)}")
        for producto in data:
            print(f"- {producto['nombre']} (ID: {producto['id_producto']})")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {e}")