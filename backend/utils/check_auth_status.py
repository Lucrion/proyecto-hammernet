#!/usr/bin/env python3
"""
Script para verificar el estado de autenticación y probar el endpoint de usuarios
"""
import requests
import json

API_URL = "http://localhost:8000/api"

def test_login():
    """Probar el login con credenciales de prueba"""
    print("=== PROBANDO LOGIN ===")
    
    # Datos de login (usando credenciales típicas de admin)
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            data=login_data,  # OAuth2PasswordRequestForm espera form data
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            token_data = response.json()
            print(f"Token obtenido: {token_data.get('access_token', 'No token')[:50]}...")
            return token_data.get('access_token')
        else:
            print("Error en login")
            return None
            
    except Exception as e:
        print(f"Error al hacer login: {e}")
        return None

def test_usuarios_endpoint(token=None):
    """Probar el endpoint de usuarios"""
    print("\n=== PROBANDO ENDPOINT DE USUARIOS ===")
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        print("Usando token de autenticación")
    else:
        print("Sin token de autenticación")
    
    try:
        response = requests.get(f"{API_URL}/usuarios/", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            usuarios = response.json()
            print(f"Número de usuarios encontrados: {len(usuarios)}")
            for usuario in usuarios:
                print(f"- ID: {usuario.get('id_usuario')}, Nombre: {usuario.get('nombre')}, Username: {usuario.get('username')}")
        
    except Exception as e:
        print(f"Error al obtener usuarios: {e}")

def check_database_users():
    """Verificar usuarios en la base de datos directamente"""
    print("\n=== VERIFICANDO USUARIOS EN BASE DE DATOS ===")
    
    import sqlite3
    
    try:
        conn = sqlite3.connect('ferreteria.db')
        cursor = conn.cursor()
        
        # Obtener todos los usuarios
        cursor.execute("SELECT id_usuario, nombre, username, activo FROM usuarios")
        usuarios = cursor.fetchall()
        
        print(f"Usuarios en base de datos: {len(usuarios)}")
        for usuario in usuarios:
            print(f"- ID: {usuario[0]}, Nombre: {usuario[1]}, Username: {usuario[2]}, Activo: {usuario[3]}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error al verificar base de datos: {e}")

if __name__ == "__main__":
    # Verificar usuarios en base de datos
    check_database_users()
    
    # Probar login
    token = test_login()
    
    # Probar endpoint de usuarios sin token
    test_usuarios_endpoint()
    
    # Probar endpoint de usuarios con token
    if token:
        test_usuarios_endpoint(token)