#!/usr/bin/env python3
"""
Script para actualizar el stock de un producto específico.
Usa la misma configuración que otros utilitarios: intenta usar DATABASE_URL
si existe, en caso contrario usa el archivo SQLite local `ferreteria.db`.
"""

import os
from datetime import datetime
from sqlalchemy import create_engine, text


def get_database_url():
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return db_url
    # Fallback a SQLite local en el backend
    return "sqlite:///ferreteria.db"


def update_stock(product_id: int, increment: int):
    db_url = get_database_url()
    engine = create_engine(db_url)

    print("Actualizando stock de producto...")
    print("=" * 50)
    print(f"DB: {db_url}")
    print(f"Producto ID: {product_id}, Incremento: {increment}")

    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # Obtener stock actual
            result = conn.execute(text(
                "SELECT nombre, cantidad_disponible FROM productos WHERE id_producto = :pid"
            ), {"pid": product_id}).fetchone()

            if not result:
                print("❌ Producto no encontrado")
                return

            nombre, stock_actual = result
            print(f"Producto: {nombre} | Stock actual: {stock_actual}")

            nuevo_stock = (stock_actual or 0) + increment
            conn.execute(text(
                "UPDATE productos SET cantidad_disponible = :nuevo, fecha_actualizacion = :fecha WHERE id_producto = :pid"
            ), {"nuevo": nuevo_stock, "fecha": datetime.now(), "pid": product_id})

            trans.commit()
            print(f"✅ Stock actualizado: {stock_actual} → {nuevo_stock}")
        except Exception as e:
            trans.rollback()
            print(f"❌ Error actualizando stock: {e}")
            raise


if __name__ == "__main__":
    # Valores por defecto: producto 1, incremento +5
    pid = int(os.getenv("PRODUCT_ID", "1"))
    inc = int(os.getenv("INCREMENT", "5"))
    update_stock(pid, inc)