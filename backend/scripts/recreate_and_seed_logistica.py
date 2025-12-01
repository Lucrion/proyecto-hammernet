#!/usr/bin/env python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from seed_data import recreate_database_with_admin, seed_logistica_reparto_demo
from models.rol import RolDB
from models.usuario import UsuarioDB
from models.categoria import CategoriaDB
from models.subcategoria import SubCategoriaDB
from models.proveedor import ProveedorDB
from models.producto import ProductoDB
from config.database import SessionLocal
from core.auth import hash_contraseña
from config.database import SessionLocal

def main():
    out = recreate_database_with_admin(rut_formatted="11.111.111-1", password_plain="admin123")
    print("RECREATE:", out)
    db = SessionLocal()
    try:
        # Roles
        rol_cliente = db.query(RolDB).filter(RolDB.nombre == 'cliente').first()
        if not rol_cliente:
            rol_cliente = RolDB(nombre='cliente')
            db.add(rol_cliente)
            db.flush()
        # Usuarios cliente
        for i in [12000001, 12000002, 12000003]:
            u = db.query(UsuarioDB).filter(UsuarioDB.rut == i).first()
            if not u:
                u = UsuarioDB(nombre=f"Cliente {i}", apellido="Demo", rut=i, email=f"cliente{i}@mail.com", telefono="+56990000000", password=hash_contraseña("demo123"), id_rol=rol_cliente.id_rol, activo=True)
                db.add(u)
        # Cat/Subcat/Proveedor
        cat = db.query(CategoriaDB).filter(CategoriaDB.nombre == 'Herramientas').first()
        if not cat:
            cat = CategoriaDB(nombre='Herramientas', descripcion='Herramientas')
            db.add(cat)
            db.flush()
        sub = db.query(SubCategoriaDB).filter(SubCategoriaDB.nombre == 'Taladros').first()
        if not sub:
            sub = SubCategoriaDB(nombre='Taladros', descripcion='Taladros', id_categoria=cat.id_categoria)
            db.add(sub)
            db.flush()
        prov = db.query(ProveedorDB).filter(ProveedorDB.nombre == 'Acme Tools').first()
        if not prov:
            prov = ProveedorDB(nombre='Acme Tools', telefono='+56922223333', correo='ventas@acme.com')
            db.add(prov)
            db.flush()
        # Productos
        for code, name, price in [('TL-800W','Taladro Percutor 800W', 59990), ('MA-16OZ','Martillo 16oz', 12990)]:
            p = db.query(ProductoDB).filter(ProductoDB.codigo_interno == code).first()
            if not p:
                p = ProductoDB(
                    nombre=name,
                    descripcion=name,
                    codigo_interno=code,
                    imagen_url=f"https://picsum.photos/seed/{code}/600/600",
                    id_categoria=cat.id_categoria,
                    id_subcategoria=sub.id_subcategoria,
                    id_proveedor=prov.id_proveedor,
                    marca='Genérica',
                    precio_venta=price,
                    cantidad_disponible=50,
                    stock_minimo=3,
                    estado='activo',
                    en_catalogo=True,
                )
                db.add(p)
        db.commit()
        resumen = seed_logistica_reparto_demo(db, ventas=10)
        print("SEED:", resumen)
    finally:
        db.close()

if __name__ == "__main__":
    main()
