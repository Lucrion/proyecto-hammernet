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
    if data:
        print(f"Datos: {json.dumps(data, indent=2, ensure_ascii=False)}")
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

print("CORRIGIENDO ENDPOINTS QUE FALLARON")
print("=" * 60)

# 1. Crear inventario con el campo correcto
inventario_data = {
    "id_producto": 1,  # Cambié de producto_id a id_producto
    "cantidad": 10,
    "precio": 15000,
    "stock_minimo": 5
}
test_endpoint("POST", "/inventario", inventario_data, "Crear entrada de inventario (corregido)")

# 2. Crear mensaje con todos los campos requeridos
mensaje_data = {
    "nombre": "Cliente",
    "apellido": "Test",  # Campo requerido
    "email": "cliente@test.com",
    "telefono": "+56912345678",
    "asunto": "Consulta de prueba",  # Campo requerido
    "mensaje": "Mensaje de prueba desde curl"
}
test_endpoint("POST", "/mensajes", mensaje_data, "Crear mensaje de contacto (corregido)")

# 3. Verificar que los datos se crearon correctamente
test_endpoint("GET", "/inventario", description="Verificar inventario creado")
test_endpoint("GET", "/mensajes", description="Verificar mensaje creado")
test_endpoint("GET", "/catalogo-inventario", description="Verificar catálogo actualizado")

print("\n" + "=" * 60)
print("CORRECCIONES COMPLETADAS")
print("=" * 60)