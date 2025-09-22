import requests
import json

# URL base de la API
API_URL = "http://localhost:8000"

# Función para obtener un token de autenticación
def obtener_token():
    # OAuth2 espera los datos como form-data, no como JSON
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        # Enviar como form-data, no como JSON
        response = requests.post(f"{API_URL}/login", data=login_data)
        if response.status_code == 200:
            token_data = response.json()
            return token_data.get("access_token")
        else:
            print(f"Error al obtener token: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"Error de conexión: {e}")
        return None

# Función para crear un producto
def crear_producto(token):
    if not token:
        print("No se pudo obtener un token válido")
        return
    
    # Datos del producto según el modelo ProductoCreate
    producto_data = {
        "nombre": "Producto de prueba",
        "descripcion": "Descripción del producto de prueba",
        "precio": 99.99,
        "stock": 10,
        "id_categoria": 1  # Asegúrate de que esta categoría exista
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    try:
        print("Enviando datos del producto:", json.dumps(producto_data, indent=2))
        response = requests.post(f"{API_URL}/productos", json=producto_data, headers=headers)
        
        print(f"Código de respuesta: {response.status_code}")
        print("Respuesta:", response.text)
        
        if response.status_code == 200 or response.status_code == 201:
            print("Producto creado exitosamente")
            return response.json()
        else:
            print("Error al crear el producto")
            return None
    except Exception as e:
        print(f"Error de conexión: {e}")
        return None

# Ejecutar las pruebas
if __name__ == "__main__":
    print("Obteniendo token de autenticación...")
    token = obtener_token()
    
    if token:
        print(f"Token obtenido: {token[:10]}...")
        print("\nCreando producto de prueba...")
        producto = crear_producto(token)
        
        if producto:
            print("\nProducto creado:")
            print(json.dumps(producto, indent=2))
    else:
        print("No se pudo obtener un token. Verifica las credenciales o la conexión al servidor.")