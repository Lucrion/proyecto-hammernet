#!/usr/bin/env python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from sqlalchemy.orm import Session, joinedload
from backend.config.database import SessionLocal
from backend.controllers.venta_controller import VentaController
from backend.models.venta import VentaDB, DetalleVentaDB

def main():
    db: Session = SessionLocal()
    try:
        vdb = (
            db.query(VentaDB)
            .options(joinedload(VentaDB.usuario), joinedload(VentaDB.detalles_venta).joinedload(DetalleVentaDB.producto))
            .order_by(VentaDB.id_venta.desc())
            .first()
        )
        if not vdb:
            print("NO_VENTAS")
            return
        v = VentaController._construir_venta_response(vdb)
        print({
            "id_venta": v.id_venta,
            "cliente_rut": v.cliente_rut,
            "cliente_nombre": v.cliente_nombre,
            "repartidor_rut": v.repartidor_rut,
            "repartidor_nombre": v.repartidor_nombre,
            "usuario_rut": v.rut_usuario,
            "usuario_nombre": v.usuario_nombre,
            "estado_envio": v.estado_envio,
            "metodo_entrega": v.metodo_entrega,
        })
    finally:
        db.close()

if __name__ == "__main__":
    main()

