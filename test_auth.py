#!/usr/bin/env python3
import requests
import json

# URL del endpoint de login
login_url = "http://localhost:8000/api/auth/login"

# Credenciales de prueba (formato form-data para OAuth2PasswordRequestForm)
credentials = {
    "username": "admin",
    "password": "123"
}

# Headers para form-data
headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}

try:
    print("Probando autenticación...")
    print(f"URL: {login_url}")
    print(f"Credenciales: {json.dumps(credentials, indent=2)}")
    
    response = requests.post(login_url, data=credentials, headers=headers)
    
    print(f"\nRespuesta de login:")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Login exitoso")
        data = response.json()
        token = data.get('access_token')
        print(f"Token obtenido: {token[:50]}..." if token else "No token")
        
        # Probar crear producto con token
        if token:
            print("\n--- Probando crear producto con token ---")
            producto_url = "http://localhost:8000/api/productos/"
            
            producto_data = {
                "nombre": "Producto Test Auth",
                "descripcion": "Descripcion test con auth",
                "id_categoria": 1,
                "precio_venta": 2000.0,
                "cantidad_actual": 15,
                "stock_minimo": 5,
                "costo_bruto": 1000.0,
                "costo_neto": 1000.0,
                "porcentaje_utilidad": 100.0,
                "utilidad_pesos": 1000.0
            }
            
            auth_headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
            
            producto_response = requests.post(producto_url, json=producto_data, headers=auth_headers)
            
            print(f"Status Code: {producto_response.status_code}")
            if producto_response.status_code == 200 or producto_response.status_code == 201:
                print("✅ Producto creado exitosamente con autenticación")
                print(f"Respuesta: {producto_response.json()}")
            else:
                print("❌ Error al crear producto")
                try:
                    error_data = producto_response.json()
                    print(f"Error: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"Error text: {producto_response.text}")
    else:
        print("❌ Error en login")
        try:
            error_data = response.json()
            print(f"Error: {json.dumps(error_data, indent=2)}")
        except:
            print(f"Error text: {response.text}")
            
except requests.exceptions.ConnectionError:
    print("❌ Error de conexión - El servidor no está disponible")
except Exception as e:
    print(f"❌ Error inesperado: {e}")