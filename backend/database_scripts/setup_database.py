#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script simple para configurar la base de datos con el nuevo esquema
"""

import sqlite3
import os

def setup_database():
    """Configura la base de datos con el nuevo esquema"""
    
    # Conectar a la base de datos
    db_path = os.path.join(os.path.dirname(__file__), 'database.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Configurando base de datos...")
        
        # Crear tabla de categorías
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categorias (
                id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre VARCHAR(100) NOT NULL,
                descripcion TEXT
            )
        """)
        print("Tabla categorias creada")
        
        # Crear tabla de proveedores
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS proveedores (
                id_proveedor INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre VARCHAR(150) NOT NULL,
                contacto VARCHAR(100),
                telefono VARCHAR(50),
                direccion VARCHAR(200)
            )
        """)
        print("Tabla proveedores creada")
        
        # Crear tabla de productos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre VARCHAR(150) NOT NULL,
                descripcion TEXT,
                codigo_barras VARCHAR(50) UNIQUE,
                id_categoria INTEGER,
                id_proveedor INTEGER,
                estado VARCHAR(20) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo')),
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria),
                FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor)
            )
        """)
        print("Tabla productos creada")
        
        # Crear tabla de inventario
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventario (
                id_inventario INTEGER PRIMARY KEY AUTOINCREMENT,
                id_producto INTEGER NOT NULL,
                precio DECIMAL(10,2) NOT NULL,
                cantidad INTEGER NOT NULL,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
            )
        """)
        print("Tabla inventario creada")
        
        # Crear tabla de movimientos de inventario
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS movimientos_inventario (
                id_movimiento INTEGER PRIMARY KEY AUTOINCREMENT,
                id_producto INTEGER NOT NULL,
                tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('entrada', 'salida', 'ajuste')),
                cantidad INTEGER NOT NULL,
                precio_unitario DECIMAL(10,2),
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
            )
        """)
        print("Tabla movimientos_inventario creada")
        
        # Insertar categorías de ejemplo
        categorias = [
            ('Electrónica', 'Productos electrónicos y tecnológicos'),
            ('Ropa', 'Vestimenta y accesorios'),
            ('Hogar', 'Artículos para el hogar y decoración'),
            ('Deportes', 'Equipamiento y artículos deportivos'),
            ('Herramientas', 'Herramientas manuales y eléctricas'),
            ('Automóvil', 'Repuestos y accesorios para vehículos'),
            ('Jardinería', 'Productos para jardín y plantas'),
            ('Oficina', 'Suministros y equipos de oficina')
        ]
        
        for nombre, descripcion in categorias:
            cursor.execute(
                "INSERT OR IGNORE INTO categorias (nombre, descripcion) VALUES (?, ?)",
                (nombre, descripcion)
            )
        print("Categorías insertadas")
        
        # Insertar proveedores de ejemplo
        proveedores = [
            ('TechSupply SA', 'Juan Pérez', '+1-555-0101', 'Av. Tecnología 123, Ciudad Tech'),
            ('Moda Global', 'María García', '+1-555-0102', 'Calle Moda 456, Centro Comercial'),
            ('Hogar Confort', 'Carlos López', '+1-555-0103', 'Blvd. Hogar 789, Zona Residencial'),
            ('Deportes Pro', 'Ana Martínez', '+1-555-0104', 'Av. Deportiva 321, Complejo Deportivo'),
            ('Herramientas Industriales', 'Roberto Silva', '+1-555-0105', 'Polígono Industrial 654, Sector Norte'),
            ('AutoPartes Express', 'Laura Rodríguez', '+1-555-0106', 'Carretera Nacional Km 15, Zona Industrial'),
            ('Verde Jardín', 'Miguel Torres', '+1-555-0107', 'Vivero Central 987, Periferia'),
            ('Oficina Total', 'Carmen Jiménez', '+1-555-0108', 'Centro Empresarial 147, Torre B')
        ]
        
        for nombre, contacto, telefono, direccion in proveedores:
            cursor.execute(
                "INSERT OR IGNORE INTO proveedores (nombre, contacto, telefono, direccion) VALUES (?, ?, ?, ?)",
                (nombre, contacto, telefono, direccion)
            )
        print("Proveedores insertados")
        
        # Confirmar cambios
        conn.commit()
        print("\nBase de datos configurada exitosamente!")
        
        # Mostrar estadísticas
        cursor.execute("SELECT COUNT(*) FROM categorias")
        total_categorias = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM proveedores")
        total_proveedores = cursor.fetchone()[0]
        
        print(f"\nEstadísticas:")
        print(f"- Categorías: {total_categorias}")
        print(f"- Proveedores: {total_proveedores}")
        
    except Exception as e:
        print(f"Error durante la configuración: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()

if __name__ == "__main__":
    setup_database()