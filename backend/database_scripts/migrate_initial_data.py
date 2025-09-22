#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy.orm import Session
from database import get_db, engine
from models import CategoriaDB, ProveedorDB

def migrate_initial_data():
    """Migra los datos iniciales de categorías y proveedores"""
    
    # Crear una sesión de base de datos
    db = Session(bind=engine)
    
    try:
        # Verificar si ya existen categorías
        existing_categories = db.query(CategoriaDB).count()
        if existing_categories == 0:
            print("Insertando categorías iniciales...")
            
            # Insertar categorías de ejemplo
            categorias = [
                CategoriaDB(nombre='Electrónica', descripcion='Productos electrónicos y tecnológicos'),
                CategoriaDB(nombre='Ropa', descripcion='Vestimenta y accesorios'),
                CategoriaDB(nombre='Hogar', descripcion='Artículos para el hogar y decoración'),
                CategoriaDB(nombre='Deportes', descripcion='Equipamiento y artículos deportivos'),
                CategoriaDB(nombre='Herramientas', descripcion='Herramientas manuales y eléctricas'),
                CategoriaDB(nombre='Automóvil', descripcion='Repuestos y accesorios para vehículos'),
                CategoriaDB(nombre='Jardinería', descripcion='Productos para jardín y plantas'),
                CategoriaDB(nombre='Oficina', descripcion='Suministros y equipos de oficina')
            ]
            
            for categoria in categorias:
                db.add(categoria)
            
            db.commit()
            print(f"Se insertaron {len(categorias)} categorías")
        else:
            print(f"Ya existen {existing_categories} categorías en la base de datos")
        
        # Verificar si ya existen proveedores
        existing_providers = db.query(ProveedorDB).count()
        if existing_providers == 0:
            print("Insertando proveedores iniciales...")
            
            # Insertar proveedores de ejemplo
            proveedores = [
                ProveedorDB(nombre='TechSupply SA', contacto='Juan Pérez', telefono='+1-555-0101', direccion='Av. Tecnología 123, Ciudad Tech'),
                ProveedorDB(nombre='Moda Global', contacto='María García', telefono='+1-555-0102', direccion='Calle Moda 456, Centro Comercial'),
                ProveedorDB(nombre='Hogar Confort', contacto='Carlos López', telefono='+1-555-0103', direccion='Blvd. Hogar 789, Zona Residencial'),
                ProveedorDB(nombre='Deportes Pro', contacto='Ana Martínez', telefono='+1-555-0104', direccion='Av. Deportiva 321, Complejo Deportivo'),
                ProveedorDB(nombre='Herramientas Industriales', contacto='Roberto Silva', telefono='+1-555-0105', direccion='Polígono Industrial 654, Sector Norte'),
                ProveedorDB(nombre='AutoPartes Express', contacto='Laura Rodríguez', telefono='+1-555-0106', direccion='Carretera Nacional Km 15, Zona Industrial'),
                ProveedorDB(nombre='Verde Jardín', contacto='Miguel Torres', telefono='+1-555-0107', direccion='Vivero Central 987, Periferia'),
                ProveedorDB(nombre='Oficina Total', contacto='Carmen Jiménez', telefono='+1-555-0108', direccion='Centro Empresarial 147, Torre B')
            ]
            
            for proveedor in proveedores:
                db.add(proveedor)
            
            db.commit()
            print(f"Se insertaron {len(proveedores)} proveedores")
        else:
            print(f"Ya existen {existing_providers} proveedores en la base de datos")
        
        print("Migración de datos iniciales completada exitosamente")
        
    except Exception as e:
        print(f"Error durante la migración: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_initial_data()