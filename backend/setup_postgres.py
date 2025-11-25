#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de configuración para PostgreSQL en producción
1. Crear todas las tablas necesarias en PostgreSQL
2. Verificar la conexión a la base de datos
3. Crear el usuario administrador inicial
"""

import os
import re
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import configure_mappers
from dotenv import load_dotenv

# Importar modelos y configuración
from config.database import Base, engine, get_db
from models.usuario import UsuarioDB
# Importar los modelos relacionados para asegurar el registro de mapeos antes de crear tablas
from models import (
    CategoriaDB, SubCategoriaDB, ProductoDB, ProveedorDB,
    VentaDB, DetalleVentaDB, MovimientoInventarioDB,
    PagoDB, DespachoDB, RolDB, PermisoDB, RolPermisoDB,
)
from core.auth import hash_contraseña
from core.auth import hash_contraseña

# Cargar variables de entorno
load_dotenv()

def verificar_conexion():
    """Verifica que la conexión a PostgreSQL funcione correctamente"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Conexión exitosa a PostgreSQL: {version[:50]}...")
            return True
    except SQLAlchemyError as e:
        print(f"❌ Error de conexión a PostgreSQL: {str(e)}")
        return False


def asegurar_esquema_usuarios():
    """Asegura que la tabla usuarios tenga la columna id_rol y FK opcional hacia roles."""
    try:
        with engine.connect() as connection:
            # Crear columna si no existe
            connection.execute(text("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS id_rol INTEGER"))
            # Agregar FK si no existe (controlando por nombre de constraint)
            fk_name = 'fk_usuarios_roles'
            exists = connection.execute(text(
                """
                SELECT 1 FROM information_schema.table_constraints
                WHERE table_name = 'usuarios' AND constraint_name = :fk
                """
            ), {"fk": fk_name}).fetchone()
            if not exists:
                try:
                    connection.execute(text(
                        "ALTER TABLE usuarios ADD CONSTRAINT fk_usuarios_roles FOREIGN KEY (id_rol) REFERENCES roles(id_rol) ON DELETE SET NULL"
                    ))
                except Exception as ce:
                    print(f"⚠️  No se pudo crear FK fk_usuarios_roles: {ce}")
            print("✅ Esquema de usuarios verificado/actualizado (id_rol)")
            return True
    except Exception as e:
        print(f"❌ Error al asegurar esquema de usuarios: {e}")
        return False

def crear_tablas():
    """Crea todas las tablas definidas en los modelos"""
    try:
        print("📋 Configurando mapeos de SQLAlchemy...")
        try:
            configure_mappers()
            print("🧩 Mappers configurados correctamente")
        except Exception as me:
            print(f"⚠️  Advertencia al configurar mappers: {me}")
        print("📋 Creando tablas en PostgreSQL...")
        Base.metadata.create_all(bind=engine)
        # Asegurar compatibilidad de esquema
        asegurar_esquema_usuarios()
        print("🐘 Tablas creadas en PostgreSQL (setup_postgres.py)")
        print("✅ Tablas creadas exitosamente")
        return True
    except SQLAlchemyError as e:
        print(f"❌ Error al crear tablas: {str(e)}")
        return False

def crear_usuario_admin():
    """Crea el usuario administrador inicial"""
    try:
        db = next(get_db())

        # Verificar si el usuario admin ya existe (por RUT)
        admin_rut_str = os.getenv('ADMIN_RUT', '0')
        # Convertir a entero (remover cualquier no dígito por si viene con puntos/guion)
        admin_rut_digits = re.sub(r"\D", "", admin_rut_str)
        admin_rut = int(admin_rut_digits) if admin_rut_digits else None
        admin_existente = db.query(UsuarioDB).filter(UsuarioDB.rut == admin_rut).first()
        if admin_existente:
            print("ℹ️  El usuario administrador ya existe")
            return True

        # Crear usuario administrador
        admin_password = os.getenv('ADMIN_PASSWORD', '123')
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@localhost')
        if admin_existente:
            # Actualizar contraseña y asegurar rol/activo
            admin_existente.password = hash_contraseña(admin_password)
            admin_existente.role = 'administrador'
            admin_existente.activo = True
            db.commit()
            print("✅ Usuario administrador actualizado exitosamente")
            print(f"   RUT: {admin_rut}")
            print(f"   Contraseña: {admin_password}")
            print(f"   Rol: administrador")
            print(f"   Email: {admin_email}")
            return True
        else:
            admin_user = UsuarioDB(
                nombre='Administrador',
                apellido=None,
                rut=admin_rut,
                email=admin_email,
                telefono=None,
                password=hash_contraseña(admin_password),
                role='administrador',
                activo=True
            )

            db.add(admin_user)
            db.commit()
            print("✅ Usuario administrador creado exitosamente")
            print(f"   RUT: {admin_rut}")
            print(f"   Contraseña: {admin_password}")
            print(f"   Rol: administrador")
            print(f"   Email: {admin_email}")
            return True
    except Exception as e:
        print(f"❌ Error al crear usuario administrador: {str(e)}")
        return False
    finally:
        try:
            db.close()
        except Exception:
            pass

def main():
    """Función principal de configuración"""
    print("🚀 Iniciando configuración de PostgreSQL para producción...")
    print("=" * 60)

    # Verificar variables de entorno críticas
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ ERROR: Variable DATABASE_URL no configurada")
        raise SystemExit(1)

    print(f"🔗 Conectando a: {database_url[:30]}...")

    # Paso 1: Verificar conexión
    if not verificar_conexion():
        print("❌ No se pudo establecer conexión con PostgreSQL")
        raise SystemExit(1)

    # Paso 2: Crear tablas
    if not crear_tablas():
        print("❌ Error al crear las tablas")
        raise SystemExit(1)

    # Paso 3: Crear usuario administrador
    if not crear_usuario_admin():
        print("❌ Error al crear usuario administrador")
        raise SystemExit(1)

    print("=" * 60)
    print("Configuración de PostgreSQL completada exitosamente")

if __name__ == '__main__':
    main()
