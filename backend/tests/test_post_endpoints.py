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

print("PROBANDO ENDPOINTS DE CREACIÓN")
print("=" * 60)

# 1. Crear categoría
categoria_data = {
    "nombre": "Herramientas",
    "descripcion": "Categoría de herramientas"
}
test_endpoint("POST", "/categorias", categoria_data, "Crear nueva categoría")

# 2. Crear proveedor
proveedor_data = {
    "nombre": "Proveedor Test",
    "rut": "12345678-9",
    "razon_social": "Proveedor Test S.A.",
    "sucursal": "Principal",
    "direccion": "Calle Test 123",
    "ciudad": "Santiago",
    "celular": "+56912345678",
    "correo": "test@proveedor.com",
    "contacto": "Juan Pérez",
    "telefono": "+56212345678"
}
test_endpoint("POST", "/proveedores", proveedor_data, "Crear nuevo proveedor")

# 3. Crear producto (verificar que precio sea entero)
producto_data = {
    "nombre": "Martillo",
    "descripcion": "Martillo de acero",
    "precio": 15000,  # Entero, no decimal
    "categoria_id": 1,
    "proveedor_id": 1
}
test_endpoint("POST", "/productos", producto_data, "Crear nuevo producto con precio entero")

# 4. Crear inventario (verificar que precio sea entero)
inventario_data = {
    "producto_id": 1,
    "cantidad": 10,
    "precio": 15000,  # Entero, no decimal
    "stock_minimo": 5
}
test_endpoint("POST", "/inventario", inventario_data, "Crear entrada de inventario con precio entero")

# 5. Crear mensaje de contacto (no requiere autenticación)
mensaje_data = {
    "nombre": "Cliente Test",
    "email": "cliente@test.com",
    "telefono": "+56912345678",
    "mensaje": "Mensaje de prueba desde curl"
}
test_endpoint("POST", "/mensajes", mensaje_data, "Crear mensaje de contacto")

print("\n" + "=" * 60)
print("PRUEBAS DE CREACIÓN COMPLETADAS")
print("=" * 60)