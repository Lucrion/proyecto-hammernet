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
from models.mensaje import MensajeContactoDB
from models.rol import RolDB
from models.permiso import PermisoDB
from models.rol_permiso import RolPermisoDB
from decimal import Decimal
import random
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


def seed_ferreteria_15_realistas(db):
    """Inserta 15 productos de ferretería realistas con categorías,
    subcategorías y proveedores. Marca los productos como activos y en catálogo.
    Evita duplicados por nombre/código.
    """
    resumen = {}

    # Categorías base
    categorias_def = [
        {"nombre": "Herramientas", "descripcion": "Herramientas manuales y eléctricas"},
        {"nombre": "Electricidad", "descripcion": "Materiales y accesorios eléctricos"},
        {"nombre": "Plomería", "descripcion": "Tubos, fittings y grifería"},
        {"nombre": "Construcción", "descripcion": "Materiales y fijaciones"},
        {"nombre": "Jardinería", "descripcion": "Riego y mantenimiento de jardín"},
    ]
    cat_map = {}
    for c in categorias_def:
        ex = db.query(CategoriaDB).filter(CategoriaDB.nombre == c["nombre"]).first()
        if not ex:
            ex = CategoriaDB(**c)
            db.add(ex)
            db.flush()
        cat_map[c["nombre"]] = ex.id_categoria
    resumen["categorias_insertadas"] = len(categorias_def)

    # Subcategorías
    subcats_def = [
        {"nombre": "Taladros", "descripcion": "Taladros y atornilladores", "categoria": "Herramientas"},
        {"nombre": "Llaves", "descripcion": "Llaves ajustables y combinadas", "categoria": "Herramientas"},
        {"nombre": "Destornilladores", "descripcion": "Destornilladores y puntas", "categoria": "Herramientas"},
        {"nombre": "Iluminación", "descripcion": "Luminarias y paneles LED", "categoria": "Electricidad"},
        {"nombre": "Cables", "descripcion": "Cables eléctricos y extensiones", "categoria": "Electricidad"},
        {"nombre": "Tubos PVC", "descripcion": "Tubos y fittings de PVC", "categoria": "Plomería"},
        {"nombre": "Grifería", "descripcion": "Llaves de paso y accesorios", "categoria": "Plomería"},
        {"nombre": "Fijaciones", "descripcion": "Tornillos y pernos", "categoria": "Construcción"},
        {"nombre": "Pinturas", "descripcion": "Pinturas y recubrimientos", "categoria": "Construcción"},
        {"nombre": "Riego", "descripcion": "Accesorios de riego por goteo", "categoria": "Jardinería"},
        {"nombre": "Mangueras", "descripcion": "Mangueras y conectores", "categoria": "Jardinería"},
    ]
    sub_map = {}
    for s in subcats_def:
        ex = db.query(SubCategoriaDB).filter(SubCategoriaDB.nombre == s["nombre"]).first()
        if not ex:
            ex = SubCategoriaDB(
                nombre=s["nombre"],
                descripcion=s.get("descripcion"),
                id_categoria=cat_map[s["categoria"]]
            )
            db.add(ex)
            db.flush()
        sub_map[s["nombre"]] = ex.id_subcategoria
    resumen["subcategorias_insertadas"] = len(subcats_def)

    # Proveedores
    proveedores_def = [
        {"nombre": "FerreMax", "telefono": "+56922000001", "correo": "ventas@ferremax.cl"},
        {"nombre": "ProElec Chile", "telefono": "+56922000002", "correo": "contacto@proelec.cl"},
        {"nombre": "AquaPipe Ltda", "telefono": "+56922000003", "correo": "ventas@aquapipe.cl"},
        {"nombre": "ConstruMarket", "telefono": "+56922000004", "correo": "soporte@construmarket.cl"},
        {"nombre": "GardenPro", "telefono": "+56922000005", "correo": "ventas@gardenpro.cl"},
    ]
    prov_map = {}
    for p in proveedores_def:
        ex = db.query(ProveedorDB).filter(ProveedorDB.nombre == p["nombre"]).first()
        if not ex:
            ex = ProveedorDB(**p)
            db.add(ex)
            db.flush()
        prov_map[p["nombre"]] = ex.id_proveedor
    resumen["proveedores_insertados"] = len(proveedores_def)

    # Productos (15 en total; algunos comparten subcategoría para "similares")
    productos_def = [
        # Herramientas / Taladros (3)
        {
            "nombre": "Taladro Percutor 850W",
            "descripcion": "Taladro percutor 850W con velocidad variable",
            "codigo_interno": "FER-001",
            "imagen_url": "https://picsum.photos/seed/FER-001/600/600",
            "id_categoria": cat_map["Herramientas"],
            "id_subcategoria": sub_map["Taladros"],
            "id_proveedor": prov_map["FerreMax"],
            "marca": "Bosch",
            "precio_venta": Decimal("79990"),
            "cantidad_disponible": 20,
            "stock_minimo": 3,
            "estado": "activo",
            "en_catalogo": True,
            "garantia_meses": 24,
            "modelo": "GSB-850",
            "color": "Azul",
            "material": "Plástico y metal",
            "caracteristicas": "Potencia: 850W; Golpe; Portabrocas 13mm; Maletín"
        },
        {
            "nombre": "Atornillador Inalámbrico 12V",
            "descripcion": "Atornillador 12V con batería y cargador",
            "codigo_interno": "FER-002",
            "imagen_url": "https://picsum.photos/seed/FER-002/600/600",
            "id_categoria": cat_map["Herramientas"],
            "id_subcategoria": sub_map["Taladros"],
            "id_proveedor": prov_map["FerreMax"],
            "marca": "Makita",
            "precio_venta": Decimal("64990"),
            "cantidad_disponible": 25,
            "stock_minimo": 3,
            "estado": "activo",
            "en_catalogo": True,
            "garantia_meses": 12,
            "modelo": "DF333D",
            "color": "Verde",
            "material": "Plástico y metal",
            "caracteristicas": "Batería 12V; Incluye maletín; 2 velocidades"
        },
        {
            "nombre": "Taladro Inalámbrico 20V",
            "descripcion": "Taladro sin cable 20V con luz LED",
            "codigo_interno": "FER-003",
            "imagen_url": "https://picsum.photos/seed/FER-003/600/600",
            "id_categoria": cat_map["Herramientas"],
            "id_subcategoria": sub_map["Taladros"],
            "id_proveedor": prov_map["FerreMax"],
            "marca": "DeWalt",
            "precio_venta": Decimal("99990"),
            "cantidad_disponible": 18,
            "stock_minimo": 3,
            "estado": "activo",
            "en_catalogo": True,
            "garantia_meses": 24,
            "modelo": "DCD777",
            "color": "Amarillo",
            "material": "Plástico y metal",
            "caracteristicas": "20V; Motor sin escobillas; Luz LED"
        },
        # Herramientas / Llaves (2)
        {
            "nombre": "Llave Ajustable 10\"",
            "descripcion": "Llave ajustable de 10 pulgadas",
            "codigo_interno": "FER-004",
            "imagen_url": "https://picsum.photos/seed/FER-004/600/600",
            "id_categoria": cat_map["Herramientas"],
            "id_subcategoria": sub_map["Llaves"],
            "id_proveedor": prov_map["FerreMax"],
            "marca": "Truper",
            "precio_venta": Decimal("14990"),
            "cantidad_disponible": 60,
            "stock_minimo": 5,
            "estado": "activo",
            "en_catalogo": True,
            "garantia_meses": 6,
            "modelo": "AJ-10",
            "color": "Plateado",
            "material": "Acero cromado",
            "caracteristicas": "Apertura 30mm; Antideslizante; Escala grabada"
        },
        {
            "nombre": "Juego Llaves Combinadas 12 pzs",
            "descripcion": "Set de llaves combinadas de 8 a 19mm",
            "codigo_interno": "FER-005",
            "imagen_url": "https://picsum.photos/seed/FER-005/600/600",
            "id_categoria": cat_map["Herramientas"],
            "id_subcategoria": sub_map["Llaves"],
            "id_proveedor": prov_map["FerreMax"],
            "marca": "Stanley",
            "precio_venta": Decimal("29990"),
            "cantidad_disponible": 35,
            "stock_minimo": 5,
            "estado": "activo",
            "en_catalogo": True,
            "garantia_meses": 12,
            "modelo": "ST-12",
            "color": "Plateado",
            "material": "Acero cromado",
            "caracteristicas": "12 piezas; Estuche enrollable; Métrica"
        },
        # Herramientas / Destornilladores (1)
        {
            "nombre": "Set Destornilladores 6 pzs",
            "descripcion": "Planos y Phillips con puntas imantadas",
            "codigo_interno": "FER-006",
            "imagen_url": "https://picsum.photos/seed/FER-006/600/600",
            "id_categoria": cat_map["Herramientas"],
            "id_subcategoria": sub_map["Destornilladores"],
            "id_proveedor": prov_map["FerreMax"],
            "marca": "Stanley",
            "precio_venta": Decimal("12990"),
            "cantidad_disponible": 80,
            "stock_minimo": 8,
            "estado": "activo",
            "en_catalogo": True,
            "garantia_meses": 6,
            "modelo": "SD-6",
            "color": "Amarillo/Negro",
            "material": "Acero y plástico",
            "caracteristicas": "6 piezas; Puntas imantadas; Mangos ergonómicos"
        },
        # Electricidad / Iluminación (2)
        {
            "nombre": "Foco LED 30W Exterior",
            "descripcion": "Proyector LED IP65 para exteriores",
            "codigo_interno": "ELE-001",
            "imagen_url": "https://picsum.photos/seed/ELE-001/600/600",
            "id_categoria": cat_map["Electricidad"],
            "id_subcategoria": sub_map["Iluminación"],
            "id_proveedor": prov_map["ProElec Chile"],
            "marca": "Osram",
            "precio_venta": Decimal("24990"),
            "cantidad_disponible": 50,
            "stock_minimo": 5,
            "estado": "activo",
            "en_catalogo": True,
            "garantia_meses": 12,
            "modelo": "FL-30W",
            "color": "Negro",
            "material": "Aluminio",
            "caracteristicas": "30W; IP65; 3000K"
        },
        {
            "nombre": "Panel LED 48W Empotrado",
            "descripcion": "Panel LED 60x60cm para oficinas",
            "codigo_interno": "ELE-002",
            "imagen_url": "https://picsum.photos/seed/ELE-002/600/600",
            "id_categoria": cat_map["Electricidad"],
            "id_subcategoria": sub_map["Iluminación"],
            "id_proveedor": prov_map["ProElec Chile"],
            "marca": "Philips",
            "precio_venta": Decimal("39990"),
            "cantidad_disponible": 40,
            "stock_minimo": 5,
            "estado": "activo",
            "en_catalogo": True,
            "garantia_meses": 24,
            "modelo": "PL-48W",
            "color": "Blanco",
            "material": "Aluminio y acrílico",
            "caracteristicas": "48W; 4000K; Alto brillo"
        },
        # Electricidad / Cables (1)
        {
            "nombre": "Cable Eléctrico 2x1.5mm 100m",
            "descripcion": "Rollo de cable dúplex 2x1.5mm",
            "codigo_interno": "ELE-003",
            "imagen_url": "https://picsum.photos/seed/ELE-003/600/600",
            "id_categoria": cat_map["Electricidad"],
            "id_subcategoria": sub_map["Cables"],
            "id_proveedor": prov_map["ProElec Chile"],
            "marca": "Ducab",
            "precio_venta": Decimal("69990"),
            "cantidad_disponible": 15,
            "stock_minimo": 2,
            "estado": "activo",
            "en_catalogo": True,
            "garantia_meses": 12,
            "modelo": "C-2X1.5-100",
            "color": "Blanco",
            "material": "Cobre y PVC",
            "caracteristicas": "2x1.5mm; 100m; Aislamiento PVC"
        },
        # Plomería / Tubos PVC (1)
        {
            "nombre": "Tubo PVC 1/2\" x 3m",
            "descripcion": "Tubo PVC presión 1/2 pulgada",
            "codigo_interno": "PLO-001",
            "imagen_url": "https://picsum.photos/seed/PLO-001/600/600",
            "id_categoria": cat_map["Plomería"],
            "id_subcategoria": sub_map["Tubos PVC"],
            "id_proveedor": prov_map["AquaPipe Ltda"],
            "marca": "Tigre",
            "precio_venta": Decimal("5990"),
            "cantidad_disponible": 120,
            "stock_minimo": 10,
            "estado": "activo",
            "en_catalogo": True,
            "garantia_meses": 6,
            "modelo": "PVC-1/2-3M",
            "color": "Gris",
            "material": "PVC",
            "caracteristicas": "Clase 10; Longitud 3m; 1/2\""
        },
        # Plomería / Grifería (1)
        {
            "nombre": "Llave de Paso 1/2\"",
            "descripcion": "Llave de paso de bronce 1/2 pulgada",
            "codigo_interno": "PLO-002",
            "imagen_url": "https://picsum.photos/seed/PLO-002/600/600",
            "id_categoria": cat_map["Plomería"],
            "id_subcategoria": sub_map["Grifería"],
            "id_proveedor": prov_map["AquaPipe Ltda"],
            "marca": "Foset",
            "precio_venta": Decimal("8990"),
            "cantidad_disponible": 90,
            "stock_minimo": 8,
            "estado": "activo",
            "en_catalogo": True,
            "garantia_meses": 12,
            "modelo": "LP-1/2",
            "color": "Bronce",
            "material": "Bronce",
            "caracteristicas": "Rosca 1/2\"; Cierre rápido; Durable"
        },
        # Construcción / Fijaciones (1)
        {
            "nombre": "Tornillos Madera 8x1\" Caja 500",
            "descripcion": "Tornillos para madera punta aguda",
            "codigo_interno": "CON-001",
            "imagen_url": "https://picsum.photos/seed/CON-001/600/600",
            "id_categoria": cat_map["Construcción"],
            "id_subcategoria": sub_map["Fijaciones"],
            "id_proveedor": prov_map["ConstruMarket"],
            "marca": "Fischer",
            "precio_venta": Decimal("19990"),
            "cantidad_disponible": 70,
            "stock_minimo": 7,
            "estado": "activo",
            "en_catalogo": True,
            "garantia_meses": 6,
            "modelo": "FM-8X1",
            "color": "Zincado",
            "material": "Acero",
            "caracteristicas": "Caja 500; 8x1\"; Rosca fina"
        },
        # Construcción / Pinturas (1)
        {
            "nombre": "Pintura Látex Interior 1 Galón",
            "descripcion": "Pintura blanca mate para interiores",
            "codigo_interno": "CON-003",
            "imagen_url": "https://picsum.photos/seed/CON-003/600/600",
            "id_categoria": cat_map["Construcción"],
            "id_subcategoria": sub_map["Pinturas"],
            "id_proveedor": prov_map["ConstruMarket"],
            "marca": "Tricolor",
            "precio_venta": Decimal("15990"),
            "cantidad_disponible": 45,
            "stock_minimo": 5,
            "estado": "activo",
            "en_catalogo": True,
            "garantia_meses": 6,
            "modelo": "LATEX-G1",
            "color": "Blanco",
            "material": "Base agua",
            "caracteristicas": "Rendimiento 30m²/galón; Secado rápido"
        },
        # Jardinería / Mangueras (1)
        {
            "nombre": "Manguera Jardín 1/2\" 20m",
            "descripcion": "Manguera flexible con conectores",
            "codigo_interno": "JAR-001",
            "imagen_url": "https://picsum.photos/seed/JAR-001/600/600",
            "id_categoria": cat_map["Jardinería"],
            "id_subcategoria": sub_map["Mangueras"],
            "id_proveedor": prov_map["GardenPro"],
            "marca": "Gardena",
            "precio_venta": Decimal("19990"),
            "cantidad_disponible": 50,
            "stock_minimo": 5,
            "estado": "activo",
            "en_catalogo": True,
            "garantia_meses": 12,
            "modelo": "MG-1/2-20",
            "color": "Verde",
            "material": "PVC",
            "caracteristicas": "20 metros; Con conectores; Resistente UV"
        },
        # Jardinería / Riego (1)
        {
            "nombre": "Kit Riego por Goteo 30m",
            "descripcion": "Kit completo para riego por goteo",
            "codigo_interno": "JAR-002",
            "imagen_url": "https://picsum.photos/seed/JAR-002/600/600",
            "id_categoria": cat_map["Jardinería"],
            "id_subcategoria": sub_map["Riego"],
            "id_proveedor": prov_map["GardenPro"],
            "marca": "Gardena",
            "precio_venta": Decimal("34990"),
            "cantidad_disponible": 30,
            "stock_minimo": 4,
            "estado": "activo",
            "en_catalogo": True,
            "garantia_meses": 12,
            "modelo": "RG-30",
            "color": "Negro",
            "material": "PVC y PE",
            "caracteristicas": "30m; 50 goteros; Accesorios incluidos"
        },
    ]

    insertados = 0
    for p in productos_def:
        ya = None
        if p.get("codigo_interno"):
            ya = db.query(ProductoDB).filter(ProductoDB.codigo_interno == p["codigo_interno"]).first()
        if ya:
            continue
        db.add(ProductoDB(**p))
        insertados += 1
    db.commit()

    # Asegurar conteo final de 15: eliminar posibles extras insertados previamente
    extras_a_eliminar = ["CON-002", "ELE-004"]
    for cod in extras_a_eliminar:
        db.query(ProductoDB).filter(ProductoDB.codigo_interno == cod).delete(synchronize_session=False)
    db.commit()

    resumen["productos_insertados"] = insertados
    resumen["total_categorias"] = len(cat_map)
    resumen["total_subcategorias"] = len(sub_map)
    resumen["total_proveedores"] = len(prov_map)
    return resumen


def seed_mensajes_contacto(db):
    """Inserta mensajes de contacto de ejemplo."""
    ejemplos = [
        {
            "nombre": "Juan",
            "apellido": "Pérez",
            "email": "juan.perez@example.com",
            "asunto": "Consulta sobre despacho",
            "mensaje": "¿Cuánto demora el despacho a Ñuñoa?"
        },
        {
            "nombre": "María",
            "apellido": "González",
            "email": "maria.gonzalez@example.com",
            "asunto": "Stock de taladro",
            "mensaje": "¿Tienen stock del Taladro Percutor 850W?"
        },
        {
            "nombre": "Pedro",
            "apellido": "López",
            "email": "pedro.lopez@example.com",
            "asunto": "Medios de pago",
            "mensaje": "¿Aceptan transferencia y pago en efectivo?"
        }
    ]
    insertados = 0
    for e in ejemplos:
        ya = db.query(MensajeContactoDB).filter(MensajeContactoDB.email == e["email"], MensajeContactoDB.asunto == e["asunto"]).first()
        if ya:
            continue
        db.add(MensajeContactoDB(**e))
        insertados += 1
    db.commit()
    return {"mensajes_contacto_insertados": insertados}


def seed_fill_tables(db, count: int = 200):
    resumen = {}
    usuarios_target = count
    proveedores_target = count
    categorias_target = count
    subcategorias_target = count
    productos_target = count
    ventas_target = count
    pagos_target = count
    despachos_target = count
    auditoria_target = count

    usuarios_insertados = 0
    proveedores_insertados = 0
    categorias_insertadas = 0
    subcategorias_insertadas = 0
    productos_insertados = 0
    ventas_insertadas = 0
    pagos_insertados = 0
    despachos_insertados = 0
    auditoria_insertada = 0

    # Roles y permisos básicos
    try:
        roles = {"administrador": None, "cliente": None, "invitado": None}
        for nombre in list(roles.keys()):
            r = db.query(RolDB).filter(RolDB.nombre == nombre).first()
            if not r:
                r = RolDB(nombre=nombre)
                db.add(r)
                db.flush()
            roles[nombre] = r.id_rol
        perms = ["admin_panel", "ventas_ver", "ventas_editar", "inventario_ver", "inventario_editar"]
        perm_ids = {}
        for p in perms:
            pr = db.query(PermisoDB).filter(PermisoDB.descripcion == p).first()
            if not pr:
                pr = PermisoDB(descripcion=p)
                db.add(pr)
                db.flush()
            perm_ids[p] = pr.id_permiso
        # Asignar permisos al rol admin
        for p in perm_ids.values():
            exists = db.query(RolPermisoDB).filter(RolPermisoDB.id_rol == roles["administrador"], RolPermisoDB.id_permiso == p).first()
            if not exists:
                db.add(RolPermisoDB(id_rol=roles["administrador"], id_permiso=p))
        db.flush()
    except Exception:
        pass

    first_names = [
        "Juan","Pedro","María","Camila","José","Carolina","Felipe","Valentina","Diego","Andrea",
        "Jorge","Francisca","Luis","Daniela","Rodrigo","Paula","Ignacio","Fernanda","Nicolás","Claudia"
    ]
    last_names = [
        "Mendoza","González","Muñoz","Rojas","Díaz","Pérez","Soto","Silva","Contreras","Rodríguez",
        "López","Martínez","Castro","Vargas","Flores","Torres","Fuentes","Valenzuela","Araya","Tapia"
    ]

    def nombre_aleatorio(i: int) -> tuple:
        try:
            fn = random.choice(first_names)
            ln1 = random.choice(last_names)
            ln2 = random.choice(last_names)
            if ln2 == ln1:
                ln2 = random.choice([l for l in last_names if l != ln1])
            return fn, f"{ln1} {ln2}"
        except Exception:
            return (f"Usuario {i}", f"Demo {i}")

    existing_users = db.query(UsuarioDB).count()
    for i in range(existing_users + 1, usuarios_target + 1):
        rut = 30000000 + i
        ya = db.query(UsuarioDB).filter(UsuarioDB.rut == rut).first()
        if ya:
            continue
        role = "cliente" if i % 10 else "administrador"
        fn, ln = nombre_aleatorio(i)
        u = UsuarioDB(
            nombre=fn,
            apellido=ln,
            rut=rut,
            email=f"usuario{i}@example.com",
            telefono=f"+5699{str(i).zfill(7)}",
            password=hash_contraseña("demo123"),
            role=role,
            activo=True,
            id_rol=roles.get(role)
        )
        db.add(u)
        usuarios_insertados += 1
    db.flush()
    resumen["usuarios_insertados_bulk"] = usuarios_insertados

    existing_prov = db.query(ProveedorDB).count()
    for i in range(existing_prov + 1, proveedores_target + 1):
        nombre = f"Proveedor {i}"
        ya = db.query(ProveedorDB).filter(ProveedorDB.nombre == nombre).first()
        if ya:
            continue
        p = ProveedorDB(nombre=nombre, telefono=f"+5693{str(i).zfill(7)}", correo=f"proveedor{i}@mail.com")
        db.add(p)
        proveedores_insertados += 1
    db.flush()
    resumen["proveedores_insertados_bulk"] = proveedores_insertados

    existing_cat = db.query(CategoriaDB).count()
    for i in range(existing_cat + 1, categorias_target + 1):
        nombre = f"Categoria {i}"
        ya = db.query(CategoriaDB).filter(CategoriaDB.nombre == nombre).first()
        if ya:
            continue
        c = CategoriaDB(nombre=nombre, descripcion=f"Descripcion {nombre}")
        db.add(c)
        categorias_insertadas += 1
    db.flush()
    resumen["categorias_insertadas_bulk"] = categorias_insertadas

    cat_ids = [c.id_categoria for c in db.query(CategoriaDB).all()]
    existing_sub = db.query(SubCategoriaDB).count()
    for i in range(existing_sub + 1, subcategorias_target + 1):
        nombre = f"Subcategoria {i}"
        ya = db.query(SubCategoriaDB).filter(SubCategoriaDB.nombre == nombre).first()
        if ya:
            continue
        cid = cat_ids[(i - 1) % len(cat_ids)] if cat_ids else None
        s = SubCategoriaDB(nombre=nombre, descripcion=f"Descripcion {nombre}", id_categoria=cid)
        db.add(s)
        subcategorias_insertadas += 1
    db.flush()
    resumen["subcategorias_insertadas_bulk"] = subcategorias_insertadas

    prov_ids = [p.id_proveedor for p in db.query(ProveedorDB).all()]
    sub_ids = [s.id_subcategoria for s in db.query(SubCategoriaDB).all()]
    existing_prod = db.query(ProductoDB).count()
    for i in range(existing_prod + 1, productos_target + 1):
        codigo = f"PRD-BULK-{i:04d}"
        ya = db.query(ProductoDB).filter(ProductoDB.codigo_interno == codigo).first()
        if ya:
            continue
        cid = cat_ids[(i - 1) % len(cat_ids)] if cat_ids else None
        sid = sub_ids[(i - 1) % len(sub_ids)] if sub_ids else None
        pid = prov_ids[(i - 1) % len(prov_ids)] if prov_ids else None
        precio = Decimal(str(random.randint(4990, 99990)))
        cantidad = random.randint(0, 150)
        p = ProductoDB(
            nombre=f"Producto Bulk {i}",
            descripcion=f"Producto generado {i}",
            codigo_interno=codigo,
            imagen_url=f"https://picsum.photos/seed/bulk{i}/600/600",
            id_categoria=cid,
            id_subcategoria=sid,
            id_proveedor=pid,
            marca=f"Marca {((i-1)%20)+1}",
            precio_venta=precio,
            cantidad_disponible=cantidad,
            stock_minimo=random.randint(1, 10),
            estado="activo",
            en_catalogo=True,
            caracteristicas="Generado"
        )
        db.add(p)
        productos_insertados += 1
        if productos_insertados % 100 == 0:
            db.flush()
    db.flush()
    resumen["productos_insertados_bulk"] = productos_insertados

    users = db.query(UsuarioDB).all()
    prods = db.query(ProductoDB).all()
    existing_ventas = db.query(VentaDB).count()
    for i in range(existing_ventas + 1, ventas_target + 1):
        if not users or not prods:
            break
        u = users[(i - 1) % len(users)]
        k = random.randint(1, 4)
        items = random.sample(prods, k if len(prods) >= k else 1)
        total = Decimal("0")
        for it in items:
            qty = random.randint(1, 3)
            total += Decimal(str((it.precio_venta or 0))) * qty
        estado = "completada" if i % 3 != 0 else "pendiente"
        venta = VentaDB(
            id_usuario=u.id_usuario,
            total_venta=total,
            estado=estado,
            observaciones=f"Seed bulk #{i}"
        )
        db.add(venta)
        db.flush()
        for it in items:
            qty = random.randint(1, 3)
            db.add(DetalleVentaDB(
                id_venta=venta.id_venta,
                id_producto=it.id_producto,
                cantidad=qty,
                precio_unitario=Decimal(str(it.precio_venta or 0)),
                subtotal=Decimal(str(it.precio_venta or 0)) * qty
            ))
            anterior = it.cantidad_disponible or 0
            nuevo = max(0, anterior - qty)
            it.cantidad_disponible = nuevo
            db.add(MovimientoInventarioDB(
                id_producto=it.id_producto,
                id_usuario=u.id_usuario,
                id_venta=venta.id_venta,
                tipo_movimiento="venta",
                cantidad=-qty,
                cantidad_anterior=anterior,
                cantidad_nueva=nuevo,
                motivo=f"Bulk {venta.id_venta}"
            ))
        ventas_insertadas += 1
        if ventas_insertadas % 50 == 0:
            db.flush()
        pago = PagoDB(
            id_venta=venta.id_venta,
            proveedor="transbank",
            estado="aprobado" if estado == "completada" else "iniciado",
            monto=total,
            moneda="CLP"
        )
        db.add(pago)
        pagos_insertados += 1
        if i % 2 == 0:
            d = DespachoDB(
                id_usuario=u.id_usuario,
                buscar=f"Direccion {i}",
                calle=f"Calle {i}",
                numero=str(100 + i),
                depto=None,
                adicional=""
            )
            db.add(d)
            despachos_insertados += 1
        db.add(AuditoriaDB(
            entidad_tipo="venta",
            entidad_id=venta.id_venta,
            accion="venta_bulk",
            usuario_id=u.id_usuario,
            detalle=f"total={float(total)}"
        ))
        auditoria_insertada += 1
    db.commit()
    resumen.update({
        "ventas_insertadas_bulk": ventas_insertadas,
        "pagos_insertados_bulk": pagos_insertados,
        "despachos_insertados_bulk": despachos_insertados,
        "auditoria_insertada_bulk": auditoria_insertada,
    })
    return resumen


def randomize_user_names(db, cantidad: int = 0):
    first_names = [
        "Juan","Pedro","María","Camila","José","Carolina","Felipe","Valentina","Diego","Andrea",
        "Jorge","Francisca","Luis","Daniela","Rodrigo","Paula","Ignacio","Fernanda","Nicolás","Claudia",
        "Sebastián","Pablo","Antonia","Isidora","Cristóbal","Javiera"
    ]
    last_names = [
        "Mendoza","González","Muñoz","Rojas","Díaz","Pérez","Soto","Silva","Contreras","Rodríguez",
        "López","Martínez","Castro","Vargas","Flores","Torres","Fuentes","Valenzuela","Araya","Tapia",
        "Reyes","Navarro","Campos","Carrasco","Saavedra","Rivera"
    ]
    usuarios = db.query(UsuarioDB).filter(UsuarioDB.activo == True).all()
    try:
        usuarios = [u for u in usuarios if (u.role or '').lower() == 'cliente']
    except Exception:
        pass
    if cantidad and cantidad > 0:
        usuarios = usuarios[:cantidad]
    updated = 0
    for u in usuarios:
        try:
            fn = random.choice(first_names)
            ln1 = random.choice(last_names)
            ln2 = random.choice(last_names)
            if ln2 == ln1:
                ln2 = random.choice([l for l in last_names if l != ln1])
            u.nombre = fn
            u.apellido = f"{ln1} {ln2}"
            updated += 1
        except Exception:
            continue
    db.commit()
    return {"usuarios_actualizados": updated}


def prune_active_clients_to_n(db, target: int = 30):
    """Deja solo N clientes activos; el resto se desactiva."""
    try:
        usuarios = db.query(UsuarioDB).filter(UsuarioDB.activo == True).all()
        clientes = [u for u in usuarios if (u.role or '').lower() == 'cliente']
        if len(clientes) <= target:
            return {"clientes_activos": len(clientes), "clientes_desactivados": 0}
        # Mantener los primeros N por fecha_creacion si existe, luego por id
        def key(u):
            try:
                return (u.fecha_creacion or 0, u.id_usuario)
            except Exception:
                return (0, u.id_usuario)
        clientes_sorted = sorted(clientes, key=key)[:target]
        keep_ids = {u.id_usuario for u in clientes_sorted}
        desactivados = 0
        for u in clientes:
            if u.id_usuario not in keep_ids:
                u.activo = False
                desactivados += 1
        db.commit()
        return {"clientes_activos": target, "clientes_desactivados": desactivados}
    except Exception:
        db.rollback()
        return {"clientes_activos": 0, "clientes_desactivados": 0}


def seed_extra_ventas(db, cantidad: int = 50):
    """Genera ventas adicionales con diferentes productos y cantidades."""
    from models.usuario import UsuarioDB
    from models.producto import ProductoDB
    from models.venta import VentaDB, DetalleVentaDB, MovimientoInventarioDB
    from models.pago import PagoDB
    from models.despacho import DespachoDB

    users = db.query(UsuarioDB).all()
    prods = db.query(ProductoDB).all()
    if not users or not prods:
        return {"ventas_agregadas": 0}

    ventas_creadas = 0
    pagos_creados = 0
    despachos_creados = 0
    movimientos_creados = 0

    for i in range(cantidad):
        u = random.choice(users)
        # Seleccionar entre 1 y 5 productos distintos
        k = random.randint(1, 5)
        items = random.sample(prods, k if len(prods) >= k else max(1, len(prods)))
        total = Decimal("0")
        detalles_tmp = []
        for it in items:
            # Cantidad requerida 1-4 pero no superar stock disponible
            req = random.randint(1, 4)
            disp = int(it.cantidad_disponible or 0)
            if disp <= 0:
                continue
            qty = min(req, disp)
            price = Decimal(str(it.precio_venta or 0))
            total += price * qty
            detalles_tmp.append((it, qty, price))

        if not detalles_tmp:
            continue

        estado = random.choice(["pendiente", "completada"]) if i % 7 else "cancelada"
        venta = VentaDB(
            id_usuario=u.id_usuario,
            total_venta=total,
            estado=estado,
            observaciones=f"seed extra {i+1}"
        )
        db.add(venta)
        db.flush()

        for it, qty, price in detalles_tmp:
            db.add(DetalleVentaDB(
                id_venta=venta.id_venta,
                id_producto=it.id_producto,
                cantidad=qty,
                precio_unitario=price,
                subtotal=price * qty
            ))
            anterior = int(it.cantidad_disponible or 0)
            nuevo = max(0, anterior - qty)
            it.cantidad_disponible = nuevo
            db.add(MovimientoInventarioDB(
                id_producto=it.id_producto,
                id_usuario=u.id_usuario,
                id_venta=venta.id_venta,
                tipo_movimiento="venta",
                cantidad=-qty,
                cantidad_anterior=anterior,
                cantidad_nueva=nuevo,
                motivo=f"Seed extra {venta.id_venta}"
            ))
            movimientos_creados += 1

        pago_estado = "aprobado" if estado == "completada" else ("iniciado" if estado == "pendiente" else "rechazado")
        db.add(PagoDB(
            id_venta=venta.id_venta,
            proveedor="transbank",
            estado=pago_estado,
            monto=total,
            moneda="CLP"
        ))
        pagos_creados += 1

        if estado != "cancelada" and (i % 2 == 0):
            d = DespachoDB(
                id_usuario=u.id_usuario,
                buscar=f"Direccion {i}",
                calle=f"Calle {i}",
                numero=str(100 + i),
                depto=None,
                adicional=""
            )
            db.add(d)
            despachos_creados += 1

        ventas_creadas += 1

    db.commit()
    return {
        "ventas_agregadas": ventas_creadas,
        "pagos_agregados": pagos_creados,
        "despachos_agregados": despachos_creados,
        "movimientos_agregados": movimientos_creados,
    }


# Purga de datos de ejemplo/demostración
def purge_demo_data(db):
    summary = {}
    try:
        # Ventas y relacionados
        ventas_demo = db.query(VentaDB).filter(
            (VentaDB.observaciones.ilike('%demo%')) |
            (VentaDB.observaciones.ilike('%seed%')) |
            (VentaDB.observaciones.ilike('%bulk%')) |
            (VentaDB.observaciones.ilike('%extra%'))
        ).all()
        venta_ids = [v.id_venta for v in ventas_demo]
        if venta_ids:
            db.query(DetalleVentaDB).filter(DetalleVentaDB.id_venta.in_(venta_ids)).delete(synchronize_session=False)
            db.query(MovimientoInventarioDB).filter(MovimientoInventarioDB.id_venta.in_(venta_ids)).delete(synchronize_session=False)
            db.query(PagoDB).filter(PagoDB.id_venta.in_(venta_ids)).delete(synchronize_session=False)
            # Auditoría ligada a ventas demo
            db.query(AuditoriaDB).filter(
                (AuditoriaDB.entidad_tipo == 'venta') & (AuditoriaDB.entidad_id.in_(venta_ids))
            ).delete(synchronize_session=False)
            db.query(VentaDB).filter(VentaDB.id_venta.in_(venta_ids)).delete(synchronize_session=False)
        summary['ventas_demo_eliminadas'] = len(venta_ids)

        # Auditorías de seed/bulk explícitas
        aud_extra = db.query(AuditoriaDB).filter(
            (AuditoriaDB.accion.ilike('%demo%')) |
            (AuditoriaDB.accion.ilike('%bulk%')) |
            (AuditoriaDB.detalle.ilike('%Seed%'))
        ).delete(synchronize_session=False)
        summary['auditorias_eliminadas'] = aud_extra or 0

        # Productos de ejemplo por código/nombre
        productos_q = db.query(ProductoDB).filter(
            (ProductoDB.codigo_interno.ilike('PRD-EX-%')) |
            (ProductoDB.codigo_interno.ilike('PRD-EXTRA-%')) |
            (ProductoDB.codigo_interno.ilike('PRD-BULK-%')) |
            (ProductoDB.codigo_interno.ilike('FER-%')) |
            (ProductoDB.codigo_interno.ilike('ELE-%')) |
            (ProductoDB.codigo_interno.ilike('PLO-%')) |
            (ProductoDB.codigo_interno.ilike('CON-%')) |
            (ProductoDB.codigo_interno.ilike('JAR-%')) |
            (ProductoDB.nombre.ilike('%Ejemplo%')) |
            (ProductoDB.nombre.ilike('%Extra%')) |
            (ProductoDB.nombre.ilike('%Bulk%'))
        )
        prod_ids = [p.id_producto for p in productos_q.all()]
        # Movimientos ligados a productos demo (sin venta)
        if prod_ids:
            db.query(MovimientoInventarioDB).filter(MovimientoInventarioDB.id_producto.in_(prod_ids)).delete(synchronize_session=False)
        deleted_prod = db.query(ProductoDB).filter(ProductoDB.id_producto.in_(prod_ids)).delete(synchronize_session=False)
        summary['productos_eliminados'] = deleted_prod or 0

        # Subcategorías/Categorías demo/realistas
        deleted_sub = db.query(SubCategoriaDB).filter(
            (SubCategoriaDB.nombre.ilike('Subcategoria Demo%')) |
            (SubCategoriaDB.nombre.ilike('Subcategoría Extra%')) |
            (SubCategoriaDB.nombre.in_([
                'Taladros','Iluminación','Cables','Tubos PVC','Grifería','Fijaciones','Pinturas','Riego','Mangueras','Llaves','Destornilladores'
            ]))
        ).delete(synchronize_session=False)
        deleted_cat = db.query(CategoriaDB).filter(
            (CategoriaDB.nombre.ilike('Categoria Demo%')) |
            (CategoriaDB.nombre.ilike('Categoría Extra%')) |
            (CategoriaDB.nombre.in_(['Herramientas','Electricidad','Plomería','Construcción','Jardinería']))
        ).delete(synchronize_session=False)
        summary['subcategorias_eliminadas'] = deleted_sub or 0
        summary['categorias_eliminadas'] = deleted_cat or 0

        # Proveedores de ejemplo
        deleted_prov = db.query(ProveedorDB).filter(
            (ProveedorDB.nombre.ilike('Proveedor Demo%')) |
            (ProveedorDB.nombre.ilike('Proveedor Extra%')) |
            (ProveedorDB.nombre.in_(['Acme Tools','FerreMax','ProElec Chile','AquaPipe Ltda','ConstruMarket','GardenPro']))
        ).delete(synchronize_session=False)
        summary['proveedores_eliminados'] = deleted_prov or 0

        # Mensajes de contacto de ejemplo
        deleted_msgs = db.query(MensajeContactoDB).filter(
            MensajeContactoDB.email.ilike('%@example.com')
        ).delete(synchronize_session=False)
        summary['mensajes_eliminados'] = deleted_msgs or 0

        # Usuarios demo (no admin)
        deleted_users = db.query(UsuarioDB).filter(
            (UsuarioDB.email.ilike('%@example.com')) |
            (UsuarioDB.nombre.ilike('Usuario %')) |
            (UsuarioDB.rut >= 20000000)
        ).filter(~UsuarioDB.role.ilike('administrador')).delete(synchronize_session=False)
        summary['usuarios_eliminados'] = deleted_users or 0

        db.commit()
        return summary
    except Exception as e:
        db.rollback()
        return {'error': str(e)}


def purge_demo_data_main():
    db = SessionLocal()
    try:
        out = purge_demo_data(db)
        print(out)
    finally:
        db.close()


# Recrear base de datos y crear usuario administrador inicial
def recreate_database_with_admin(rut_formatted: str = "00.000.000-0", password_plain: str = "123"):
    from config.database import engine
    from models.base import Base
    # Importar todos los modelos para registrar metadata completa
    from models.usuario import UsuarioDB
    from models.rol import RolDB
    from models.permiso import PermisoDB
    from models.rol_permiso import RolPermisoDB
    from models.categoria import CategoriaDB
    from models.subcategoria import SubCategoriaDB
    from models.proveedor import ProveedorDB
    from models.producto import ProductoDB
    from models.venta import VentaDB, DetalleVentaDB, MovimientoInventarioDB
    from models.pago import PagoDB
    from models.despacho import DespachoDB
    from models.auditoria import AuditoriaDB
    import os

    # Eliminar archivo SQLite si existe
    try:
        if engine.dialect.name == 'sqlite':
            db_path = engine.url.database
            if db_path and os.path.exists(db_path):
                os.remove(db_path)
    except Exception:
        pass

    # Crear tablas nuevamente
    Base.metadata.create_all(bind=engine)

    # Crear usuario administrador
    db = SessionLocal()
    try:
        # Asegurar rol administrador
        rol_admin = db.query(RolDB).filter(RolDB.nombre == 'administrador').first()
        if not rol_admin:
            rol_admin = RolDB(nombre='administrador')
            db.add(rol_admin)
            db.flush()

        # Convertir RUT formateado a entero (solo dígitos)
        digits = ''.join(ch for ch in str(rut_formatted) if ch.isdigit())
        rut_int = int(digits) if digits else None

        # Crear usuario
        admin = UsuarioDB(
            nombre='Administrador',
            apellido=None,
            rut=rut_int,
            email='admin@localhost',
            telefono=None,
            password=hash_contraseña(password_plain),
            role='administrador',
            id_rol=rol_admin.id_rol,
            activo=True,
        )
        db.add(admin)
        db.commit()
        return {'status': 'ok', 'admin_id': admin.id_usuario, 'rut': rut_int}
    except Exception as e:
        db.rollback()
        return {'status': 'error', 'detail': str(e)}
    finally:
        db.close()


def recreate_database_with_admin_main():
    out = recreate_database_with_admin()
    print(out)


def seed_real_dataset_2025(db):
    from models.usuario import UsuarioDB
    from models.proveedor import ProveedorDB
    from models.categoria import CategoriaDB
    from models.subcategoria import SubCategoriaDB
    from models.producto import ProductoDB
    from models.venta import VentaDB, DetalleVentaDB, MovimientoInventarioDB
    from models.pago import PagoDB
    from models.despacho import DespachoDB
    from models.mensaje import MensajeContactoDB
    from decimal import Decimal
    from datetime import datetime, timedelta, date
    import random

    resumen = {}

    proveedores_nombres = [
        "FerreMax","ProElectro","AquaPipe","Construmarket","GardenPro","ToolHouse","MetalWorks","PowerTools","IluminaChile","FijacionesPlus"
    ]
    categorias_nombres = [
        "Herramientas","Electricidad","Plomería","Construcción","Jardinería","Pinturas","Seguridad","Iluminación","Adhesivos","Maderas"
    ]
    subcategorias_nombres = [
        "Taladros","Atornilladores","Llaves","Destornilladores","Cables","Paneles LED","Tubos PVC","Grifería","Fijaciones","Hormigón",
        "Riego","Mangueras","Esmaltes","Látex","Guantes","Cascos","Reflectores","Silicona","Pegamento","Tablas"
    ]

    proveedores = []
    for nombre in proveedores_nombres:
        p = db.query(ProveedorDB).filter(ProveedorDB.nombre == nombre).first()
        if not p:
            p = ProveedorDB(nombre=nombre, telefono=f"+5692{random.randint(1000000,9999999)}", correo=f"contacto@{nombre.lower()}.cl")
            db.add(p)
            db.flush()
        proveedores.append(p)
    resumen["proveedores"] = len(proveedores)

    categorias = []
    for nombre in categorias_nombres:
        c = db.query(CategoriaDB).filter(CategoriaDB.nombre == nombre).first()
        if not c:
            c = CategoriaDB(nombre=nombre, descripcion=nombre)
            db.add(c)
            db.flush()
        categorias.append(c)
    resumen["categorias"] = len(categorias)

    subcategorias = []
    for i, nombre in enumerate(subcategorias_nombres):
        sc = db.query(SubCategoriaDB).filter(SubCategoriaDB.nombre == nombre).first()
        if not sc:
            cid = categorias[i % len(categorias)].id_categoria
            sc = SubCategoriaDB(nombre=nombre, descripcion=nombre, id_categoria=cid)
            db.add(sc)
            db.flush()
        subcategorias.append(sc)
    resumen["subcategorias"] = len(subcategorias)

    productos_defs = [
        ("Taladro Percutor 850W","TL-850W","Bosch","Herramientas","Taladros"),
        ("Atornillador Inalámbrico 12V","AT-12V","Makita","Herramientas","Atornilladores"),
        ("Llave Ajustable 10\"","LL-10","Truper","Herramientas","Llaves"),
        ("Set Destornilladores 6 pzs","DS-6","Stanley","Herramientas","Destornilladores"),
        ("Cable Eléctrico 2x1.5mm 100m","CB-2X1.5","Ducab","Electricidad","Cables"),
        ("Panel LED 48W Empotrado","PL-48W","Philips","Iluminación","Paneles LED"),
        ("Tubo PVC 1/2\" x 3m","PVC-12-3","Tigre","Plomería","Tubos PVC"),
        ("Llave de Paso 1/2\"","LP-12","Foset","Plomería","Grifería"),
        ("Tornillos Madera 8x1\" Caja 500","TM-8X1","Fischer","Construcción","Fijaciones"),
        ("Hormigón Seco 25kg","HS-25","Sipa","Construcción","Hormigón"),
        ("Kit Riego por Goteo 30m","RG-30","Gardena","Jardinería","Riego"),
        ("Manguera Jardín 1/2\" 20m","MJ-12-20","Gardena","Jardinería","Mangueras"),
        ("Esmalte Sintético 1 Galón","ES-1G","Tricolor","Pinturas","Esmaltes"),
        ("Pintura Látex Interior 1 Galón","LAT-1G","Tricolor","Pinturas","Látex"),
        ("Guantes de Seguridad Nitrilo","GS-NIT","3M","Seguridad","Guantes"),
        ("Casco de Seguridad Industrial","CS-IND","3M","Seguridad","Cascos"),
        ("Reflector LED 50W","RL-50W","Osram","Iluminación","Reflectores"),
        ("Silicona Transparente 280ml","SI-280","Sika","Adhesivos","Silicona"),
        ("Pegamento de Contacto 250ml","PG-250","UHU","Adhesivos","Pegamento"),
        ("Tabla Pino 1x6 3m","TP-1X6-3","Arauco","Maderas","Tablas"),
        ("Taladro Inalámbrico 20V","TL-20V","DeWalt","Herramientas","Taladros"),
        ("Atornillador Impacto 18V","AT-IM-18","Bosch","Herramientas","Atornilladores"),
        ("Llaves Combinadas 12 pzs","LC-12","Stanley","Herramientas","Llaves"),
        ("Destornillador de Precisión 10 pzs","DP-10","Xiaomi","Herramientas","Destornilladores"),
        ("Cable Extensión 10m","CB-EXT-10","Nexans","Electricidad","Cables"),
        ("Panel LED 36W Empotrado","PL-36W","Philips","Iluminación","Paneles LED"),
        ("Tubo PVC 3/4\" x 3m","PVC-34-3","Tigre","Plomería","Tubos PVC"),
        ("Monomando Lavaplatos","MM-LP","Foset","Plomería","Grifería"),
        ("Tornillos Drywall 6x1\" Caja 500","TD-6X1","Fischer","Construcción","Fijaciones"),
        ("Reflector LED 100W","RL-100W","Osram","Iluminación","Reflectores")
    ]

    productos = []
    def precio_real(cat):
        rng = {
            "Herramientas": (19990, 189990),
            "Electricidad": (3990, 49990),
            "Iluminación": (9990, 129990),
            "Plomería": (5990, 59990),
            "Construcción": (4990, 79990),
            "Jardinería": (7990, 69990),
            "Pinturas": (6990, 39990),
            "Seguridad": (4990, 39990),
            "Adhesivos": (1990, 9990),
            "Maderas": (9990, 59990),
        }
        lo, hi = rng.get(cat, (5990, 99990))
        return Decimal(str(random.randint(lo, hi)))

    for i, (nombre, codigo, marca, cat_name, sub_name) in enumerate(productos_defs):
        cat = db.query(CategoriaDB).filter(CategoriaDB.nombre == cat_name).first()
        sub = db.query(SubCategoriaDB).filter(SubCategoriaDB.nombre == sub_name).first()
        prov = proveedores[i % len(proveedores)]
        precio = precio_real(cat_name)
        cantidad = random.randint(5, 120)
        en_cat = i < 25
        ya = db.query(ProductoDB).filter(ProductoDB.codigo_interno == codigo).first()
        if ya:
            productos.append(ya)
            continue
        # costos y utilidades razonables
        costo_bruto = (precio * Decimal('0.65')).quantize(Decimal('1'))
        costo_neto = (costo_bruto * Decimal('0.88')).quantize(Decimal('1'))
        utilidad_pesos = (precio - costo_neto).quantize(Decimal('1'))
        porcentaje_utilidad = (utilidad_pesos / precio * Decimal('100')).quantize(Decimal('1')) if precio > 0 else Decimal('0')

        prod = ProductoDB(
            nombre=nombre,
            descripcion=nombre,
            codigo_interno=codigo,
            imagen_url=f"https://picsum.photos/seed/{codigo}/600/600",
            id_categoria=cat.id_categoria if cat else None,
            id_subcategoria=sub.id_subcategoria if sub else None,
            id_proveedor=prov.id_proveedor,
            marca=marca,
            precio_venta=precio,
            costo_bruto=costo_bruto,
            costo_neto=costo_neto,
            utilidad_pesos=utilidad_pesos,
            porcentaje_utilidad=porcentaje_utilidad,
            cantidad_disponible=cantidad,
            stock_minimo=random.randint(1, 10),
            estado="activo",
            en_catalogo=en_cat
        )
        db.add(prod)
        db.flush()
        productos.append(prod)
    db.commit()
    resumen["productos"] = len(productos)

    nombres = [
        "Juan","Pedro","María","Camila","José","Carolina","Felipe","Valentina","Diego","Andrea",
        "Jorge","Francisca","Luis","Daniela","Rodrigo","Paula","Ignacio","Fernanda","Nicolás","Claudia"
    ]
    apellidos = [
        "Mendoza","González","Muñoz","Rojas","Díaz","Pérez","Soto","Silva","Contreras","Rodríguez",
        "López","Martínez","Castro","Vargas","Flores","Torres","Fuentes","Valenzuela","Araya","Tapia"
    ]
    usuarios = []
    for i in range(20):
        fn = nombres[i % len(nombres)]
        ln = apellidos[i % len(apellidos)]
        rut = 12000000 + i
        email = f"{fn.lower()}.{ln.lower()}@mail.com"
        tel = f"+5699{random.randint(1000000,9999999)}"
        u = db.query(UsuarioDB).filter(UsuarioDB.rut == rut).first()
        if not u:
            u = UsuarioDB(nombre=fn, apellido=ln, rut=rut, email=email, telefono=tel, password=hash_contraseña("123456"), role="cliente", activo=True)
            db.add(u)
            db.flush()
        usuarios.append(u)
    db.commit()
    resumen["usuarios"] = len(usuarios)

    mensajes = []
    asuntos = ["Consulta de stock","Despacho","Garantía","Medios de pago","Horarios","Cotización","Soporte","Cambios y devoluciones","Instalación","Sugerencias"]
    for i in range(20):
        fn = nombres[(i+3) % len(nombres)]
        ln = apellidos[(i+5) % len(apellidos)]
        email = f"{fn.lower()}.{ln.lower()}@mail.com"
        asunto = asuntos[i % len(asuntos)]
        msg = f"Hola, necesito información sobre {productos[i % len(productos)].nombre}."
        ya = db.query(MensajeContactoDB).filter(MensajeContactoDB.email == email, MensajeContactoDB.asunto == asunto).first()
        if not ya:
            m = MensajeContactoDB(nombre=fn, apellido=ln, email=email, asunto=asunto, mensaje=msg)
            db.add(m)
            mensajes.append(m)
    db.commit()
    resumen["mensajes"] = len(mensajes)

    inicio = datetime(2025, 11, 1)
    fin = datetime(2025, 12, 31, 23, 59, 59)
    ventas_creadas = 0
    pagos_creados = 0
    despachos_creados = 0
    for i in range(60):
        u = random.choice(usuarios)
        dt = inicio + timedelta(seconds=random.randint(0, int((fin - inicio).total_seconds())))
        k = random.randint(1, 4)
        items = random.sample(productos, k)
        total = Decimal("0")
        detalles_tmp = []
        for it in items:
            disp = int(it.cantidad_disponible or 0)
            if disp <= 0:
                continue
            qty = random.randint(1, min(3, disp))
            price = Decimal(str(it.precio_venta or 0))
            total += price * qty
            detalles_tmp.append((it, qty, price))
        if not detalles_tmp:
            continue
        estado = random.choice(["completada","pendiente","completada","completada"]) if i % 9 else "cancelada"
        venta = VentaDB(id_usuario=u.id_usuario, total_venta=total, estado=estado, observaciones="venta real", tipo_documento="boleta", folio_documento=f"B-{1000+i}", fecha_emision_sii=dt.date(), cliente_id=u.id_usuario, fecha_venta=dt)
        db.add(venta)
        db.flush()
        for it, qty, price in detalles_tmp:
            db.add(DetalleVentaDB(id_venta=venta.id_venta, id_producto=it.id_producto, cantidad=qty, precio_unitario=price, subtotal=price*qty))
            anterior = int(it.cantidad_disponible or 0)
            nuevo = max(0, anterior - qty)
            it.cantidad_disponible = nuevo
            db.add(MovimientoInventarioDB(id_producto=it.id_producto, id_usuario=u.id_usuario, id_venta=venta.id_venta, tipo_movimiento="venta", cantidad=-qty, cantidad_anterior=anterior, cantidad_nueva=nuevo, motivo="venta"))
        pagos_estado = "aprobado" if estado == "completada" else ("iniciado" if estado == "pendiente" else "rechazado")
        db.add(PagoDB(id_venta=venta.id_venta, proveedor="transbank", estado=pagos_estado, monto=total, moneda="CLP"))
        pagos_creados += 1
        if estado != "cancelada" and (i % 2 == 0):
            d = DespachoDB(id_usuario=u.id_usuario, buscar="direccion", calle="Calle 123", numero="100", depto=None, adicional="")
            db.add(d)
            despachos_creados += 1
        ventas_creadas += 1
    db.commit()
    resumen.update({"ventas": ventas_creadas, "pagos": pagos_creados, "despachos": despachos_creados})
    return resumen


def seed_client_purchases(db, cantidad: int = 30):
    """Crea 'cantidad' compras reales con distintos usuarios cliente y asigna una dirección real a cada uno.
    - Cada venta usa entre 1 y 3 productos con stock disponible.
    - Se asegura que cada cliente tenga exactamente 1 dirección Despacho con datos realistas.
    - Las ventas se marcan como 'completada' con pago 'aprobado'.
    """
    import random
    from decimal import Decimal
    clientes = db.query(UsuarioDB).filter((UsuarioDB.role == 'cliente') & (UsuarioDB.activo == True)).all()
    productos = db.query(ProductoDB).filter((ProductoDB.estado == 'activo') & (ProductoDB.en_catalogo == True)).all()
    if not clientes:
        return {"ventas_creadas": 0, "mensaje": "No hay clientes"}
    if not productos:
        return {"ventas_creadas": 0, "mensaje": "No hay productos activos"}

    # Direcciones realistas (Chile)
    comunas = [
        "Santiago", "Providencia", "Ñuñoa", "Las Condes", "La Florida", "Maipú",
        "Puente Alto", "San Miguel", "Macul", "Independencia", "Recoleta", "Vitacura"
    ]
    calles = [
        "Av. Apoquindo", "Av. Providencia", "Irarrázabal", "Av. O'Higgins", "Av. La Florida",
        "Gran Avenida", "Av. Los Leones", "Av. Kennedy", "Av. Grecia", "Av. Vicuña Mackenna"
    ]

    # Elegir hasta 'cantidad' clientes únicos
    random.shuffle(clientes)
    seleccion = clientes[:cantidad] if len(clientes) >= cantidad else clientes
    ventas_creadas = 0
    pagos_creados = 0
    movimientos_creados = 0
    despachos_actualizados = 0

    for idx, cli in enumerate(seleccion, start=1):
        try:
            # Asignar/actualizar dirección única
            db.query(DespachoDB).filter(DespachoDB.id_usuario == cli.id_usuario).delete(synchronize_session=False)
            comuna = random.choice(comunas)
            calle = random.choice(calles)
            numero = str(random.randint(100, 9999))
            buscar = f"{calle} {numero}, {comuna}, Región Metropolitana"
            despacho = DespachoDB(
                id_usuario=cli.id_usuario,
                buscar=buscar,
                calle=calle,
                numero=numero,
                depto=None,
                adicional=""
            )
            db.add(despacho)
            despachos_actualizados += 1

            # Seleccionar productos (1-3) con stock
            disponibles = [p for p in productos if (p.cantidad_disponible or 0) > 0]
            if not disponibles:
                db.flush()
                continue
            k = random.randint(1, 3)
            items = random.sample(disponibles, k if len(disponibles) >= k else 1)

            total = Decimal("0")
            detalles = []
            for it in items:
                disp = int(it.cantidad_disponible or 0)
                if disp <= 0:
                    continue
                qty = min(random.randint(1, 3), disp)
                price = Decimal(str(it.precio_venta or 0))
                total += price * qty
                detalles.append((it, qty, price))

            if not detalles:
                db.flush()
                continue

            venta = VentaDB(
                id_usuario=cli.id_usuario,
                total_venta=total,
                estado="completada",
                observaciones=f"compra cliente {cli.id_usuario}",
                cliente_id=cli.id_usuario,
                tipo_documento="boleta",
            )
            db.add(venta)
            db.flush()

            for it, qty, price in detalles:
                db.add(DetalleVentaDB(
                    id_venta=venta.id_venta,
                    id_producto=it.id_producto,
                    cantidad=qty,
                    precio_unitario=price,
                    subtotal=price * qty
                ))
                anterior = int(it.cantidad_disponible or 0)
                nuevo = max(0, anterior - qty)
                it.cantidad_disponible = nuevo
                db.add(MovimientoInventarioDB(
                    id_producto=it.id_producto,
                    id_usuario=cli.id_usuario,
                    id_venta=venta.id_venta,
                    tipo_movimiento="venta",
                    cantidad=-qty,
                    cantidad_anterior=anterior,
                    cantidad_nueva=nuevo,
                    motivo=f"Compra cliente {venta.id_venta}"
                ))
                movimientos_creados += 1

            pago = PagoDB(
                id_venta=venta.id_venta,
                proveedor="transbank",
                estado="aprobado",
                monto=total,
                moneda="CLP"
            )
            db.add(pago)
            pagos_creados += 1
            ventas_creadas += 1
            db.flush()
        except Exception:
            continue

    db.commit()
    return {
        "ventas_creadas": ventas_creadas,
        "pagos_creados": pagos_creados,
        "movimientos_creados": movimientos_creados,
        "direcciones_actualizadas": despachos_actualizados,
        "clientes_afectados": len(seleccion)
    }


def seed_real_dataset_2025_main():
    db = SessionLocal()
    try:
        out = seed_real_dataset_2025(db)
        print(out)
    finally:
        db.close()


def fix_products_missing_subcategories(db):
    from models.producto import ProductoDB
    from models.subcategoria import SubCategoriaDB
    from models.categoria import CategoriaDB
    fixed = 0
    created_subs = 0
    productos = db.query(ProductoDB).filter(ProductoDB.id_subcategoria == None).all()
    for prod in productos:
        if not prod.id_categoria:
            continue
        sub = db.query(SubCategoriaDB).filter(SubCategoriaDB.id_categoria == prod.id_categoria).first()
        if not sub:
            cat = db.query(CategoriaDB).filter(CategoriaDB.id_categoria == prod.id_categoria).first()
            name = (getattr(cat, 'nombre', None) or 'Categoría') + ' - General'
            sub = SubCategoriaDB(nombre=name, descripcion='Subcategoría por defecto', id_categoria=prod.id_categoria)
            db.add(sub)
            db.flush()
            created_subs += 1
        prod.id_subcategoria = sub.id_subcategoria
        fixed += 1
    db.commit()
    return {'productos_actualizados': fixed, 'subcategorias_creadas': created_subs}


def fix_products_missing_subcategories_main():
    db = SessionLocal()
    try:
        out = fix_products_missing_subcategories(db)
        print(out)
    finally:
        db.close()


def update_proveedores_real_fields(db):
    from models.proveedor import ProveedorDB
    import random
    cities = [
        'Santiago','Valparaíso','Concepción','La Serena','Antofagasta','Temuco','Rancagua','Iquique','Puerto Montt','Talca'
    ]
    first_names = [
        'Juan','María','Pedro','Camila','José','Carolina','Felipe','Valentina','Diego','Andrea',
        'Jorge','Francisca','Luis','Daniela','Rodrigo','Paula','Ignacio','Fernanda','Nicolás','Claudia'
    ]
    last_names = [
        'Mendoza','González','Muñoz','Rojas','Díaz','Pérez','Soto','Silva','Contreras','Rodríguez',
        'López','Martínez','Castro','Vargas','Flores','Torres','Fuentes','Valenzuela','Araya','Tapia'
    ]
    updated = 0
    proveedores = db.query(ProveedorDB).all()
    for i, p in enumerate(proveedores, start=1):
        try:
            if not p.rut:
                base = 76000000 + (i * 13 % 8999999)
                dv = str((base % 9))
                s = str(base)
                p.rut = f"{s[:-6]}.{s[-6:-3]}.{s[-3:]}-{dv}"
            if not p.razon_social:
                p.razon_social = f"{p.nombre} Ltda"
            fn = random.choice(first_names)
            ln = random.choice(last_names)
            p.contacto = f"{fn} {ln}"
            if not p.telefono:
                p.telefono = f"+5622{random.randint(1000000,9999999)}"
            if not p.celular:
                p.celular = f"+5699{random.randint(1000000,9999999)}"
            if not p.correo:
                p.correo = f"ventas@{p.nombre.lower().replace(' ','')}.cl"
            if not p.ciudad:
                p.ciudad = random.choice(cities)
            if not p.sucursal:
                p.sucursal = 'Casa Matriz'
            if not p.direccion:
                p.direccion = f"Av. Principal {random.randint(100,999)}, {p.ciudad}"
            updated += 1
        except Exception:
            continue
    db.commit()
    return {'proveedores_actualizados': updated}


def update_proveedores_real_fields_main():
    db = SessionLocal()
    try:
        out = update_proveedores_real_fields(db)
        print(out)
    finally:
        db.close()


def improve_categories_and_subcategories(db):
    from models.categoria import CategoriaDB
    from models.subcategoria import SubCategoriaDB
    mapping = {
        "Herramientas": "Herramientas manuales y eléctricas para perforar, atornillar y cortar",
        "Electricidad": "Cables, conexiones y equipos eléctricos para instalación y mantenimiento",
        "Plomería": "Tuberías, grifería y accesorios para conducción de agua",
        "Construcción": "Materiales y fijaciones para obra gruesa y terminaciones",
        "Jardinería": "Soluciones de riego y mantención de áreas verdes",
        "Pinturas": "Recubrimientos, esmaltes y látex para acabados",
        "Seguridad": "Elementos de protección personal y seguridad industrial",
        "Iluminación": "Luminarias y tecnología LED para interiores y exteriores",
        "Adhesivos": "Siliconas, pegamentos y sellantes para múltiples usos",
        "Maderas": "Tablas y derivados para proyectos y construcciones"
    }
    cchanges = 0
    for nombre, desc in mapping.items():
        c = db.query(CategoriaDB).filter(CategoriaDB.nombre == nombre).first()
        if c:
            c.descripcion = desc
            cchanges += 1
    schanges = 0
    subs = db.query(SubCategoriaDB).all()
    for sc in subs:
        if not sc.id_categoria:
            continue
        cat = db.query(CategoriaDB).filter(CategoriaDB.id_categoria == sc.id_categoria).first()
        if not cat:
            continue
        pref = f"{cat.nombre} - "
        if not str(sc.nombre or "").lower().startswith(cat.nombre.lower()):
            sc.nombre = pref + sc.nombre
            schanges += 1
        sc.descripcion = f"Subcategoría de {cat.nombre}: {sc.nombre.split(' - ',1)[-1]}"
    db.commit()
    return {"categorias_actualizadas": cchanges, "subcategorias_actualizadas": schanges}


def improve_categories_and_subcategories_main():
    db = SessionLocal()
    try:
        out = improve_categories_and_subcategories(db)
        print(out)
    finally:
        db.close()


def main():
    db = SessionLocal()
    try:
        resumen = {}
        # Solo ejecutar el seed solicitado de 15 productos realistas
        resumen.update(seed_ferreteria_15_realistas(db))
        print(resumen)
    finally:
        db.close()


if __name__ == "__main__":
    main()
