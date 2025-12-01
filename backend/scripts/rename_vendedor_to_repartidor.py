#!/usr/bin/env python3
import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from sqlalchemy.orm import Session
from config.database import SessionLocal, engine
from models.base import Base
from models.usuario import UsuarioDB
from models.rol import RolDB


def run():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        vend = db.query(RolDB).filter(RolDB.nombre == 'vendedor').first()
        rep = db.query(RolDB).filter(RolDB.nombre == 'repartidor').first()
        if not rep:
            rep = RolDB(nombre='repartidor')
            db.add(rep)
            db.flush()
        if vend:
            # Reasignar usuarios con rol vendedor a repartidor
            usuarios = db.query(UsuarioDB).filter(UsuarioDB.id_rol == vend.id_rol).all()
            for u in usuarios:
                u.id_rol = rep.id_rol
            # Opcional: renombrar rol vendedor a legacy
            vend.nombre = 'vendedor_legacy'
        db.commit()
        print('OK')
    except Exception as e:
        db.rollback()
        print('ERR:', e)
    finally:
        db.close()


if __name__ == '__main__':
    run()
