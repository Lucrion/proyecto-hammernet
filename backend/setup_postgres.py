#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de configuración para PostgreSQL en producción

Este script se encarga de:
1. Crear todas las tablas necesarias en PostgreSQL
2. Verificar la conexión a la base de datos
3. Crear el usuario administrador inicial
4. Configurar índices y restricciones
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Importar modelos y configuración
from database import Base, engine, get_db
from models import ProductoDB, UsuarioDB, MensajeContactoDB
from auth import hash_contraseña

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

def crear_tablas():
    """Crea todas las tablas definidas en los modelos"""
    try:
        print("📋 Creando tablas en PostgreSQL...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas exitosamente")
        
        # Verificar que las tablas se crearon
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tablas = [row[0] for row in result.fetchall()]
            print(f"📊 Tablas disponibles: {', '.join(tablas)}")
            
        return True
    except SQLAlchemyError as e:
        print(f"❌ Error al crear tablas: {str(e)}")
        return False

def crear_usuario_admin():
    """Crea el usuario administrador inicial"""
    try:
        db = next(get_db())
        
        # Verificar si el usuario admin ya existe
        admin_existente = db.query(UsuarioDB).filter(UsuarioDB.username == 'admin').first()
        if admin_existente:
            print("ℹ️  El usuario administrador ya existe")
            return True
        
        # Crear usuario administrador
        admin_password = os.getenv('ADMIN_PASSWORD', '123')
        admin_user = UsuarioDB(
            nombre='Administrador',
            username='admin',
            password=hash_contraseña(admin_password),
            role='administrador'
        )
        
        db.add(admin_user)
        db.commit()
        print("✅ Usuario administrador creado exitosamente")
        print(f"   Usuario: admin")
        print(f"   Contraseña: {admin_password}")
        print(f"   Rol: administrador")
        
        return True
    except Exception as e:
        print(f"❌ Error al crear usuario administrador: {str(e)}")
        return False
    finally:
        db.close()

def main():
    """Función principal de configuración"""
    print("🚀 Iniciando configuración de PostgreSQL para producción...")
    print("=" * 60)
    
    # Verificar variables de entorno críticas
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ ERROR: Variable DATABASE_URL no configurada")
        sys.exit(1)
    
    if 'postgres' not in database_url.lower():
        print("⚠️  ADVERTENCIA: La URL no parece ser de PostgreSQL")
    
    print(f"🔗 Conectando a: {database_url[:30]}...")
    
    # Paso 1: Verificar conexión
    if not verificar_conexion():
        print("❌ No se pudo establecer conexión con PostgreSQL")
        sys.exit(1)
    
    # Paso 2: Crear tablas
    if not crear_tablas():
        print("❌ Error al crear las tablas")
        sys.exit(1)
    
    # Paso 3: Crear usuario administrador
    if not crear_usuario_admin():
        print("❌ Error al crear usuario administrador")
        sys.exit(1)
    
    print("=" * 60)
    print("🎉 Configuración de PostgreSQL completada exitosamente")
    print("📝 La base de datos está lista para producción")

if __name__ == '__main__':
    main()