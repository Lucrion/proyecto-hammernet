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

print("PROBANDO ENDPOINTS DELETE")
print("=" * 60)

# Primero crear algunos elementos adicionales para poder eliminar
print("\nCreando elementos adicionales para probar DELETE...")

# Crear segunda categoría
categoria_data = {
    "nombre": "Electricidad",
    "descripcion": "Categoría de productos eléctricos"
}
test_endpoint("POST", "/categorias", categoria_data, "Crear segunda categoría")

# Crear segundo proveedor
proveedor_data = {
    "nombre": "Proveedor Eléctrico",
    "rut": "87654321-0",
    "razon_social": "Eléctricos S.A.",
    "sucursal": "Principal",
    "direccion": "Av. Eléctrica 789",
    "ciudad": "Valparaíso",
    "celular": "+56987654321",
    "correo": "contacto@electricos.com",
    "contacto": "María González",
    "telefono": "+56232654321"
}
test_endpoint("POST", "/proveedores", proveedor_data, "Crear segundo proveedor")

# Crear segundo producto
producto_data = {
    "nombre": "Cable Eléctrico",
    "descripcion": "Cable eléctrico 2.5mm",
    "precio": 5000,
    "categoria_id": 2,
    "proveedor_id": 2
}
test_endpoint("POST", "/productos", producto_data, "Crear segundo producto")

# Ahora probar eliminaciones
print("\n" + "=" * 60)
print("INICIANDO PRUEBAS DE ELIMINACIÓN")
print("=" * 60)

# 1. Eliminar producto
test_endpoint("DELETE", "/productos/2", description="Eliminar segundo producto")

# 2. Eliminar mensaje
test_endpoint("DELETE", "/mensajes/1", description="Eliminar mensaje de contacto")

# 3. Eliminar entrada de inventario
test_endpoint("DELETE", "/inventario/1", description="Eliminar entrada de inventario")

# 4. Intentar eliminar categoría (puede fallar si tiene productos asociados)
test_endpoint("DELETE", "/categorias/2", description="Eliminar segunda categoría")

# 5. Intentar eliminar proveedor (puede fallar si tiene productos asociados)
test_endpoint("DELETE", "/proveedores/2", description="Eliminar segundo proveedor")

# Verificar eliminaciones
print("\n" + "=" * 60)
print("VERIFICANDO ELIMINACIONES")
print("=" * 60)

test_endpoint("GET", "/productos", description="Verificar productos restantes")
test_endpoint("GET", "/mensajes", description="Verificar mensajes restantes")
test_endpoint("GET", "/inventario", description="Verificar inventario restante")
test_endpoint("GET", "/categorias", description="Verificar categorías restantes")
test_endpoint("GET", "/proveedores", description="Verificar proveedores restantes")

print("\n" + "=" * 60)
print("PRUEBAS DELETE COMPLETADAS")
print("=" * 60)