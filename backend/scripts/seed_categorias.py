#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de seeding de categorías.
Inserta una lista de categorías por defecto si no existen.
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


DEFAULT_CATEGORIES = [
    "Herramientas",
    "Construcción",
    "Jardinería y Exteriores",
    "Electricidad",
    "Plomería",
    "Seguridad",
    "Hogar y Limpieza",
    "Pinturas",
    "Tornillos y Clavos",
]


def ensure_tables():
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"[seed] Error al crear/verificar tablas: {e}")


def seed_categories():
    db = SessionLocal()
    try:
        existentes = {c.nombre for c in db.query(CategoriaDB).all()}
        nuevos = [c for c in DEFAULT_CATEGORIES if c not in existentes]

        for nombre in nuevos:
            db.add(CategoriaDB(nombre=nombre, descripcion=None))

        if nuevos:
            db.commit()
            print(f"[seed] Categorías insertadas: {', '.join(nuevos)}")
        else:
            print("[seed] No hay categorías nuevas para insertar; ya existen.")
    except Exception as e:
        db.rollback()
        print(f"[seed] Error al insertar categorías: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    ensure_tables()
    seed_categories()