#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para crear un usuario administrador en la base de datos.

Uso:
    python scripts/create_admin.py <RUT_sin_formato> <contraseña>

Ejemplo:
    python scripts/create_admin.py 111111111 123

Este script aplica hashing seguro a la contraseña usando la misma
función del backend (PBKDF2-SHA256) y evita duplicados por RUT.
"""

import re
import sys
import os
from sqlalchemy.orm import Session

# Asegurar que el backend esté en el sys.path para las importaciones
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from config.database import SessionLocal
# Importar explícitamente dependencias de modelos para evitar errores de mapeo
from models.subcategoria import SubCategoriaDB  # noqa: F401
from models.categoria import CategoriaDB  # noqa: F401
from models.usuario import UsuarioDB
from core.auth import hash_contraseña


def create_admin(rut_input: str, password: str) -> None:
    # Normalizar RUT: extraer solo dígitos
    rut_digits = re.sub(r"\D", "", rut_input or "")
    if not rut_digits:
        print("❌ Debes proporcionar un RUT en dígitos")
        return
    rut_int = int(rut_digits)

    db: Session = SessionLocal()
    try:
        existente = db.query(UsuarioDB).filter(UsuarioDB.rut == rut_int).first()
        if existente:
            print(f"ℹ️  Ya existe un usuario con RUT {rut_int} (rol: {existente.role})")
            return

        admin = UsuarioDB(
            nombre="Administrador",
            apellido=None,
            rut=rut_int,
            email="admin@localhost",
            telefono=None,
            password=hash_contraseña(password),
            role="administrador",
            activo=True,
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)
        print("✅ Usuario administrador creado exitosamente")
        print(f"   ID: {admin.id_usuario}")
        print(f"   RUT: {admin.rut}")
        print(f"   Rol: {admin.role}")
    except Exception as e:
        db.rollback()
        print(f"❌ Error al crear usuario administrador: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python scripts/create_admin.py <RUT_sin_formato> <contraseña>")
        sys.exit(1)
    _, rut_arg, password_arg = sys.argv
    create_admin(rut_arg, password_arg)