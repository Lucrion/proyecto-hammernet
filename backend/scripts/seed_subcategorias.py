#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Seed de subcategorías por categorías existentes.

- Inserta subcategorías de ejemplo mapeadas por nombre de categoría.
- Es idempotente: no duplica si ya existen (por nombre + id_categoria).
"""

import os
import sys

# Asegurar que el directorio raíz de backend esté en sys.path
CURRENT_DIR = os.path.dirname(__file__)
BACKEND_ROOT = os.path.dirname(CURRENT_DIR)
if BACKEND_ROOT not in sys.path:
    sys.path.append(BACKEND_ROOT)

from config.database import SessionLocal, engine
from models.base import Base
from models.categoria import CategoriaDB
from models.subcategoria import SubCategoriaDB


# Mapeos soportando distintas denominaciones de categorías
CATEGORY_SUBCATS = {
    # Conjunto 1 (seed_categorias.py)
    "Herramientas": ["Martillos", "Destornilladores", "Llaves", "Alicates"],
    "Construcción": ["Cemento", "Arena", "Yeso", "Ladrillos"],
    "Jardinería y Exteriores": ["Podadoras", "Mangueras", "Riego", "Fertilizantes"],
    "Electricidad": ["Cables", "Interruptores", "Enchufes", "Iluminación"],
    "Plomería": ["Tuberías", "Válvulas", "Grifería", "Accesorios"],
    "Seguridad": ["Candados", "CCTV", "Alarmas", "Guantes y Protección"],
    "Hogar y Limpieza": ["Detergentes", "Escobas", "Organizadores", "Bolsas de Basura"],
    "Pinturas": ["Pintura Látex", "Esmaltes", "Barnices", "Brochas y Rodillos"],
    "Tornillos y Clavos": ["Tornillos", "Clavos", "Tarugos", "Anclajes"],
    # Conjunto 2 (populate_db.py)
    "Herramientas Manuales": ["Martillos", "Destornilladores", "Llaves", "Alicates"],
    "Herramientas Eléctricas": ["Taladros", "Sierras", "Lijadoras", "Pulidoras"],
    "Materiales de Construcción": ["Cemento", "Arena", "Yeso", "Ladrillos"],
    "Ferretería General": ["Tornillos", "Clavos", "Tarugos", "Anclajes"],
    "Pinturas y Acabados": ["Pintura Látex", "Esmaltes", "Barnices", "Brochas y Rodillos"],
}


def ensure_tables():
    """Crea tablas si no existen."""
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"[seed-subcats] Error al crear/verificar tablas: {e}")


def seed_subcategories():
    """Inserta subcategorías de ejemplo por categoría existente."""
    db = SessionLocal()
    try:
        categorias = db.query(CategoriaDB).all()
        if not categorias:
            print("[seed-subcats] No hay categorías en la base. Ejecuta seed_categorias.py o populate_db.py primero.")
            return

        total_insertadas = 0
        for cat in categorias:
            nombres = CATEGORY_SUBCATS.get(cat.nombre)
            if not nombres:
                # Saltar categorías sin mapeo
                continue

            # Obtener subcategorías existentes por nombre para esta categoría
            existentes = {
                s.nombre for s in db.query(SubCategoriaDB).filter(SubCategoriaDB.id_categoria == cat.id_categoria).all()
            }

            nuevas = [n for n in nombres if n not in existentes]
            for nombre_sub in nuevas:
                db.add(SubCategoriaDB(
                    id_categoria=cat.id_categoria,
                    nombre=nombre_sub,
                    descripcion=None
                ))
                total_insertadas += 1

        if total_insertadas:
            db.commit()
            print(f"[seed-subcats] Subcategorías insertadas: {total_insertadas}")
        else:
            print("[seed-subcats] No hay subcategorías nuevas para insertar; ya existen.")
    except Exception as e:
        db.rollback()
        print(f"[seed-subcats] Error al insertar subcategorías: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    ensure_tables()
    seed_subcategories()