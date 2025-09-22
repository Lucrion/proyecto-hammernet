import requests
import json

# Configuración
BASE_URL = "http://localhost:8000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0IiwiZXhwIjoxNzU3MzcxMjIzfQ.kimAm90TKGXw1etzDiRYUh5cWyPV92-exy1r3f4HPkA"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_endpoint(method, endpoint, data=None, description=""):
    """Función para probar un endpoint"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n{'='*60}")
    print(f"Probando: {method} {endpoint}")
    print(f"Descripción: {description}")
    print(f"{'='*60}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=HEADERS)
        elif method == "POST":
            response = requests.post(url, headers=HEADERS, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=HEADERS, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=HEADERS)
        
        print(f"Status Code: {response.status_code}")
        
        try:
            response_json = response.json()
            print(f"Response: {json.dumps(response_json, indent=2, ensure_ascii=False)}")
        except:
            print(f"Response (text): {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

# Probar endpoints principales
print("INICIANDO PRUEBAS DE ENDPOINTS")
print("=" * 60)

# 1. Health check
test_endpoint("GET", "/health", description="Verificar estado del servidor")

# 2. Usuarios
test_endpoint("GET", "/usuarios", description="Obtener lista de usuarios")
test_endpoint("GET", "/usuarios/1", description="Obtener usuario específico")

# 3. Categorías
test_endpoint("GET", "/categorias", description="Obtener lista de categorías")

# 4. Proveedores
test_endpoint("GET", "/proveedores", description="Obtener lista de proveedores")

# 5. Productos
test_endpoint("GET", "/productos", description="Obtener lista de productos")

# 6. Inventario
test_endpoint("GET", "/inventario", description="Obtener inventario")

# 7. Catálogo-Inventario
test_endpoint("GET", "/catalogo-inventario", description="Obtener catálogo con inventario")

# 8. Mensajes
test_endpoint("GET", "/mensajes", description="Obtener mensajes de contacto")

print("\n" + "=" * 60)
print("PRUEBAS COMPLETADAS")
print("=" * 60)