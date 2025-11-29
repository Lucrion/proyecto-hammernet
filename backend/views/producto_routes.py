"""
Rutas de productos
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from config.database import get_db
from controllers.producto_controller import ProductoController
from models.producto import Producto, ProductoCreate, ProductoUpdate, ProductoInventario
from models.catalogo import ProductoCatalogo, AgregarACatalogo
from core.auth import get_current_user, require_admin
from config.constants import API_PREFIX
from controllers.auditoria_controller import registrar_evento
from models.auditoria import AuditoriaCreate
from seed_data import (
    seed_20_ejemplos_por_tabla,
    seed_usuarios,
    seed_catalogo_y_productos,
    seed_venta_simple,
    seed_despacho_y_pago,
    seed_mas_productos_catalogo,
    seed_ferreteria_15_realistas,
    seed_mensajes_contacto,
    seed_fill_tables,
    randomize_user_names,
)

router = APIRouter(prefix=f"{API_PREFIX}/productos", tags=["Productos"])


@router.get("/", response_model=List[Producto])
async def obtener_productos(
    categoria_id: Optional[int] = None,
    proveedor_id: Optional[int] = None,
    skip: int = 0,
    limit: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """ Obtener todos los productos del inventario (permite filtrar por categoría y proveedor, y paginar) """
    return await ProductoController.obtener_productos(db, categoria_id, proveedor_id, skip, limit)

@router.get("/total")
async def obtener_total_productos(
    categoria_id: Optional[int] = None,
    proveedor_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """ Obtener total de productos aplicando filtros opcionales """
    total = await ProductoController.obtener_total_productos(db, categoria_id, proveedor_id)
    return {"total": total}


@router.get("/catalogo", response_model=List[ProductoCatalogo])
async def obtener_catalogo_publico(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """ Obtener productos del catálogo público con paginación """
    return await ProductoController.obtener_catalogo_publico(db, skip, limit)

@router.get("/catalogo/slug/{slug}", response_model=ProductoCatalogo)
async def obtener_catalogo_por_slug(
    slug: str,
    db: Session = Depends(get_db)
):
    """ Obtener un producto del catálogo público por slug (derivado del nombre) """
    return await ProductoController.obtener_catalogo_por_slug(db, slug)


@router.get("/catalogo/total")
async def obtener_total_catalogo(
    db: Session = Depends(get_db)
):
    """ Obtener total de productos en catálogo """
    return {"total": await ProductoController.obtener_total_catalogo(db)}


@router.get("/buscar", response_model=List[Producto])
async def buscar_productos(
    q: str = Query(..., description="Término de búsqueda"),
    db: Session = Depends(get_db)
):
    """ Buscar productos por nombre o descripción """
    return await ProductoController.buscar_productos(q, db)


@router.get("/inventario/total")
async def obtener_total_inventario(
    soloNoCatalogo: bool = Query(False, description="Si true, contar solo productos no catalogados"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """ Obtener total de productos en inventario (parametrizable por catálogo) """
    return {"total": await ProductoController.obtener_total_inventario(db, soloNoCatalogo)}


@router.get("/inventario", response_model=List[ProductoInventario])
async def obtener_inventario(
    skip: int = 0,
    limit: int = 10,
    soloNoCatalogo: bool = Query(False, description="Si true, listar solo productos no catalogados"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """ Obtener inventario de productos con paginación (parametrizable por catálogo) """
    return await ProductoController.obtener_inventario(db, skip, limit, soloNoCatalogo)


@router.get("/inventario/{inventario_id}", response_model=ProductoInventario)
async def obtener_inventario_producto(
    inventario_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """ Obtener inventario de un producto específico """
    return await ProductoController.obtener_inventario_por_id_alt(inventario_id, db)


@router.put("/inventario/{inventario_id}", response_model=ProductoInventario)
async def actualizar_inventario(
    inventario_id: int,
    cantidad: int,
    precio: float = None,
    db: Session = Depends(get_db),
    request: Request = None,
    current_user: dict = Depends(require_admin)
):
    """ Actualizar inventario de un producto (solo administradores) """
    inventario_data = {"cantidad": cantidad}
    if precio is not None:
        inventario_data["precio"] = precio
    resultado = await ProductoController.actualizar_inventario_por_id(inventario_id, inventario_data, db)
    try:
        ip = request.client.host if request and request.client else None
        ua = request.headers.get("user-agent") if request else None
        await registrar_evento(
            db,
            accion="inventario_actualizar",
            usuario_rut=str(getattr(current_user, "rut", None)) if current_user else None,
            entidad_tipo="Inventario",
            entidad_id=inventario_id,
            detalle=f"cantidad={cantidad}, precio={precio}",
            ip_address=ip,
            user_agent=ua,
        )
    except Exception:
        pass
    return resultado


@router.delete("/inventario/{inventario_id}")
async def eliminar_inventario(
    inventario_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
    current_user: dict = Depends(require_admin)
):
    """ Eliminar registro de inventario (solo administradores) """
    resultado = await ProductoController.eliminar_inventario_por_id(inventario_id, db)
    try:
        ip = request.client.host if request and request.client else None
        ua = request.headers.get("user-agent") if request else None
        await registrar_evento(db, AuditoriaCreate(
            usuario_id=None,
            accion="inventario_eliminar",
            entidad_tipo="Inventario",
            entidad_id=inventario_id,
            detalle="Inventario eliminado",
            ip_address=ip,
            user_agent=ua,
        ))
    except Exception:
        pass
    return resultado


@router.get("/inventario/resumen")
async def obtener_resumen_inventario(
    db: Session = Depends(get_db),
    # current_user: dict = Depends(get_current_user)  # Comentado temporalmente
):
    """ Obtener resumen del inventario """
    return await ProductoController.obtener_resumen_inventario(db)


@router.get("/{producto_id}", response_model=Producto)
async def obtener_producto(
    producto_id: int,
    db: Session = Depends(get_db)
):
    """ Obtener un producto por ID """
    return await ProductoController.obtener_producto(producto_id, db)


@router.post("/", response_model=Producto)
async def crear_producto(
    producto: ProductoCreate,
    db: Session = Depends(get_db),
    request: Request = None,
    current_user: dict = Depends(require_admin)
):
    """ Crear un nuevo producto (solo administradores) """
    creado = await ProductoController.crear_producto(producto, db)
    try:
        ip = request.client.host if request and request.client else None
        ua = request.headers.get("user-agent") if request else None
        await registrar_evento(db, AuditoriaCreate(
            usuario_id=None,
            accion="crear",
            entidad_tipo="Producto",
            entidad_id=creado.id_producto,
            detalle=f"Producto creado: {creado.nombre}",
            ip_address=ip,
            user_agent=ua,
        ))
    except Exception:
        pass
    return creado


@router.post("/nuevo", response_model=Producto)
async def crear_producto_completo(
    producto: ProductoCreate,
    db: Session = Depends(get_db),
    request: Request = None,
    current_user: dict = Depends(require_admin)
):
    """ Crear un producto completo con validaciones adicionales (solo administradores) """
    creado = await ProductoController.crear_producto_completo(producto, db)
    try:
        ip = request.client.host if request and request.client else None
        ua = request.headers.get("user-agent") if request else None
        await registrar_evento(db, AuditoriaCreate(
            usuario_id=None,
            accion="crear",
            entidad_tipo="Producto",
            entidad_id=creado.id_producto,
            detalle=f"Producto creado (completo): {creado.nombre}",
            ip_address=ip,
            user_agent=ua,
        ))
    except Exception:
        pass
    return creado


@router.put("/{producto_id}", response_model=Producto)
async def actualizar_producto(
    producto_id: int,
    producto: ProductoUpdate,
    db: Session = Depends(get_db),
    request: Request = None,
    current_user: dict = Depends(require_admin)
):
    """ Actualizar un producto (solo administradores) """
    actualizado = await ProductoController.actualizar_producto(producto_id, producto, db)
    try:
        cambios = producto.dict(exclude_unset=True)
        ip = request.client.host if request and request.client else None
        ua = request.headers.get("user-agent") if request else None
        await registrar_evento(db, AuditoriaCreate(
            usuario_id=None,
            accion="actualizar",
            entidad_tipo="Producto",
            entidad_id=producto_id,
            detalle=f"Cambios: {cambios}",
            ip_address=ip,
            user_agent=ua,
        ))
    except Exception:
        pass
    return actualizado


@router.post("/{producto_id}/imagen")
async def subir_imagen_producto(
    producto_id: int,
    imagen: UploadFile = File(...),
    db: Session = Depends(get_db),
    request: Request = None,
    current_user: dict = Depends(require_admin)
):
    """ Subir imagen para un producto (solo administradores) """
    resultado = await ProductoController.subir_imagen_producto(producto_id, imagen, db)
    try:
        ip = request.client.host if request and request.client else None
        ua = request.headers.get("user-agent") if request else None
        await registrar_evento(db, AuditoriaCreate(
            usuario_id=None,
            accion="imagen_subir",
            entidad_tipo="Producto",
            entidad_id=producto_id,
            detalle="Imagen subida",
            ip_address=ip,
            user_agent=ua,
        ))
    except Exception:
        pass
    return resultado


@router.delete("/{producto_id}")
async def eliminar_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
    current_user: dict = Depends(require_admin)
):
    """ Eliminar un producto (solo administradores) """
    resultado = await ProductoController.eliminar_producto(producto_id, db)
    try:
        ip = request.client.host if request and request.client else None
        ua = request.headers.get("user-agent") if request else None
        await registrar_evento(db, AuditoriaCreate(
            usuario_id=None,
            accion="eliminar",
            entidad_tipo="Producto",
            entidad_id=producto_id,
            detalle="Producto eliminado",
            ip_address=ip,
            user_agent=ua,
        ))
    except Exception:
        pass
    return resultado


@router.put("/{producto_id}/inventario")
async def actualizar_inventario_producto(
    producto_id: int,
    cantidad_actual: int,
    stock_minimo: Optional[int] = None,
    db: Session = Depends(get_db),
    request: Request = None,
    current_user: dict = Depends(require_admin)
):
    """ Actualizar inventario de un producto específico (solo administradores) """
    inventario_data = {
        "cantidad_disponible": cantidad_actual,
        "stock_minimo": stock_minimo,
    }
    resultado = await ProductoController.actualizar_inventario_producto(
        producto_id, inventario_data, db
    )
    try:
        ip = request.client.host if request and request.client else None
        ua = request.headers.get("user-agent") if request else None
        await registrar_evento(db, AuditoriaCreate(
            usuario_id=None,
            accion="inventario_actualizar",
            entidad_tipo="Producto",
            entidad_id=producto_id,
            detalle=f"cantidad_actual={cantidad_actual}, stock_minimo={stock_minimo}",
            ip_address=ip,
            user_agent=ua,
        ))
    except Exception:
        pass
    return resultado


@router.post("/{producto_id}/agregar-catalogo", response_model=ProductoCatalogo)
async def agregar_producto_a_catalogo(
    producto_id: int,
    datos_catalogo: AgregarACatalogo,
    db: Session = Depends(get_db),
    request: Request = None,
    current_user: dict = Depends(require_admin)
):
    """ Agregar un producto del inventario al catálogo público (solo administradores) """
    agregado = await ProductoController.agregar_producto_a_catalogo(producto_id, datos_catalogo, db)
    try:
        ip = request.client.host if request and request.client else None
        ua = request.headers.get("user-agent") if request else None
        await registrar_evento(db, AuditoriaCreate(
            usuario_id=None,
            accion="catalogo_agregar",
            entidad_tipo="Producto",
            entidad_id=producto_id,
            detalle=f"Datos catálogo: {datos_catalogo.dict()}",
            ip_address=ip,
            user_agent=ua,
        ))
    except Exception:
        pass
    return agregado


@router.put("/catalogo/{producto_id}")
async def actualizar_producto_catalogado(
    producto_id: int,
    datos_actualizacion: dict,
    db: Session = Depends(get_db),
    request: Request = None,
    current_user: dict = Depends(require_admin)
):
    """ Actualizar un producto que ya está en el catálogo (solo administradores) """
    actualizado = await ProductoController.actualizar_producto_catalogado(producto_id, datos_actualizacion, db)
    try:
        ip = request.client.host if request and request.client else None
        ua = request.headers.get("user-agent") if request else None
        await registrar_evento(db, AuditoriaCreate(
            usuario_id=None,
            accion="catalogo_actualizar",
            entidad_tipo="Producto",
            entidad_id=producto_id,
            detalle=f"Actualización catálogo: {datos_actualizacion}",
            ip_address=ip,
            user_agent=ua,
        ))
    except Exception:
        pass
    return actualizado


@router.put("/{producto_id}/quitar-catalogo")
async def quitar_producto_de_catalogo(
    producto_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
    current_user: dict = Depends(require_admin)
):
    """ Quitar un producto del catálogo público (cambia en_catalogo a False) """
    resultado = await ProductoController.quitar_producto_de_catalogo(producto_id, db)
    try:
        ip = request.client.host if request and request.client else None
        ua = request.headers.get("user-agent") if request else None
        await registrar_evento(db, AuditoriaCreate(
            usuario_id=None,
            accion="catalogo_quitar",
            entidad_tipo="Producto",
            entidad_id=producto_id,
            detalle="Producto quitado del catálogo",
            ip_address=ip,
            user_agent=ua,
        ))
    except Exception:
        pass
    return resultado

@router.get("/similares/{producto_id}")
async def obtener_productos_similares(
    producto_id: int,
    limit: int = Query(6, ge=1, le=24),
    db: Session = Depends(get_db)
):
    """Obtener productos similares desde la base de datos (misma subcategoría o categoría)."""
    return await ProductoController.obtener_similares(producto_id, db, limit)

@router.post("/seed/all")
async def seed_todas_tablas(
    cantidad_extra: int = Query(100, ge=0, le=5000, description="Cantidad extra de productos de catálogo"),
    cantidad_por_tabla: int = Query(200, ge=1, le=5000, description="Cantidad mínima por tabla"),
    db: Session = Depends(get_db)
):
    """Inserta ejemplos realistas en todas las tablas principales para pruebas.

    Incluye usuarios, proveedores, categorías, subcategorías, productos, ventas,
    detalles, pagos, despachos, movimientos y auditoría. Evita duplicados.
    """
    resumen = {}
    try:
        resumen.update(seed_usuarios(db))
        resumen.update(seed_catalogo_y_productos(db))
        resumen.update(seed_ferreteria_15_realistas(db))
        resumen["productos_extra_insertados"] = seed_mas_productos_catalogo(db, cantidad=cantidad_extra)
        resumen.update(seed_20_ejemplos_por_tabla(db))
        resumen.update(seed_venta_simple(db))
        resumen.update(seed_despacho_y_pago(db))
        resumen.update(seed_fill_tables(db, count=cantidad_por_tabla))
        try:
            resumen.update(randomize_user_names(db, cantidad=0))
        except Exception:
            pass
        resumen.update(seed_mensajes_contacto(db))
        return {"status": "ok", "resumen": resumen}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en seed all: {str(e)}")
