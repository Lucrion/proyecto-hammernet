#!/usr/bin/env python3
import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from sqlalchemy.orm import Session
from config.database import SessionLocal, engine
from models.base import Base
from models.rol import RolDB
from models.permiso import PermisoDB
from models.rol_permiso import RolPermisoDB
from models.usuario import UsuarioDB
from core.auth import hash_contraseña


def run():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        perms = [
            "usuarios",
            "catalogo",
            "inventario",
            "ventas",
            "pagos",
            "auditoria",
            "dashboard",
            "proveedores",
            "categorias",
            "subcategorias",
            "despachos",
        ]
        created_perms = {}
        for name in perms:
            p = db.query(PermisoDB).filter(PermisoDB.descripcion == name).first()
            if not p:
                p = PermisoDB(descripcion=name)
                db.add(p)
                db.flush()
            created_perms[name] = p.id_permiso

        roles = ["administrador", "vendedor", "bodeguero", "cliente"]
        created_roles = {}
        for rname in roles:
            r = db.query(RolDB).filter(RolDB.nombre == rname).first()
            if not r:
                r = RolDB(nombre=rname)
                db.add(r)
                db.flush()
            created_roles[rname] = r.id_rol

        admin_id = created_roles.get("administrador")
        if admin_id:
            for pid in created_perms.values():
                rp = db.query(RolPermisoDB).filter(RolPermisoDB.id_rol == admin_id, RolPermisoDB.id_permiso == pid).first()
                if not rp:
                    db.add(RolPermisoDB(id_rol=admin_id, id_permiso=pid))

        rut_admin = "203477937"
        user = db.query(UsuarioDB).filter(UsuarioDB.rut == rut_admin).first()
        if not user:
            user = UsuarioDB(
                nombre="Administrador",
                apellido=None,
                rut=rut_admin,
                email=os.getenv("ADMIN_EMAIL", "admin@localhost"),
                telefono=None,
                password=hash_contraseña("123"),
                id_rol=admin_id,
                activo=True,
            )
            db.add(user)
        else:
            user.id_rol = admin_id
            user.activo = True
        db.commit()
        print("OK")
    except Exception as e:
        db.rollback()
        print(f"ERR: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    run()
