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
import random


def seed_20_ejemplos_por_tabla(db):
    """Inserta 20 ejemplos en las tablas principales (usuarios, proveedores,
    categorías, subcategorías, productos) y genera 20 ventas con pago y despacho.
    Evita duplicados por claves naturales (rut, nombre, código interno).
    """
    resumen = {}

    # 1) Usuarios
    usuarios_insertados = 0
    for i in range(1, 21):
        rut = 20000000 + i
        existente = db.query(UsuarioDB).filter(UsuarioDB.rut == rut).first()
        if existente:
            continue
        u = UsuarioDB(
            nombre=f"Usuario {i}",
            apellido=f"Demo {i}",
            rut=rut,
            email=f"usuario{i}@example.com",
            telefono=f"+5697{str(i).zfill(7)}",
            password=hash_contraseña("demo123"),
            role="cliente",
            activo=True,
        )
        db.add(u)
        usuarios_insertados += 1
    db.flush()
    resumen["usuarios_demo_insertados"] = usuarios_insertados

    # 2) Proveedores
    proveedores_insertados = 0
    proveedores_ids = []
    for i in range(1, 21):
        nombre = f"Proveedor Demo {i}"
        existente = db.query(ProveedorDB).filter(ProveedorDB.nombre == nombre).first()
        if existente:
            proveedores_ids.append(existente.id_proveedor)
            continue
        p = ProveedorDB(
            nombre=nombre,
            telefono=f"+5698{str(i).zfill(7)}",
            correo=f"proveedor{i}@example.com",
        )
        db.add(p)
        db.flush()
        proveedores_ids.append(p.id_proveedor)
        proveedores_insertados += 1
    resumen["proveedores_demo_insertados"] = proveedores_insertados

    # 3) Categorías
    categorias_insertadas = 0
    cat_ids = []
    for i in range(1, 21):
        nombre = f"Categoria Demo {i}"
        existente = db.query(CategoriaDB).filter(CategoriaDB.nombre == nombre).first()
        if existente:
            cat_ids.append(existente.id_categoria)
            continue
        c = CategoriaDB(nombre=nombre, descripcion=f"Descripción {nombre}")
        db.add(c)
        db.flush()
        cat_ids.append(c.id_categoria)
        categorias_insertadas += 1
    resumen["categorias_demo_insertadas"] = categorias_insertadas

    # 4) Subcategorías
    subcategorias_insertadas = 0
    sub_ids = []
    for i in range(1, 21):
        nombre = f"Subcategoria Demo {i}"
        existente = db.query(SubCategoriaDB).filter(SubCategoriaDB.nombre == nombre).first()
        if existente:
            sub_ids.append(existente.id_subcategoria)
            continue
        cat_id = cat_ids[(i - 1) % len(cat_ids)]
        s = SubCategoriaDB(nombre=nombre, descripcion=f"Descripción {nombre}", id_categoria=cat_id)
        db.add(s)
        db.flush()
        sub_ids.append(s.id_subcategoria)
        subcategorias_insertadas += 1
    resumen["subcategorias_demo_insertadas"] = subcategorias_insertadas

    # 5) Productos
    productos_insertados = 0
    producto_ids = []
    for i in range(1, 21):
        codigo = f"PRD-EX-{str(i).zfill(3)}"
        existente = db.query(ProductoDB).filter(ProductoDB.codigo_interno == codigo).first()
        if existente:
            producto_ids.append(existente.id_producto)
            continue
        cat_id = cat_ids[(i - 1) % len(cat_ids)]
        sub_id = sub_ids[(i - 1) % len(sub_ids)]
        prov_id = proveedores_ids[(i - 1) % len(proveedores_ids)]
        precio = 4990 + 1000 * (i % 10)
        cantidad = 5 + (i % 7)
        p = ProductoDB(
            nombre=f"Producto Ejemplo {i}",
            descripcion=f"Descripción del producto ejemplo {i}",
            codigo_interno=codigo,
            imagen_url=f"https://picsum.photos/seed/{codigo}/600/600",
            id_categoria=cat_id,
            id_subcategoria=sub_id,
            id_proveedor=prov_id,
            marca=f"Marca {((i-1)%5)+1}",
            precio_venta=Decimal(str(precio)),
            cantidad_disponible=cantidad,
            stock_minimo=1,
            estado="activo",
            en_catalogo=True,
            caracteristicas=f"Llave: {i}; Color: Negro; Modelo: DEMO-{i}",
        )
        db.add(p)
        db.flush()
        producto_ids.append(p.id_producto)
        productos_insertados += 1
    resumen["productos_demo_insertados"] = productos_insertados

    db.commit()

    # 6) Ventas + Detalles + Pagos + Despachos + Movimientos
    ventas_insertadas = 0
    for i in range(1, 21):
        # Seleccionar usuario y producto
        usr = db.query(UsuarioDB).filter(UsuarioDB.rut == (20000000 + i)).first() or db.query(UsuarioDB).first()
        prod_id = producto_ids[(i - 1) % len(producto_ids)] if producto_ids else None
        producto = db.query(ProductoDB).filter(ProductoDB.id_producto == prod_id).first() if prod_id else None
        if not usr or not producto:
            continue

        cantidad = 1 + (i % 3)
        precio_unitario = Decimal(str(producto.precio_venta or 0))
        subtotal = precio_unitario * cantidad

        venta = VentaDB(
            id_usuario=usr.id_usuario,
            total_venta=subtotal,
            estado="completada",
            observaciones=f"Venta demo #{i}",
            tipo_documento="boleta",
            folio_documento=f"B-{str(i).zfill(6)}",
            fecha_emision_sii=date.today(),
            cliente_id=usr.id_usuario,
        )
        db.add(venta)
        db.flush()

        detalle = DetalleVentaDB(
            id_venta=venta.id_venta,
            id_producto=producto.id_producto,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            subtotal=subtotal,
        )
        db.add(detalle)

        # Actualizar inventario y movimiento
        anterior = int(producto.cantidad_disponible or 0)
        nuevo = max(0, anterior - cantidad)
        producto.cantidad_disponible = nuevo
        producto.fecha_ultima_venta = datetime.now()

        mov = MovimientoInventarioDB(
            id_producto=producto.id_producto,
            id_usuario=usr.id_usuario,
            id_venta=venta.id_venta,
            tipo_movimiento="venta",
            cantidad=-cantidad,
            cantidad_anterior=anterior,
            cantidad_nueva=nuevo,
            motivo=f"Venta demo #{venta.id_venta}",
        )
        db.add(mov)

        # Despacho
        despacho = DespachoDB(
            id_usuario=usr.id_usuario,
            buscar="retiro_tienda",
            calle="",
            numero="",
            depto=None,
            adicional=f"Retiro demo #{i}",
        )
        db.add(despacho)

        # Pago
        pago = PagoDB(
            id_venta=venta.id_venta,
            proveedor="webpay",
            estado="aprobado",
            monto=subtotal,
            token=f"TOK-DEMO-{venta.id_venta}-{i}",
            payment_method="tarjeta_credito",
        )
        db.add(pago)

        # Auditoría
        aud = AuditoriaDB(
            entidad_tipo="venta",
            entidad_id=venta.id_venta,
            accion="venta_demo_creada",
            usuario_id=usr.id_usuario,
            detalle=f"Seed: venta demo #{i}",
        )
        db.add(aud)

        ventas_insertadas += 1

    db.commit()
    resumen["ventas_demo_insertadas"] = ventas_insertadas

    return resumen


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
        {
            "nombre": "Martillo Forjado 16oz",
            "descripcion": "Martillo de carpintero con mango antideslizante",
            "codigo_interno": "MA-16OZ",
            "imagen_url": "https://picsum.photos/seed/MA-16OZ/600/600",
            "id_categoria": cat_map["Herramientas"],
            "id_subcategoria": sub_map["Taladros"],
            "id_proveedor": prov.id_proveedor,
            "marca": "Truper",
            "precio_venta": 12990,
            "cantidad_disponible": 40,
            "stock_minimo": 5,
            "estado": "activo",
            "en_catalogo": True,
            "caracteristicas": "Peso: 16oz; Mango: antideslizante; Cabeza: acero forjado; Longitud: 32cm"
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


def seed_mas_productos_catalogo(db, cantidad=60):
    """Agrega productos extra al catálogo para pruebas de listado/paginación.
    Evita duplicados por "codigo_interno".
    """
    insertados = 0

    # Asegurar que existan categorías, subcategorías y proveedores
    categorias = db.query(CategoriaDB).all()
    if not categorias:
        for i in range(1, 4):
            c = CategoriaDB(nombre=f"Categoría Extra {i}", descripcion="Generada para pruebas")
            db.add(c)
            db.flush()
            for j in range(1, 3):
                s = SubCategoriaDB(id_categoria=c.id_categoria, nombre=f"Subcategoría Extra {i}-{j}", descripcion="Generada para pruebas")
                db.add(s)
        db.commit()
        categorias = db.query(CategoriaDB).all()

    subcategorias = db.query(SubCategoriaDB).all()
    if not subcategorias:
        # Crear al menos algunas subcategorías para la primera categoría
        primera = categorias[0]
        for j in range(1, 4):
            s = SubCategoriaDB(id_categoria=primera.id_categoria, nombre=f"Subcategoría Base {j}", descripcion="Generada para pruebas")
            db.add(s)
        db.commit()
        subcategorias = db.query(SubCategoriaDB).all()

    proveedores = db.query(ProveedorDB).all()
    if not proveedores:
        for i in range(1, 4):
            p = ProveedorDB(nombre=f"Proveedor Extra {i}", telefono=f"+5692000{i:03d}", correo=f"extra{i}@proveedor.com")
            db.add(p)
        db.commit()
        proveedores = db.query(ProveedorDB).all()

    cat_ids = [c.id_categoria for c in categorias]
    sub_ids = subcategorias
    prov_ids = [p.id_proveedor for p in proveedores] if proveedores else [None]

    for i in range(1, cantidad + 1):
        codigo = f"PRD-EXTRA-{i:03d}"
        ya = db.query(ProductoDB).filter(ProductoDB.codigo_interno == codigo).first()
        if ya:
            continue

        cat_id = random.choice(cat_ids)
        subs_de_cat = [s.id_subcategoria for s in sub_ids if s.id_categoria == cat_id]
        sub_id = random.choice(subs_de_cat) if subs_de_cat else None
        prov_id = random.choice(prov_ids) if prov_ids else None

        precio = Decimal(str(random.randint(4990, 49990)))
        cantidad_disp = random.randint(5, 150)

        prod = ProductoDB(
            nombre=f"Producto Extra {i}",
            descripcion="Generado para pruebas de catálogo y paginación",
            codigo_interno=codigo,
            imagen_url=f"https://picsum.photos/seed/extra{i}/600/600",
            id_categoria=cat_id,
            id_subcategoria=sub_id,
            id_proveedor=prov_id,
            marca="Genérica",
            precio_venta=precio,
            cantidad_disponible=cantidad_disp,
            stock_minimo=random.randint(1, 10),
            estado="activo",
            en_catalogo=True,
            caracteristicas="Durable, confiable, apto para uso diario",
        )
        db.add(prod)
        insertados += 1

        if insertados % 50 == 0:
            db.commit()

    db.commit()
    return insertados


def main():
    db = SessionLocal()
    try:
        resumen = {}
        resumen.update(seed_usuarios(db))
        resumen.update(seed_catalogo_y_productos(db))
        resumen.update(seed_venta_simple(db))
        resumen.update(seed_despacho_y_pago(db))
        # Insertar 20 ejemplos por tabla
        resumen.update(seed_20_ejemplos_por_tabla(db))
        # Agregar más productos al catálogo para probar la paginación
        extras = seed_mas_productos_catalogo(db, cantidad=60)
        resumen["productos_extra_catalogo"] = extras
        print(resumen)
    finally:
        db.close()


if __name__ == "__main__":
    main()