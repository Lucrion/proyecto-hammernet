#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para configurar MySQL con XAMPP

Este script ayuda a configurar la base de datos MySQL para el proyecto
cuando se usa XAMPP como servidor local.
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def create_database():
    """
    Crea la base de datos 'ferreteria' si no existe
    """
    try:
        # Conectar a MySQL sin especificar base de datos
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password=''  # XAMPP por defecto no tiene contraseña para root
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Crear base de datos si no existe
            cursor.execute("CREATE DATABASE IF NOT EXISTS ferreteria CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print("✅ Base de datos 'ferreteria' creada o ya existe")
            
            # Mostrar bases de datos disponibles
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            print("\n📋 Bases de datos disponibles:")
            for db in databases:
                print(f"   - {db[0]}")
                
            cursor.close()
            
    except Error as e:
        print(f"❌ Error al conectar con MySQL: {e}")
        print("\n🔧 Soluciones posibles:")
        print("   1. Asegúrate de que XAMPP esté ejecutándose")
        print("   2. Verifica que el servicio MySQL esté activo en XAMPP")
        print("   3. Comprueba que el puerto 3306 esté disponible")
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("\n🔌 Conexión a MySQL cerrada")

def test_connection():
    """
    Prueba la conexión a la base de datos usando la configuración del proyecto
    """
    try:
        # Usar la misma configuración que el proyecto
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='',
            database='ferreteria'
        )
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"✅ Conexión exitosa a MySQL Server versión {db_info}")
            
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            database_name = cursor.fetchone()
            print(f"✅ Conectado a la base de datos: {database_name[0]}")
            cursor.close()
            
    except Error as e:
        print(f"❌ Error al conectar con la base de datos: {e}")
        return False
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            
    return True

def main():
    print("🔧 Configurador de MySQL para XAMPP")
    print("=" * 40)
    
    print("\n1️⃣ Creando base de datos...")
    create_database()
    
    print("\n2️⃣ Probando conexión...")
    if test_connection():
        print("\n✅ ¡Configuración completada exitosamente!")
        print("\n📝 Próximos pasos:")
        print("   1. Instala las dependencias: pip install -r requirements.txt")
        print("   2. Inicializa las tablas: python init_db.py")
        print("   3. Ejecuta el servidor: python main.py")
    else:
        print("\n❌ La configuración no se completó correctamente")
        print("\n🔧 Verifica que:")
        print("   - XAMPP esté ejecutándose")
        print("   - El servicio MySQL esté activo")
        print("   - No haya otros servicios usando el puerto 3306")

if __name__ == '__main__':
    main()