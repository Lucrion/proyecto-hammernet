#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de diagnóstico para verificar registros en las tablas 'ventas' y 'detalles_venta'.
Usa la configuración existente de SQLAlchemy para conectarse a la base de datos.
"""

from sqlalchemy import text
from config.database import engine

def main():
    print("\n=== Diagnóstico de ventas ===\n")
    print(f"Motor: {engine.dialect.name}")

    with engine.begin() as conn:
        # Contadores
        try:
            ventas_count = conn.execute(text("SELECT COUNT(*) FROM ventas")).scalar() or 0
        except Exception as e:
            print(f"Error consultando 'ventas': {e}")
            ventas_count = None

        try:
            detalles_count = conn.execute(text("SELECT COUNT(*) FROM detalles_venta")).scalar() or 0
        except Exception as e:
            print(f"Error consultando 'detalles_venta': {e}")
            detalles_count = None

        print(f"Ventas: {ventas_count}")
        print(f"Detalles de venta: {detalles_count}\n")

        # Últimas ventas
        if ventas_count and ventas_count > 0:
            ventas = conn.execute(text(
                """
                SELECT id_venta, id_usuario, total_venta, estado, fecha_venta
                FROM ventas
                ORDER BY id_venta DESC
                LIMIT 5
                """
            )).fetchall()

            for v in ventas:
                print(f"Venta #{v.id_venta} | usuario={v.id_usuario} | total={v.total_venta} | estado={v.estado} | fecha={v.fecha_venta}")
                detalles = conn.execute(text(
                    """
                    SELECT id_detalle, id_producto, cantidad, precio_unitario, subtotal
                    FROM detalles_venta
                    WHERE id_venta = :id
                    ORDER BY id_detalle ASC
                    """
                ), {"id": v.id_venta}).fetchall()

                if not detalles:
                    print("  - Sin detalles asociados")
                else:
                    for d in detalles:
                        print(f"  - Detalle #{d.id_detalle} | prod={d.id_producto} | cant={d.cantidad} | unit={d.precio_unitario} | sub={d.subtotal}")
            print()
        else:
            print("No hay ventas registradas aún.")

if __name__ == "__main__":
    main()