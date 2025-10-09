#!/usr/bin/env python3
import requests
import json

def test_catalogo_endpoint():
    try:
        print("Probando endpoint del catálogo...")
        response = requests.get('http://localhost:8000/api/productos/catalogo')
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Número de productos en catálogo: {len(data)}")
            print("Productos encontrados:")
            for i, producto in enumerate(data, 1):
                print(f"{i}. {producto.get('nombre', 'Sin nombre')}")
                print(f"   ID: {producto.get('id_producto', 'N/A')}")
                print(f"   Descripción: {producto.get('descripcion', 'Sin descripción')}")
                print(f"   Marca: {producto.get('marca', 'Sin marca')}")
                print(f"   Imagen: {producto.get('imagen_url', 'Sin imagen')}")
                print(f"   Características: {producto.get('caracteristicas', 'Sin características')}")
                print("   ---")
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Error: No se pudo conectar al servidor. ¿Está ejecutándose en localhost:8000?")
    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":
    test_catalogo_endpoint()