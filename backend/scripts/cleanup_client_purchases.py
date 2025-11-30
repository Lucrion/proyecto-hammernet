#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config.database import SessionLocal
from controllers.venta_controller import VentaController

def run():
    db = SessionLocal()
    try:
        res = VentaController.eliminar_compras_de_clientes(db)
        print(res)
    finally:
        db.close()

if __name__ == "__main__":
    run()

