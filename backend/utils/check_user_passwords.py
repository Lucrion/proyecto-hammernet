#!/usr/bin/env python3
"""
Script para verificar las contraseñas de los usuarios en la base de datos
"""
import sqlite3
from passlib.context import CryptContext

# Configurar el contexto de contraseñas (debe coincidir con el del backend)
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def verificar_contraseñas():
    """Verificar las contraseñas de los usuarios en la base de datos"""
    print("=== VERIFICANDO CONTRASEÑAS DE USUARIOS ===")
    
    try:
        conn = sqlite3.connect('ferreteria.db')
        cursor = conn.cursor()
        
        # Obtener todos los usuarios con sus contraseñas
        cursor.execute("SELECT id_usuario, nombre, username, password, activo FROM usuarios")
        usuarios = cursor.fetchall()
        
        print(f"Usuarios en base de datos: {len(usuarios)}")
        
        for usuario in usuarios:
            id_usuario, nombre, username, password_hash, activo = usuario
            print(f"\n--- Usuario ID: {id_usuario} ---")
            print(f"Nombre: {nombre}")
            print(f"Username: {username}")
            print(f"Activo: {activo}")
            print(f"Hash de contraseña: {password_hash[:50]}..." if len(password_hash) > 50 else f"Hash de contraseña: {password_hash}")
            
            # Probar contraseñas comunes
            contraseñas_prueba = ["admin", "admin123", "123456", "password", username]
            
            for contraseña in contraseñas_prueba:
                try:
                    # Verificar PBKDF2-SHA256
                    if password_hash.startswith("$pbkdf2-sha256$"):
                        if pwd_context.verify(contraseña, password_hash):
                            print(f"✓ Contraseña encontrada: '{contraseña}' (PBKDF2)")
                            break
                    # Compatibilidad con bcrypt (evitar handler de passlib)
                    elif password_hash.startswith("$2"):
                        import bcrypt
                        if bcrypt.checkpw(contraseña.encode('utf-8'), password_hash.encode('utf-8')):
                            print(f"✓ Contraseña encontrada: '{contraseña}' (bcrypt)")
                            break
                    else:
                        # Texto plano legado
                        if contraseña == password_hash:
                            print(f"✓ Contraseña encontrada: '{contraseña}' (texto plano)")
                            break
                except Exception as e:
                    print(f"Error verificando contraseña '{contraseña}': {e}")
            else:
                print("✗ No se encontró la contraseña entre las opciones probadas")
        
        conn.close()
        
    except Exception as e:
        print(f"Error al verificar contraseñas: {e}")

def crear_usuario_admin():
    """Crear un usuario admin con contraseña conocida"""
    print("\n=== CREANDO USUARIO ADMIN ===")
    
    try:
        conn = sqlite3.connect('ferreteria.db')
        cursor = conn.cursor()
        
        # Verificar si ya existe un usuario admin
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE username = 'admin'")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print("Ya existe un usuario 'admin'. Actualizando contraseña...")
            # Actualizar la contraseña del usuario admin existente
            nueva_contraseña = "admin123"
            password_hash = pwd_context.hash(nueva_contraseña)
            
            cursor.execute(
                "UPDATE usuarios SET password = ? WHERE username = 'admin'",
                (password_hash,)
            )
            print(f"Contraseña actualizada para usuario 'admin': {nueva_contraseña}")
        else:
            print("Creando nuevo usuario 'admin'...")
            # Crear nuevo usuario admin
            nueva_contraseña = "admin123"
            password_hash = pwd_context.hash(nueva_contraseña)
            
            cursor.execute(
                "INSERT INTO usuarios (nombre, username, password, role, activo) VALUES (?, ?, ?, ?, ?)",
                ("Administrador", "admin", password_hash, "administrador", True)
            )
            print(f"Usuario 'admin' creado con contraseña: {nueva_contraseña}")
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"Error al crear/actualizar usuario admin: {e}")

if __name__ == "__main__":
    # Verificar contraseñas actuales
    verificar_contraseñas()
    
    # Crear/actualizar usuario admin
    crear_usuario_admin()
    
    # Verificar de nuevo después de la actualización
    print("\n" + "="*50)
    verificar_contraseñas()