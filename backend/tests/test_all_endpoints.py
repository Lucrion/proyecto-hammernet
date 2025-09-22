import requests
import json
from datetime import datetime

# Configuración base
BASE_URL = "http://localhost:8000"
headers = {"Content-Type": "application/json"}

def obtener_token():
    """Obtiene token de autenticación"""
    print("\n=== OBTENIENDO TOKEN DE AUTENTICACIÓN ===")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", data=login_data)
        if response.status_code == 200:
            token_data = response.json()
            print(f"✅ Token obtenido exitosamente")
            return token_data["access_token"]
        else:
            print(f"❌ Error al obtener token: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def test_endpoint(method, endpoint, data=None, token=None, description=""):
    """Función genérica para probar endpoints"""
    url = f"{BASE_URL}{endpoint}"
    headers_with_auth = headers.copy()
    
    if token:
        headers_with_auth["Authorization"] = f"Bearer {token}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers_with_auth)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers_with_auth)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers_with_auth)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers_with_auth)
        
        status = "✅" if 200 <= response.status_code < 300 else "❌"
        print(f"{status} {method} {endpoint} - {response.status_code} - {description}")
        
        if response.status_code >= 400:
            print(f"   Error: {response.text}")
        
        return response
    except Exception as e:
        print(f"❌ {method} {endpoint} - Error de conexión: {e}")
        return None

def main():
    print("=== PRUEBA COMPLETA DE ENDPOINTS CRUD ===")
    
    # Obtener token
    token = obtener_token()
    if not token:
        print("No se pudo obtener el token. Abortando pruebas.")
        return
    
    # Test Health Check
    print("\n=== HEALTH CHECK ===")
    test_endpoint("GET", "/health", description="Health check")
    
    # Test Categorías CRUD
    print("\n=== CATEGORÍAS CRUD ===")
    test_endpoint("GET", "/categorias", token=token, description="Listar categorías")
    test_endpoint("GET", "/categorias/1", token=token, description="Obtener categoría por ID")
    
    nueva_categoria = {
        "nombre": "Categoría Test",
        "descripcion": "Categoría de prueba"
    }
    response = test_endpoint("POST", "/categorias", nueva_categoria, token, "Crear categoría")
    categoria_id = None
    if response and response.status_code == 200:
        categoria_id = response.json().get("id_categoria")
    
    if categoria_id:
        actualizar_categoria = {
            "nombre": "Categoría Test Actualizada",
            "descripcion": "Descripción actualizada"
        }
        test_endpoint("PUT", f"/categorias/{categoria_id}", actualizar_categoria, token, "Actualizar categoría")
        test_endpoint("DELETE", f"/categorias/{categoria_id}", token=token, description="Eliminar categoría")
    
    # Test Proveedores CRUD
    print("\n=== PROVEEDORES CRUD ===")
    test_endpoint("GET", "/proveedores", token=token, description="Listar proveedores")
    test_endpoint("GET", "/proveedores/1", token=token, description="Obtener proveedor por ID")
    
    nuevo_proveedor = {
        "nombre": "Proveedor Test",
        "contacto": "Juan Pérez",
        "telefono": "+1-555-9999",
        "direccion": "Dirección de prueba"
    }
    response = test_endpoint("POST", "/proveedores", nuevo_proveedor, token, "Crear proveedor")
    proveedor_id = None
    if response and response.status_code == 200:
        proveedor_id = response.json().get("id_proveedor")
    
    if proveedor_id:
        actualizar_proveedor = {
            "nombre": "Proveedor Test Actualizado",
            "contacto": "María García",
            "telefono": "+1-555-8888",
            "direccion": "Nueva dirección"
        }
        test_endpoint("PUT", f"/proveedores/{proveedor_id}", actualizar_proveedor, token, "Actualizar proveedor")
        test_endpoint("DELETE", f"/proveedores/{proveedor_id}", token=token, description="Eliminar proveedor")
    
    # Test Productos CRUD
    print("\n=== PRODUCTOS CRUD ===")
    test_endpoint("GET", "/productos", token=token, description="Listar productos")
    test_endpoint("GET", "/productos/1", token=token, description="Obtener producto por ID")
    
    nuevo_producto = {
        "nombre": "Producto Test",
        "descripcion": "Descripción del producto test",
        "precio": 199.99,
        "stock": 50,
        "id_categoria": 1
    }
    response = test_endpoint("POST", "/productos", nuevo_producto, token, "Crear producto")
    producto_id = None
    if response and response.status_code == 200:
        producto_id = response.json().get("id")
    
    if producto_id:
        actualizar_producto = {
            "nombre": "Producto Test Actualizado",
            "descripcion": "Descripción actualizada",
            "precio": 299.99,
            "stock": 75
        }
        test_endpoint("PUT", f"/productos/{producto_id}", actualizar_producto, token, "Actualizar producto")
        test_endpoint("DELETE", f"/productos/{producto_id}", token=token, description="Eliminar producto")
    
    # Test Inventario CRUD
    print("\n=== INVENTARIO CRUD ===")
    test_endpoint("GET", "/inventario", token=token, description="Listar inventario")
    test_endpoint("GET", "/inventario/1", token=token, description="Obtener inventario por ID")
    
    nuevo_inventario = {
        "id_producto": 1,
        "cantidad_disponible": 100,
        "cantidad_minima": 10,
        "ubicacion": "Almacén A-1"
    }
    response = test_endpoint("POST", "/inventario", nuevo_inventario, token, "Crear inventario")
    inventario_id = None
    if response and response.status_code == 200:
        inventario_id = response.json().get("id_inventario")
    
    if inventario_id:
        actualizar_inventario = {
            "cantidad_disponible": 150,
            "cantidad_minima": 15,
            "ubicacion": "Almacén B-2"
        }
        test_endpoint("PUT", f"/inventario/{inventario_id}", actualizar_inventario, token, "Actualizar inventario")
        test_endpoint("DELETE", f"/inventario/{inventario_id}", token=token, description="Eliminar inventario")
    
    # Test Movimientos de Inventario CRUD
    print("\n=== MOVIMIENTOS DE INVENTARIO CRUD ===")
    test_endpoint("GET", "/movimientos-inventario", token=token, description="Listar movimientos")
    test_endpoint("GET", "/movimientos-inventario/1", token=token, description="Obtener movimiento por ID")
    
    nuevo_movimiento = {
        "id_producto": 1,
        "tipo_movimiento": "entrada",
        "cantidad": 50,
        "motivo": "Reposición de stock",
        "fecha_movimiento": datetime.now().isoformat()
    }
    response = test_endpoint("POST", "/movimientos-inventario", nuevo_movimiento, token, "Crear movimiento")
    movimiento_id = None
    if response and response.status_code == 200:
        movimiento_id = response.json().get("id_movimiento")
    
    if movimiento_id:
        actualizar_movimiento = {
            "motivo": "Reposición de stock actualizada",
            "cantidad": 75
        }
        test_endpoint("PUT", f"/movimientos-inventario/{movimiento_id}", actualizar_movimiento, token, "Actualizar movimiento")
        test_endpoint("DELETE", f"/movimientos-inventario/{movimiento_id}", token=token, description="Eliminar movimiento")
    
    # Test Usuarios CRUD
    print("\n=== USUARIOS CRUD ===")
    test_endpoint("GET", "/usuarios", token=token, description="Listar usuarios")
    test_endpoint("GET", "/usuarios/1", token=token, description="Obtener usuario por ID")
    
    nuevo_usuario = {
        "nombre": "Usuario Test",
        "username": "usertest",
        "password": "password123",
        "role": "empleado"
    }
    response = test_endpoint("POST", "/usuarios", nuevo_usuario, token, "Crear usuario")
    usuario_id = None
    if response and response.status_code == 200:
        usuario_id = response.json().get("id")
    
    if usuario_id:
        actualizar_usuario = {
            "nombre": "Usuario Test Actualizado",
            "role": "administrador"
        }
        test_endpoint("PUT", f"/usuarios/{usuario_id}", actualizar_usuario, token, "Actualizar usuario")
        test_endpoint("DELETE", f"/usuarios/{usuario_id}", token=token, description="Eliminar usuario")
    
    # Test Mensajes CRUD
    print("\n=== MENSAJES CRUD ===")
    test_endpoint("GET", "/mensajes", token=token, description="Listar mensajes")
    
    nuevo_mensaje = {
        "nombre": "Juan Pérez",
        "email": "juan@example.com",
        "telefono": "+1-555-1234",
        "mensaje": "Este es un mensaje de prueba"
    }
    response = test_endpoint("POST", "/mensajes", nuevo_mensaje, description="Crear mensaje (sin auth)")
    mensaje_id = None
    if response and response.status_code == 200:
        mensaje_id = response.json().get("id")
    
    if mensaje_id:
        test_endpoint("PUT", f"/mensajes/{mensaje_id}/leer", token=token, description="Marcar mensaje como leído")
        test_endpoint("DELETE", f"/mensajes/{mensaje_id}", token=token, description="Eliminar mensaje")
    
    print("\n=== PRUEBAS COMPLETADAS ===")

if __name__ == "__main__":
    main()