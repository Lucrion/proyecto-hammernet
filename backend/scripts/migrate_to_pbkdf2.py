#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de migración a PBKDF2-SHA256 para usuarios.

Acciones:
1. Elimina el usuario 'admin' existente (si es posible).
2. Si no puede eliminar por restricciones, lo renombra a 'admin_old' y lo desactiva.
3. Crea un nuevo usuario 'admin' con contraseña desde ENV 'ADMIN_PASSWORD' (por defecto '123'),
   hasheada con el nuevo esquema PBKDF2-SHA256.

Uso:
    python backend/scripts/migrate_to_pbkdf2.py
"""

import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import get_db, Base, engine
from models.usuario import UsuarioDB
from core.auth import hash_contraseña
from sqlalchemy.exc import IntegrityError


def migrate_admin_user():
    load_dotenv()
    db = next(get_db())

    admin_username = os.getenv('ADMIN_USERNAME', 'admin')
    admin_password = os.getenv('ADMIN_PASSWORD', '123')

    print("📋 Verificando tablas...")
    Base.metadata.create_all(bind=engine)

    print(f"🔎 Buscando usuario existente: {admin_username}")
    existing = db.query(UsuarioDB).filter(UsuarioDB.username == admin_username).first()

    if existing:
        print("⚠️ Usuario existente encontrado. Intentando eliminar...")
        try:
            db.delete(existing)
            db.commit()
            print("🗑️ Usuario anterior eliminado correctamente.")
        except IntegrityError as ie:
            print(f"❌ No se pudo eliminar por restricciones: {ie}. Intentando renombrar y desactivar...")
            db.rollback()
            # Renombrar con sufijo para evitar colisiones
            suffix = os.getenv('ADMIN_OLD_SUFFIX', 'old')
            new_username = f"{admin_username}_{suffix}"
            # Verificar colisión
            if db.query(UsuarioDB).filter(UsuarioDB.username == new_username).first():
                new_username = f"{admin_username}_{suffix}_{existing.id_usuario}"
            existing.username = new_username
            existing.activo = False
            try:
                db.commit()
                print(f"✏️ Usuario renombrado a '{new_username}' y desactivado.")
            except Exception as e:
                db.rollback()
                print(f"❌ Error al renombrar/desactivar usuario: {e}")

    # Crear nuevo usuario admin con PBKDF2
    print("➕ Creando usuario administrador con PBKDF2-SHA256...")
    new_admin = UsuarioDB(
        nombre='Administrador',
        username=admin_username,
        password=hash_contraseña(admin_password),
        role='administrador',
        activo=True
    )
    db.add(new_admin)
    db.commit()
    print(f"✅ Usuario '{admin_username}' creado con PBKDF2-SHA256.")


if __name__ == '__main__':
    migrate_admin_user()