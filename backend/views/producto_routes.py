"""
Rutas de productos
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from controllers.producto_controller import ProductoController
from models.producto import Producto, ProductoCreate, ProductoUpdate, ProductoInventario
from auth import get_current_user, require_admin

router = APIRouter(prefix="/api/productos", tags=["Productos"])


@router.get("/", response_model=List[Producto])
async def obtener_productos(
    db: Session = Depends(get_db)
):
    """ Obtener todos los productos """
    return await ProductoController.obtener_productos(db)


@router.get("/buscar", response_model=List[Producto])
async def buscar_productos(
    q: str = Query(..., description="Término de búsqueda"),
    db: Session = Depends(get_db)
):
    """ Buscar productos por nombre o descripción """
    return await ProductoController.buscar_productos(q, db)


@router.get("/inventario", response_model=List[ProductoInventario])
async def obtener_inventario(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """ Obtener inventario de productos """
    return await ProductoController.obtener_inventario(db)


@router.get("/inventario/{inventario_id}", response_model=ProductoInventario)
async def obtener_inventario_producto(
    inventario_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """ Obtener inventario de un producto específico """
    return await ProductoController.obtener_inventario_producto(inventario_id, db)


@router.put("/inventario/{inventario_id}", response_model=ProductoInventario)
async def actualizar_inventario(
    inventario_id: int,
    cantidad: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """ Actualizar inventario de un producto (solo administradores) """
    return await ProductoController.actualizar_inventario(inventario_id, cantidad, db)


@router.delete("/inventario/{inventario_id}")
async def eliminar_inventario(
    inventario_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """ Eliminar registro de inventario (solo administradores) """
    return await ProductoController.eliminar_inventario(inventario_id, db)


@router.get("/inventario/resumen")
async def obtener_resumen_inventario(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
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
    current_user: dict = Depends(require_admin)
):
    """ Crear un nuevo producto (solo administradores) """
    return await ProductoController.crear_producto(producto, db)


@router.post("/nuevo", response_model=Producto)
async def crear_producto_completo(
    producto: ProductoCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """ Crear un producto completo con validaciones adicionales (solo administradores) """
    return await ProductoController.crear_producto_completo(producto, db)


@router.put("/{producto_id}", response_model=Producto)
async def actualizar_producto(
    producto_id: int,
    producto: ProductoUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """ Actualizar un producto (solo administradores) """
    return await ProductoController.actualizar_producto(producto_id, producto, db)


@router.post("/{producto_id}/imagen")
async def subir_imagen_producto(
    producto_id: int,
    imagen: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """ Subir imagen para un producto (solo administradores) """
    return await ProductoController.subir_imagen_producto(producto_id, imagen, db)


@router.delete("/{producto_id}")
async def eliminar_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """ Eliminar un producto (solo administradores) """
    return await ProductoController.eliminar_producto(producto_id, db)


@router.put("/{producto_id}/inventario")
async def actualizar_inventario_producto(
    producto_id: int,
    cantidad_actual: int,
    stock_minimo: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """ Actualizar inventario de un producto específico (solo administradores) """
    return await ProductoController.actualizar_inventario_producto(
        producto_id, cantidad_actual, stock_minimo, db
    )