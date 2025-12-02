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

# Cargar variables de entorno
load_dotenv()

def verificar_conexion():
    """Verifica que la conexión a PostgreSQL funcione correctamente"""
    try:
        with engine.connect() as connection:
            dialect = engine.dialect.name
            if dialect == 'postgresql':
                result = connection.execute(text("SELECT version();"))
                version = result.fetchone()[0]
                print(f"✅ Conexión exitosa a PostgreSQL: {version[:50]}...")
            elif dialect == 'sqlite':
                result = connection.execute(text("SELECT sqlite_version();"))
                version = result.fetchone()[0]
                print(f"✅ Conexión a SQLite detectada: {version}")
            else:
                print(f"⚠️ Dialecto {dialect} detectado; conexión abierta")
            return True
    except SQLAlchemyError as e:
        print(f"❌ Error de conexión a PostgreSQL: {str(e)}")
        return False


def asegurar_esquema_usuarios():
    """Asegura que la tabla usuarios tenga la columna id_rol y FK opcional hacia roles."""
    try:
        if engine.dialect.name != 'postgresql':
            # Ajuste solo para Postgres; en SQLite se gestiona en config.database
            print("ℹ️ Esquema de usuarios: omitiendo verificación específica de Postgres (dialecto no postgres)")
            return True
        with engine.connect() as connection:
            # Crear columna si no existe
            exists_col = connection.execute(text("SELECT 1 FROM information_schema.columns WHERE table_name='usuarios' AND column_name='id_rol'"))
            if not exists_col.fetchone():
                connection.execute(text("ALTER TABLE usuarios ADD COLUMN id_rol INTEGER"))
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

def seed_roles_y_permisos():
    """Crea roles y permisos base y asigna todos los permisos al rol administrador."""
    try:
        db = next(get_db())
        # Permisos base
        perms = [
            "usuarios",
            "catalogo",
            "inventario",
            "ventas",
            "pagos",
            "auditoria",
            "dashboard",
            "proveedores",
            "categorias",
            "subcategorias",
            "despachos",
        ]
        created_perms = {}
        for name in perms:
            p = db.query(PermisoDB).filter(PermisoDB.descripcion == name).first()
            if not p:
                p = PermisoDB(descripcion=name)
                db.add(p)
                db.flush()
            created_perms[name] = p.id_permiso

        # Roles base
        roles = ["administrador", "vendedor", "bodeguero", "cliente"]
        created_roles = {}
        for rname in roles:
            r = db.query(RolDB).filter(RolDB.nombre == rname).first()
            if not r:
                r = RolDB(nombre=rname)
                db.add(r)
                db.flush()
            created_roles[rname] = r.id_rol

        # Asignar todos los permisos al rol administrador
        admin_id = created_roles.get("administrador")
        if admin_id:
            for pid in created_perms.values():
                rp = db.query(RolPermisoDB).filter(RolPermisoDB.id_rol == admin_id, RolPermisoDB.id_permiso == pid).first()
                if not rp:
                    db.add(RolPermisoDB(id_rol=admin_id, id_permiso=pid))
        db.commit()
        db.close()
        print("✅ Roles y permisos iniciales verificados/creados")
        return True
    except Exception as e:
        try:
            db.rollback(); db.close()
        except Exception:
            pass
        print(f"⚠️  Inicialización de roles/permisos parcialmente fallida: {e}")
        return False

def crear_usuario_admin():
    try:
        db = next(get_db())

        # RUT y contraseña por defecto solicitados
        admin_rut_str = os.getenv('ADMIN_RUT', '203477937')
        admin_rut_digits = re.sub(r"\D", "", admin_rut_str)
        admin_rut = int(admin_rut_digits) if admin_rut_digits else None

        admin_password = os.getenv('ADMIN_PASSWORD', '123')
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@localhost')
        with engine.connect() as conn:
            dialect = engine.dialect.name
            if dialect == 'postgresql':
                cols = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='usuarios'"))
                cols_set = {r[0] for r in cols.fetchall()}
            else:
                cols = conn.execute(text("PRAGMA table_info(usuarios)"))
                cols_set = {r[1] for r in cols.fetchall()}
            nombre_val = 'Administrador'
            password_hash = hash_contraseña(admin_password)
            role_val = 'administrador'
            activo_val = True
            username_val = os.getenv('ADMIN_USERNAME', 'admin')
            if dialect == 'postgresql':
                username_required_row = conn.execute(text("SELECT is_nullable FROM information_schema.columns WHERE table_name='usuarios' AND column_name='username'")).fetchone()
                username_required = bool(username_required_row and (str(username_required_row[0]).upper() == 'NO'))
            else:
                username_required = False

            # Verificar existencia por rut como texto (compatible con varchar/int)
            exists_sql = "SELECT 1 FROM usuarios WHERE CAST(rut AS TEXT) = :rut_txt LIMIT 1" if dialect == 'postgresql' else "SELECT 1 FROM usuarios WHERE rut = :rut_txt LIMIT 1"
            exists_row = conn.execute(text(exists_sql), {"rut_txt": admin_rut_str}).fetchone()
            exists_username_row = None
            if 'username' in cols_set:
                exists_username_row = conn.execute(text("SELECT 1 FROM usuarios WHERE username = :u LIMIT 1"), {"u": username_val}).fetchone()

            # Obtener id_rol de administrador si existe
            admin_role_row = conn.execute(text("SELECT id_rol FROM roles WHERE nombre='administrador' LIMIT 1")).fetchone()
            admin_role_id = int(admin_role_row[0]) if admin_role_row else None

            if exists_username_row:
                set_parts = ["nombre=:nombre", "password=:password", "activo=:activo"]
                if 'role' in cols_set:
                    set_parts.insert(2, "role=:role")
                params = {"nombre": nombre_val, "password": password_hash, "role": role_val, "activo": activo_val, "username": username_val}
                if 'id_rol' in cols_set and admin_role_id:
                    set_parts.append("id_rol=:id_rol")
                    params["id_rol"] = admin_role_id
                up_sql = "UPDATE usuarios SET nombre=:nombre, password=:password, role=:role, activo=:activo WHERE username=:username"
                conn.execute(text(up_sql), params)
                db.commit()
                print("✅ Usuario administrador actualizado exitosamente")
                print(f"   RUT: {admin_rut_str}")
                print(f"   Contraseña: {admin_password}")
                print(f"   Rol: administrador")
                print(f"   Email: {admin_email}")
                return True
            elif exists_row:
                set_parts = ["nombre=:nombre", "password=:password", "activo=:activo"]
                if 'role' in cols_set:
                    set_parts.insert(2, "role=:role")
                params = {"nombre": nombre_val, "password": password_hash, "role": role_val, "activo": activo_val, "rut_txt": admin_rut_str}
                if 'id_rol' in cols_set and admin_role_id:
                    set_parts.append("id_rol=:id_rol")
                    params["id_rol"] = admin_role_id
                up_sql = f"UPDATE usuarios SET {', '.join(set_parts)} WHERE CAST(rut AS TEXT) = :rut_txt" if dialect == 'postgresql' else f"UPDATE usuarios SET {', '.join(set_parts)} WHERE rut = :rut_txt"
                conn.execute(text(up_sql), params)
                db.commit()
                print("✅ Usuario administrador actualizado exitosamente")
                print(f"   RUT: {admin_rut_str}")
                print(f"   Contraseña: {admin_password}")
                print(f"   Rol: administrador")
                print(f"   Email: {admin_email}")
                return True
            else:
                insert_cols = ["nombre", "rut", "email", "password", "activo"]
                if 'role' in cols_set:
                    insert_cols.append('role')
                insert_cols = [c for c in insert_cols if c in cols_set]
                if 'username' in cols_set:
                    candidate = username_val
                    if username_required:
                        i = 0
                        while conn.execute(text("SELECT 1 FROM usuarios WHERE username=:u LIMIT 1"), {"u": candidate}).fetchone():
                            i += 1
                            candidate = f"{username_val}{i}"
                    username_val = candidate
                    insert_cols.append('username')
                if 'id_rol' in cols_set and admin_role_id:
                    insert_cols.append('id_rol')
                placeholders = ",".join([f":{c}" for c in insert_cols])
                cols_str = ",".join(insert_cols)
                ins_sql = f"INSERT INTO usuarios ({cols_str}) VALUES ({placeholders})"
                params = {"nombre": nombre_val, "rut": admin_rut_str, "email": admin_email, "password": password_hash, "role": role_val, "activo": activo_val}
                if 'username' in cols_set:
                    params['username'] = username_val
                if 'id_rol' in cols_set and admin_role_id:
                    params['id_rol'] = admin_role_id
                conn.execute(text(ins_sql), params)
                db.commit()
                print("✅ Usuario administrador creado exitosamente")
                print(f"   RUT: {admin_rut_str}")
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

    # Paso 2.1: Inicializar roles y permisos
    seed_roles_y_permisos()

    # Paso 3: Crear usuario administrador
    if not crear_usuario_admin():
        print("❌ Error al crear usuario administrador")
        raise SystemExit(1)

    print("=" * 60)
    print("Configuración de PostgreSQL completada exitosamente")

if __name__ == '__main__':
    main()
