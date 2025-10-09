import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import get_db, Base, engine
from models import UsuarioDB, CategoriaDB, ProductoDB, ProveedorDB
from core.auth import hash_contraseña
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def populate_database():
    try:
        # Crear las tablas si no existen
        Base.metadata.create_all(bind=engine)
        print("🗂️ Tablas verificadas en populate_db.py")
        
        # Obtener sesión de base de datos
        db = next(get_db())
        
        # Crear categorías
        categorias_data = [
            {"nombre": "Herramientas Manuales", "descripcion": "Herramientas básicas para construcción"},
            {"nombre": "Herramientas Eléctricas", "descripcion": "Herramientas con motor eléctrico"},
            {"nombre": "Materiales de Construcción", "descripcion": "Materiales básicos para construcción"},
            {"nombre": "Ferretería General", "descripcion": "Artículos diversos de ferretería"},
            {"nombre": "Pinturas y Acabados", "descripcion": "Pinturas, barnices y productos de acabado"}
        ]
        
        categorias_creadas = []
        for cat_data in categorias_data:
            categoria_existente = db.query(CategoriaDB).filter(CategoriaDB.nombre == cat_data["nombre"]).first()
            if not categoria_existente:
                categoria = CategoriaDB(**cat_data)
                db.add(categoria)
                db.flush()
                categorias_creadas.append(categoria)
            else:
                categorias_creadas.append(categoria_existente)
        
        # Crear proveedores
        proveedores_data = [
            {"nombre": "Ferretería Central", "contacto": "contacto@ferreteriacentral.com", "telefono": "+56912345678"},
            {"nombre": "Distribuidora Norte", "contacto": "ventas@distribuidoranorte.cl", "telefono": "+56987654321"},
            {"nombre": "Materiales del Sur", "contacto": "info@materialesdelsur.cl", "telefono": "+56955555555"}
        ]
        
        proveedores_creados = []
        for prov_data in proveedores_data:
            proveedor_existente = db.query(ProveedorDB).filter(ProveedorDB.nombre == prov_data["nombre"]).first()
            if not proveedor_existente:
                proveedor = ProveedorDB(**prov_data)
                db.add(proveedor)
                db.flush()
                proveedores_creados.append(proveedor)
            else:
                proveedores_creados.append(proveedor_existente)
        
        # Crear productos
        productos_data = [
            {
                "nombre": "Martillo de Carpintero",
                "descripcion": "Martillo profesional con mango de madera",
                "precio_venta": 15000,
                "cantidad_disponible": 25,
                "id_categoria": categorias_creadas[0].id_categoria,
                "id_proveedor": proveedores_creados[0].id_proveedor,
                "en_catalogo": True,
                "imagen_url": "/images/productos/martillo.jpg"
            },
            {
                "nombre": "Taladro Eléctrico",
                "descripcion": "Taladro eléctrico 500W con set de brocas",
                "precio_venta": 45000,
                "cantidad_disponible": 15,
                "id_categoria": categorias_creadas[1].id_categoria,
                "id_proveedor": proveedores_creados[1].id_proveedor,
                "en_catalogo": True,
                "imagen_url": "/images/productos/taladro.jpg"
            },
            {
                "nombre": "Cemento Portland",
                "descripcion": "Saco de cemento Portland 25kg",
                "precio_venta": 8500,
                "cantidad_disponible": 100,
                "id_categoria": categorias_creadas[2].id_categoria,
                "id_proveedor": proveedores_creados[2].id_proveedor,
                "en_catalogo": True,
                "imagen_url": "/images/productos/cemento.jpg"
            },
            {
                "nombre": "Destornillador Phillips",
                "descripcion": "Set de destornilladores Phillips profesionales",
                "precio_venta": 12000,
                "cantidad_disponible": 30,
                "id_categoria": categorias_creadas[0].id_categoria,
                "id_proveedor": proveedores_creados[0].id_proveedor,
                "en_catalogo": True,
                "imagen_url": "/images/productos/destornillador.jpg"
            },
            {
                "nombre": "Pintura Látex Blanca",
                "descripcion": "Pintura látex blanca interior/exterior 4L",
                "precio_venta": 18000,
                "cantidad_disponible": 20,
                "id_categoria": categorias_creadas[4].id_categoria,
                "id_proveedor": proveedores_creados[1].id_proveedor,
                "en_catalogo": True,
                "imagen_url": "/images/productos/pintura.jpg"
            },
            {
                "nombre": "Sierra Circular",
                "descripcion": "Sierra circular eléctrica 1200W",
                "precio_venta": 85000,
                "cantidad_disponible": 8,
                "id_categoria": categorias_creadas[1].id_categoria,
                "id_proveedor": proveedores_creados[1].id_proveedor,
                "en_catalogo": True,
                "imagen_url": "/images/productos/sierra.jpg"
            },
            {
                "nombre": "Clavos de Acero",
                "descripcion": "Clavos de acero galvanizado 2 pulgadas - 1kg",
                "precio_venta": 3500,
                "cantidad_disponible": 50,
                "id_categoria": categorias_creadas[3].id_categoria,
                "id_proveedor": proveedores_creados[0].id_proveedor,
                "en_catalogo": True,
                "imagen_url": "/images/productos/clavos.jpg"
            },
            {
                "nombre": "Llave Inglesa",
                "descripcion": "Llave inglesa ajustable 10 pulgadas",
                "precio_venta": 22000,
                "cantidad_disponible": 18,
                "id_categoria": categorias_creadas[0].id_categoria,
                "id_proveedor": proveedores_creados[2].id_proveedor,
                "en_catalogo": True,
                "imagen_url": "/images/productos/llave.jpg"
            }
        ]
        
        productos_creados = 0
        for prod_data in productos_data:
            producto_existente = db.query(ProductoDB).filter(ProductoDB.nombre == prod_data["nombre"]).first()
            if not producto_existente:
                producto = ProductoDB(**prod_data)
                db.add(producto)
                productos_creados += 1
        
        # Confirmar cambios
        db.commit()
        
        print(f"Base de datos poblada exitosamente:")
        print(f"- Categorías: {len(categorias_creadas)}")
        print(f"- Proveedores: {len(proveedores_creados)}")
        print(f"- Productos nuevos: {productos_creados}")
        
    except Exception as e:
        print(f'Error al poblar la base de datos: {str(e)}')
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    populate_database()