#!/usr/bin/env python3
"""
Script para probar el login con credenciales corregidas y el endpoint de usuarios
"""
import requests
import json

API_URL = "http://localhost:8000/api"

def test_login_and_users():
    """Probar el login y luego el endpoint de usuarios"""
    print("=== PROBANDO LOGIN CON CREDENCIALES CORREGIDAS ===")
    
    # Datos de login
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        # Hacer login
        response = requests.post(
            f"{API_URL}/auth/login",
            data=login_data,  # OAuth2PasswordRequestForm espera form data
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"Login Status Code: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get('access_token')
            print(f"✓ Login exitoso!")
            print(f"Token obtenido: {token[:50]}..." if token else "No token")
            print(f"Usuario: {token_data.get('nombre')} ({token_data.get('username')})")
            
            # Ahora probar el endpoint de usuarios
            print("\n=== PROBANDO ENDPOINT DE USUARIOS CON TOKEN ===")
            
            headers = {"Authorization": f"Bearer {token}"}
            users_response = requests.get(f"{API_URL}/usuarios/", headers=headers)
            
            print(f"Usuarios Status Code: {users_response.status_code}")
            
            if users_response.status_code == 200:
                usuarios = users_response.json()
                print(f"✓ Usuarios obtenidos exitosamente!")
                print(f"Número de usuarios: {len(usuarios)}")
                
                for usuario in usuarios:
                    print(f"- ID: {usuario.get('id_usuario')}")
                    print(f"  Nombre: {usuario.get('nombre')}")
                    print(f"  Username: {usuario.get('username')}")
                    print(f"  Rol: {usuario.get('role')}")
                    print(f"  Activo: {usuario.get('activo')}")
                    print()
            else:
                print(f"✗ Error al obtener usuarios: {users_response.text}")
                
        else:
            print(f"✗ Error en login: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_login_and_users()