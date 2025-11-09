import asyncio
from datetime import datetime, date
from decimal import Decimal

from config.database import SessionLocal
from core.auth import hash_contraseña

from models.usuario import UsuarioDB
from models.proveedor import ProveedorDB
from models.categoria import CategoriaDB
from models.subcategoria import SubCategoriaDB
from models.producto import ProductoDB
from models.venta import VentaDB, DetalleVentaDB, MovimientoInventarioDB
from models.despacho import DespachoDB
from models.pago import PagoDB
from models.auditoria import AuditoriaDB


def seed_usuarios(db):
    """Inserta usuarios de ejemplo sin username, usando rut y email"""
    usuarios = [
        {
            "nombre": "Administrador",
            "apellido": None,
            "rut": 11111111,
            "email": "admin@localhost",
            "telefono": None,
            "password": hash_contraseña("admin123"),
            "role": "administrador",
            "activo": True,
        },
        {
            "nombre": "María",
            "apellido": "Pérez",
            "rut": 12345678,
            "email": "maria@example.com",
            "telefono": "+56911112222",
            "password": hash_contraseña("maria123"),
            "role": "cliente",
            "activo": True,
        },
    ]

    insertados = 0
    for u in usuarios:
        ya = db.query(UsuarioDB).filter(UsuarioDB.rut == u["rut"]).first()
        if ya:
            continue
        db.add(UsuarioDB(**u))
        insertados += 1
    db.commit()
    return {"usuarios_insertados": insertados}


def seed_catalogo_y_productos(db):
    """Inserta categorías, subcategorías, proveedor y productos de ejemplo"""
    # Categorías
    cats = [
        {"nombre": "Herramientas", "descripcion": "Herramientas manuales y eléctricas"},
        {"nombre": "Electricidad", "descripcion": "Materiales y accesorios eléctricos"},
    ]
    cat_map = {}
    for c in cats:
        ex = db.query(CategoriaDB).filter(CategoriaDB.nombre == c["nombre"]).first()
        if not ex:
            ex = CategoriaDB(**c)
            db.add(ex)
            db.flush()
        cat_map[c["nombre"]] = ex.id_categoria

    # Subcategorías
    subs = [
        {"nombre": "Taladros", "descripcion": "Taladros y atornilladores", "categoria": "Herramientas"},
        {"nombre": "Iluminación", "descripcion": "Luminarias y focos", "categoria": "Electricidad"},
    ]
    sub_map = {}
    for s in subs:
        ex = db.query(SubCategoriaDB).filter(SubCategoriaDB.nombre == s["nombre"]).first()
        if not ex:
            ex = SubCategoriaDB(nombre=s["nombre"], descripcion=s.get("descripcion"), id_categoria=cat_map[s["categoria"]])
            db.add(ex)
            db.flush()
        sub_map[s["nombre"]] = ex.id_subcategoria

    # Proveedor
    prov = db.query(ProveedorDB).filter(ProveedorDB.nombre == "Acme Tools").first()
    if not prov:
        prov = ProveedorDB(nombre="Acme Tools", telefono="+56922223333", correo="ventas@acme.com")
        db.add(prov)
        db.flush()

    # Productos
    productos = [
        {
            "nombre": "Taladro Percutor 800W",
            "descripcion": "Taladro percutor con velocidad variable",
            "codigo_interno": "TL-800W",
            "imagen_url": "https://picsum.photos/seed/TL-800W/600/600",
            "id_categoria": cat_map["Herramientas"],
            "id_subcategoria": sub_map["Taladros"],
            "id_proveedor": prov.id_proveedor,
            "marca": "Bosch",
            "precio_venta": 59990,
            "cantidad_disponible": 15,
            "stock_minimo": 3,
            "estado": "activo",
            "en_catalogo": True,
            "caracteristicas": '{"potencia":"800W","velocidades":2,"incluye":"Maletín"}'
        },
        {
            "nombre": "Foco LED 20W Exterior",
            "descripcion": "Proyector LED IP65",
            "codigo_interno": "FO-20W",
            "imagen_url": "https://picsum.photos/seed/FO-20W/600/600",
            "id_categoria": cat_map["Electricidad"],
            "id_subcategoria": sub_map["Iluminación"],
            "id_proveedor": prov.id_proveedor,
            "marca": "Osram",
            "precio_venta": 19990,
            "cantidad_disponible": 30,
            "stock_minimo": 5,
            "estado": "activo",
            "en_catalogo": True,
            "caracteristicas": '{"potencia":"20W","proteccion":"IP65"}'
        },
    ]

    insertados = 0
    for p in productos:
        ya = None
        if p.get("codigo_interno"):
            ya = db.query(ProductoDB).filter(ProductoDB.codigo_interno == p["codigo_interno"]).first()
        if ya:
            continue
        db.add(ProductoDB(**p))
        insertados += 1
    db.commit()
    return {"productos_insertados": insertados, "categorias": cat_map, "subcategorias": sub_map, "proveedor": prov.nombre}


def seed_venta_simple(db):
    """Crea una venta de ejemplo para el usuario con RUT 12345678-9"""
    usuario = db.query(UsuarioDB).filter(UsuarioDB.rut == 12345678).first()
    producto = db.query(ProductoDB).filter(ProductoDB.codigo_interno == "TL-800W").first()
    if not usuario or not producto:
        return {"venta": "omitida"}

    # Calcular subtotal y total
    precio = Decimal(str(producto.precio_venta or 0))
    cantidad = 2
    subtotal = precio * cantidad

    venta = VentaDB(
        id_usuario=usuario.id_usuario,
        total_venta=subtotal,
        estado="completada",
        observaciones="Venta de ejemplo",
        tipo_documento="boleta",
        folio_documento="B-000001",
        fecha_emision_sii=date.today(),
        cliente_id=usuario.id_usuario,
    )
    db.add(venta)
    db.flush()

    detalle = DetalleVentaDB(
        id_venta=venta.id_venta,
        id_producto=producto.id_producto,
        cantidad=cantidad,
        precio_unitario=precio,
        subtotal=subtotal,
    )
    db.add(detalle)

    # Actualizar inventario y registrar movimiento
    anterior = producto.cantidad_disponible
    nuevo = anterior - cantidad
    producto.cantidad_disponible = nuevo
    producto.fecha_ultima_venta = datetime.now()

    mov = MovimientoInventarioDB(
        id_producto=producto.id_producto,
        id_usuario=usuario.id_usuario,
        id_venta=venta.id_venta,
        tipo_movimiento="venta",
        cantidad=-cantidad,
        cantidad_anterior=anterior,
        cantidad_nueva=nuevo,
        motivo=f"Venta #{venta.id_venta}",
    )
    db.add(mov)
    db.commit()

    return {"venta_id": venta.id_venta, "detalle": detalle.id_detalle}


def seed_despacho_y_pago(db):
    """Crea despacho y pago de ejemplo asociados a la venta previa"""
    venta = db.query(VentaDB).order_by(VentaDB.id_venta.desc()).first()
    usuario = db.query(UsuarioDB).filter(UsuarioDB.rut == 12345678).first()
    if not venta or not usuario:
        return {"despacho_pago": "omitidos"}

    # Despacho: retiro en tienda
    despacho = DespachoDB(
        id_usuario=usuario.id_usuario,
        buscar="retiro_tienda",
        calle="",
        numero="",
        depto=None,
        adicional="Retiro en tienda",
    )
    db.add(despacho)

    # Pago
    pago = PagoDB(
        id_venta=venta.id_venta,
        proveedor="webpay",
        estado="aprobado",
        monto=venta.total_venta,
        token=f"TOK-{venta.id_venta}-001",
        payment_method="tarjeta_credito",
    )
    db.add(pago)

    # Auditoría
    aud = AuditoriaDB(
        entidad_tipo="venta",
        entidad_id=venta.id_venta,
        accion="venta_creada",
        usuario_id=usuario.id_usuario,
        detalle="Seed: venta y pago de ejemplo",
    )
    db.add(aud)

    db.commit()
    return {"despacho_id": despacho.id_despacho, "pago_id": pago.id_pago}


def main():
    db = SessionLocal()
    try:
        resumen = {}
        resumen.update(seed_usuarios(db))
        resumen.update(seed_catalogo_y_productos(db))
        resumen.update(seed_venta_simple(db))
        resumen.update(seed_despacho_y_pago(db))
        print(resumen)
    finally:
        db.close()


if __name__ == "__main__":
    main()