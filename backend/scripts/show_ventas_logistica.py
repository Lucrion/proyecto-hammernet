#!/usr/bin/env python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from sqlalchemy.orm import Session
from backend.config.database import SessionLocal
from backend.models.venta import VentaDB
from backend.models.despacho import DespachoDB
from backend.models.usuario import UsuarioDB

def main():
    db: Session = SessionLocal()
    try:
        ventas = (
            db.query(VentaDB)
            .order_by(VentaDB.id_venta.desc())
            .limit(10)
            .all()
        )
        for v in ventas:
            rep = db.query(UsuarioDB).filter(UsuarioDB.rut == v.repartidor_rut).first() if v.repartidor_rut else None
            dir = db.query(DespachoDB).filter(DespachoDB.id_despacho == v.despacho_id).first() if v.despacho_id else None
            print(f"Venta {v.id_venta}: estado={v.estado} envio={v.estado_envio} metodo={v.metodo_entrega} total={v.total_venta}")
            print(f"  cliente_rut={v.cliente_rut} repartidor_rut={v.repartidor_rut} repartidor={getattr(rep,'nombre',None)}")
            print(f"  ventana={v.ventana_inicio}..{v.ventana_fin} eta={v.eta}")
            print(f"  fechas asignacion={v.fecha_asignacion} despacho={v.fecha_despacho} entrega={v.fecha_entrega}")
            print(f"  pod_url={v.prueba_entrega_url} geo=({v.geo_entrega_lat},{v.geo_entrega_lng}) motivo_no_entrega={v.motivo_no_entrega}")
            if dir:
                print(f"  despacho: {dir.buscar} | {dir.calle} {dir.numero}")
            print("---")
    finally:
        db.close()

if __name__ == "__main__":
    main()

