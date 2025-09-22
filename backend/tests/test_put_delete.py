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

print("PROBANDO ENDPOINTS PUT Y DELETE")
print("=" * 60)

# 1. Actualizar producto
producto_update = {
    "nombre": "Martillo Actualizado",
    "descripcion": "Martillo de acero mejorado",
    "precio": 18000,  # Precio actualizado
    "categoria_id": 1,
    "proveedor_id": 1
}
test_endpoint("PUT", "/productos/1", producto_update, "Actualizar producto existente")

# 2. Actualizar categoría
categoria_update = {
    "nombre": "Herramientas Manuales",
    "descripcion": "Categoría de herramientas manuales actualizada"
}
test_endpoint("PUT", "/categorias/1", categoria_update, "Actualizar categoría existente")

# 3. Actualizar proveedor
proveedor_update = {
    "nombre": "Proveedor Test Actualizado",
    "rut": "12345678-9",
    "razon_social": "Proveedor Test S.A. Actualizado",
    "sucursal": "Principal",
    "direccion": "Calle Test 456",
    "ciudad": "Santiago",
    "celular": "+56912345679",
    "correo": "test.updated@proveedor.com",
    "contacto": "Juan Pérez Actualizado",
    "telefono": "+56212345679"
}
test_endpoint("PUT", "/proveedores/1", proveedor_update, "Actualizar proveedor existente")

# 4. Actualizar inventario
inventario_update = {
    "id_producto": 1,
    "cantidad": 15,  # Cantidad actualizada
    "precio": 18000,  # Precio actualizado
    "stock_minimo": 8
}
test_endpoint("PUT", "/inventario/1", inventario_update, "Actualizar entrada de inventario")

# 5. Marcar mensaje como leído
test_endpoint("PUT", "/mensajes/1/leido", description="Marcar mensaje como leído")

# 6. Verificar cambios
test_endpoint("GET", "/productos/1", description="Verificar producto actualizado")
test_endpoint("GET", "/categorias/1", description="Verificar categoría actualizada")
test_endpoint("GET", "/inventario", description="Verificar inventario actualizado")
test_endpoint("GET", "/mensajes/1", description="Verificar mensaje marcado como leído")

print("\n" + "=" * 60)
print("PRUEBAS PUT COMPLETADAS")
print("=" * 60)