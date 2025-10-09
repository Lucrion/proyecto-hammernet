#!/usr/bin/env python3
"""
Script para configurar datos iniciales del sistema
- Usuario administrador
- Productos de ferretería
- Mensajes de ejemplo
"""
from config.database import SessionLocal
from models.usuario import UsuarioDB
from models.producto import ProductoDB
from models.categoria import CategoriaDB
from models.proveedor import ProveedorDB
from models.mensaje import MensajeContactoDB
from core.auth import hash_contraseña
from datetime import datetime

def create_admin_user(db):
    """Crear usuario administrador"""
    print("Creando usuario administrador...")
    
    # Verificar si ya existe
    existing_admin = db.query(UsuarioDB).filter(UsuarioDB.username == "admin").first()
    if existing_admin:
        print("✓ Usuario admin ya existe")
        return existing_admin
    
    # Crear nuevo usuario admin
    admin_user = UsuarioDB(
        username="admin",
        nombre="Administrador",
        password=hash_contraseña("admin123"),
        role="admin",
        activo=True
    )
    
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    print("✓ Usuario admin creado exitosamente")
    return admin_user

def create_categories(db):
    """Crear categorías de productos"""
    print("Creando categorías...")
    
    categorias = [
        {"nombre": "Herramientas", "descripcion": "Herramientas manuales y eléctricas"},
        {"nombre": "Tornillería", "descripcion": "Tornillos, tuercas y elementos de fijación"},
        {"nombre": "Pintura", "descripcion": "Pinturas, barnices y accesorios"},
        {"nombre": "Plomería", "descripcion": "Tuberías, conexiones y accesorios"},
        {"nombre": "Electricidad", "descripcion": "Cables, interruptores y material eléctrico"},
        {"nombre": "Ferretería General", "descripcion": "Artículos varios de ferretería"}
    ]
    
    created_categories = []
    for cat_data in categorias:
        existing = db.query(CategoriaDB).filter(CategoriaDB.nombre == cat_data["nombre"]).first()
        if not existing:
            categoria = CategoriaDB(**cat_data)
            db.add(categoria)
            created_categories.append(categoria)
        else:
            created_categories.append(existing)
    
    db.commit()
    print(f"✓ {len(created_categories)} categorías configuradas")
    return created_categories

def create_providers(db):
    """Crear proveedores"""
    print("Creando proveedores...")
    
    proveedores = [
        {
            "nombre": "Ferretería Central S.A.",
            "rut": "76.123.456-7",
            "razon_social": "Ferretería Central Sociedad Anónima",
            "sucursal": "Casa Matriz",
            "direccion": "Av. Principal 1234",
            "ciudad": "Santiago",
            "celular": "+56 9 8765 4321",
            "correo": "ventas@ferreteriacentral.cl",
            "contacto": "Juan Pérez",
            "telefono": "+56 2 2345 6789"
        },
        {
            "nombre": "Distribuidora Herramientas Ltda.",
            "rut": "78.987.654-3",
            "razon_social": "Distribuidora de Herramientas Limitada",
            "sucursal": "Sucursal Norte",
            "direccion": "Calle Industrial 567",
            "ciudad": "Valparaíso",
            "celular": "+56 9 1234 5678",
            "correo": "contacto@distherramientas.cl",
            "contacto": "María González",
            "telefono": "+56 32 234 5678"
        },
        {
            "nombre": "Suministros Eléctricos del Sur",
            "rut": "77.555.888-9",
            "razon_social": "Suministros Eléctricos del Sur SpA",
            "sucursal": "Principal",
            "direccion": "Av. Eléctrica 890",
            "ciudad": "Concepción",
            "celular": "+56 9 5555 7777",
            "correo": "info@electricosur.cl",
            "contacto": "Carlos Rodríguez",
            "telefono": "+56 41 333 4444"
        },
        {
            "nombre": "Pinturas y Barnices Norte",
            "rut": "79.111.222-4",
            "razon_social": "Pinturas y Barnices del Norte Ltda.",
            "sucursal": "Almacén Central",
            "direccion": "Pasaje Colorido 123",
            "ciudad": "Antofagasta",
            "celular": "+56 9 2222 3333",
            "correo": "ventas@pinturasnorte.cl",
            "contacto": "Ana Silva",
            "telefono": "+56 55 444 5555"
        },
        {
            "nombre": "Plomería Profesional",
            "rut": "75.666.777-8",
            "razon_social": "Plomería Profesional y Asociados",
            "direccion": "Calle Tubería 456",
            "ciudad": "Temuco",
            "celular": "+56 9 7777 8888",
            "correo": "contacto@plomeriapro.cl",
            "contacto": "Roberto Muñoz"
        }
    ]
    
    created_providers = []
    for prov_data in proveedores:
        existing = db.query(ProveedorDB).filter(ProveedorDB.nombre == prov_data["nombre"]).first()
        if not existing:
            proveedor = ProveedorDB(**prov_data)
            db.add(proveedor)
            created_providers.append(proveedor)
        else:
            created_providers.append(existing)
    
    db.commit()
    print(f"✓ {len(created_providers)} proveedores configurados")
    return created_providers

def create_products(db, categories, providers):
    """Crear productos de ferretería"""
    print("Creando productos...")
    
    # Obtener categorías por nombre
    cat_herramientas = next((c for c in categories if c.nombre == "Herramientas"), None)
    cat_tornilleria = next((c for c in categories if c.nombre == "Tornillería"), None)
    cat_pintura = next((c for c in categories if c.nombre == "Pintura"), None)
    cat_plomeria = next((c for c in categories if c.nombre == "Plomería"), None)
    cat_electricidad = next((c for c in categories if c.nombre == "Electricidad"), None)
    cat_general = next((c for c in categories if c.nombre == "Ferretería General"), None)
    
    # Obtener proveedores por nombre
    prov_ferreteria = next((p for p in providers if "Ferretería Central" in p.nombre), None)
    prov_herramientas = next((p for p in providers if "Distribuidora Herramientas" in p.nombre), None)
    prov_electrico = next((p for p in providers if "Suministros Eléctricos" in p.nombre), None)
    prov_pintura = next((p for p in providers if "Pinturas y Barnices" in p.nombre), None)
    prov_plomeria = next((p for p in providers if "Plomería Profesional" in p.nombre), None)
    
    productos = [
        # Herramientas
        {
            "nombre": "Martillo de Carpintero 16oz",
            "descripcion": "Martillo profesional con mango de madera, cabeza de acero forjado",
            "precio_venta": 25.99,
            "cantidad_disponible": 50,
            "id_categoria": cat_herramientas.id_categoria if cat_herramientas else 1,
            "id_proveedor": prov_herramientas.id_proveedor if prov_herramientas else 1,
            "codigo_interno": "MART001"
        },
        {
            "nombre": "Destornillador Phillips #2",
            "descripcion": "Destornillador con punta Phillips, mango ergonómico",
            "precio_venta": 8.50,
            "cantidad_disponible": 100,
            "id_categoria": cat_herramientas.id_categoria if cat_herramientas else 1,
            "id_proveedor": prov_herramientas.id_proveedor if prov_herramientas else 1,
            "codigo_interno": "DEST001"
        },
        {
            "nombre": "Taladro Eléctrico 500W",
            "descripcion": "Taladro eléctrico con velocidad variable, incluye brocas",
            "precio_venta": 89.99,
            "cantidad_disponible": 15,
            "id_categoria": cat_herramientas.id_categoria if cat_herramientas else 1,
            "id_proveedor": prov_herramientas.id_proveedor if prov_herramientas else 1,
            "codigo_interno": "TAL001"
        },
        
        # Tornillería
        {
            "nombre": "Tornillos Autorroscantes 3/4\"",
            "descripcion": "Caja de 100 tornillos autorroscantes galvanizados",
            "precio_venta": 12.75,
            "cantidad_disponible": 200,
            "id_categoria": cat_tornilleria.id_categoria if cat_tornilleria else 2,
            "id_proveedor": prov_ferreteria.id_proveedor if prov_ferreteria else 1,
            "codigo_interno": "TORN001"
        },
        {
            "nombre": "Tuercas Hexagonales M8",
            "descripcion": "Paquete de 50 tuercas hexagonales de acero",
            "precio_venta": 6.25,
            "cantidad_disponible": 150,
            "id_categoria": cat_tornilleria.id_categoria if cat_tornilleria else 2,
            "id_proveedor": prov_ferreteria.id_proveedor if prov_ferreteria else 1,
            "codigo_interno": "TUER001"
        },
        
        # Pintura
        {
            "nombre": "Pintura Látex Blanco 4L",
            "descripcion": "Pintura látex lavable para interiores, color blanco",
            "precio_venta": 45.00,
            "cantidad_disponible": 30,
            "id_categoria": cat_pintura.id_categoria if cat_pintura else 3,
            "id_proveedor": prov_pintura.id_proveedor if prov_pintura else 1,
            "codigo_interno": "PINT001"
        },
        {
            "nombre": "Brocha 3 pulgadas",
            "descripcion": "Brocha profesional con cerdas sintéticas",
            "precio_venta": 15.50,
            "cantidad_disponible": 75,
            "id_categoria": cat_pintura.id_categoria if cat_pintura else 3,
            "id_proveedor": prov_pintura.id_proveedor if prov_pintura else 1,
            "codigo_interno": "BROC001"
        },
        
        # Plomería
        {
            "nombre": "Tubería PVC 1/2\" x 3m",
            "descripcion": "Tubería de PVC para agua fría, 1/2 pulgada",
            "precio_venta": 8.90,
            "cantidad_disponible": 80,
            "id_categoria": cat_plomeria.id_categoria if cat_plomeria else 4,
            "id_proveedor": prov_plomeria.id_proveedor if prov_plomeria else 1,
            "codigo_interno": "TUB001"
        },
        {
            "nombre": "Codo PVC 90° 1/2\"",
            "descripcion": "Conexión codo de 90 grados para tubería de 1/2\"",
            "precio_venta": 2.25,
            "cantidad_disponible": 300,
            "id_categoria": cat_plomeria.id_categoria if cat_plomeria else 4,
            "id_proveedor": prov_plomeria.id_proveedor if prov_plomeria else 1,
            "codigo_interno": "COD001"
        },
        
        # Electricidad
        {
            "nombre": "Cable THW 12 AWG",
            "descripcion": "Cable eléctrico THW calibre 12, por metro",
            "precio_venta": 3.50,
            "cantidad_disponible": 500,
            "id_categoria": cat_electricidad.id_categoria if cat_electricidad else 5,
            "id_proveedor": prov_electrico.id_proveedor if prov_electrico else 1,
            "codigo_interno": "CAB001"
        },
        {
            "nombre": "Interruptor Simple",
            "descripcion": "Interruptor sencillo 15A, color blanco",
            "precio_venta": 4.75,
            "cantidad_disponible": 120,
            "id_categoria": cat_electricidad.id_categoria if cat_electricidad else 5,
            "id_proveedor": prov_electrico.id_proveedor if prov_electrico else 1,
            "codigo_interno": "INT001"
        },
        
        # Ferretería General
        {
            "nombre": "Candado de Seguridad 40mm",
            "descripcion": "Candado de latón con arco de acero templado",
            "precio_venta": 18.00,
            "cantidad_disponible": 60,
            "id_categoria": cat_general.id_categoria if cat_general else 6,
            "id_proveedor": prov_ferreteria.id_proveedor if prov_ferreteria else 1,
            "codigo_interno": "CAND001"
        }
    ]
    
    created_products = []
    for prod_data in productos:
        existing = db.query(ProductoDB).filter(ProductoDB.codigo_interno == prod_data["codigo_interno"]).first()
        if not existing:
            producto = ProductoDB(**prod_data)
            db.add(producto)
            created_products.append(producto)
        else:
            created_products.append(existing)
    
    db.commit()
    print(f"✓ {len(created_products)} productos creados")
    return created_products

def create_messages(db, admin_user):
    """Crear mensajes de ejemplo"""
    print("Creando mensajes...")
    
    mensajes = [
        {
            "nombre": "Sistema",
            "apellido": "Administrador", 
            "email": "admin@ferreteria.com",
            "asunto": "Bienvenido al Sistema",
            "mensaje": "¡Bienvenido al sistema de gestión de ferretería! Aquí podrás administrar productos, categorías y usuarios.",
            "leido": False
        },
        {
            "nombre": "Sistema",
            "apellido": "Notificaciones",
            "email": "notificaciones@ferreteria.com", 
            "asunto": "Recordatorio de Inventario",
            "mensaje": "Recuerda revisar el inventario semanalmente para mantener el stock actualizado.",
            "leido": False
        },
        {
            "nombre": "Desarrollo",
            "apellido": "Equipo",
            "email": "desarrollo@ferreteria.com",
            "asunto": "Nueva Funcionalidad",
            "mensaje": "Se ha agregado la funcionalidad de gestión de proveedores. Puedes acceder desde el menú principal.",
            "leido": True
        },
        {
            "nombre": "Mantenimiento",
            "apellido": "Sistemas",
            "email": "sistemas@ferreteria.com",
            "asunto": "Mantenimiento Programado",
            "mensaje": "El sistema tendrá mantenimiento programado el próximo domingo de 2:00 AM a 4:00 AM.",
            "leido": False
        }
    ]
    
    created_messages = []
    for msg_data in mensajes:
        mensaje = MensajeContactoDB(**msg_data)
        db.add(mensaje)
        created_messages.append(mensaje)
    
    db.commit()
    print(f"✓ {len(created_messages)} mensajes creados")
    return created_messages

def main():
    """Función principal"""
    print("=== Configuración de Datos Iniciales ===")
    
    db = SessionLocal()
    try:
        # 1. Crear usuario admin
        admin_user = create_admin_user(db)
        
        # 2. Crear categorías
        categories = create_categories(db)
        
        # 3. Crear proveedores
        providers = create_providers(db)
        
        # 4. Crear productos
        products = create_products(db, categories, providers)
        
        # 5. Crear mensajes
        messages = create_messages(db, admin_user)
        
        print("\n=== Resumen ===")
        print(f"✓ Usuario admin: {admin_user.username}")
        print(f"✓ Categorías: {len(categories)}")
        print(f"✓ Proveedores: {len(providers)}")
        print(f"✓ Productos: {len(products)}")
        print(f"✓ Mensajes: {len(messages)}")
        print("\n¡Configuración completada exitosamente!")
        
    except Exception as e:
        print(f"✗ Error durante la configuración: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()