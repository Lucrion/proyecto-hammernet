#!/usr/bin/env python3
"""
Script para probar la conexión a la base de datos
"""
from config.database import SessionLocal
from models.usuario import UsuarioDB

def test_db_connection():
    """Probar la conexión a la base de datos"""
    db = SessionLocal()
    try:
        usuarios = db.query(UsuarioDB).all()
        print(f'✓ Conexión exitosa!')
        print(f'Usuarios encontrados: {len(usuarios)}')
        
        for usuario in usuarios:
            print(f'- Username: {usuario.username}')
            print(f'  Nombre: {usuario.nombre}')
            print(f'  Activo: {usuario.activo}')
            print(f'  Rol: {usuario.role}')
            print()
            
    except Exception as e:
        print(f'✗ Error de conexión: {e}')
        print(f'Tipo de error: {type(e).__name__}')
    finally:
        db.close()

if __name__ == "__main__":
    test_db_connection()