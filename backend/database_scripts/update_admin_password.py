#!/usr/bin/env python
# -*- coding: utf-8 -*-

from auth import hash_contraseña
from database import SessionLocal
from models import UsuarioDB

def update_admin_password():
    db = SessionLocal()
    try:
        # Buscar el usuario admin
        user = db.query(UsuarioDB).filter(UsuarioDB.username == 'admin').first()
        
        if user:
            # Actualizar la contraseña
            new_hash = hash_contraseña('admin123')
            user.password = new_hash
            db.commit()
            print(f"Contraseña actualizada para usuario: {user.username}")
            print(f"Nuevo hash: {new_hash}")
        else:
            print("Usuario admin no encontrado")
            
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_admin_password()