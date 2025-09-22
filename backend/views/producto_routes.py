#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Rutas de productos
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from controllers.producto_controller import ProductoController
from models.producto import Producto, ProductoCreate, ProductoUpdate, ProductoNuevo
from auth import get_current_user, require_admin

router = APIRouter(prefix="/productos", tags=["Productos"])


@router.get("/", response_model=List[Producto])
async def obtener_productos(
    db: Session = Depends(get_db)
):
    """
    Obtener todos los productos
    
    Args:
        db: Sesión de base de datos
        
    Returns:
        List[Producto]: Lista de todos los productos
    """
    return await ProductoController.obtener_productos(db)


@router.get("/buscar", response_model=List[Producto])
async def buscar_productos(
    q: str = Query(..., description="Término de búsqueda"),
    db: Session = Depends(get_db)
):
    """
    Buscar productos por nombre o descripción
    
    Args:
        q: Término de búsqueda
        db: Sesión de base de datos
        
    Returns:
        List[Producto]: Lista de productos que coinciden con la búsqueda
    """
    return await ProductoController.buscar_productos(q, db)


@router.get("/{producto_id}", response_model=Producto)
async def obtener_producto(
    producto_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener un producto por ID
    
    Args:
        producto_id: ID del producto
        db: Sesión de base de datos
        
    Returns:
        Producto: Datos del producto
        
    Raises:
        HTTPException: Si el producto no existe
    """
    return await ProductoController.obtener_producto(producto_id, db)


@router.post("/", response_model=Producto)
async def crear_producto(
    producto: ProductoCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Crear un nuevo producto (solo administradores)
    
    Args:
        producto: Datos del producto a crear
        db: Sesión de base de datos
        current_user: Usuario actual (debe ser admin)
        
    Returns:
        Producto: Producto creado
        
    Raises:
        HTTPException: Si hay errores en la creación
    """
    return await ProductoController.crear_producto(producto, db)


@router.post("/nuevo", response_model=Producto)
async def crear_producto_nuevo(
    producto: ProductoNuevo,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Crear un nuevo producto con categoría y proveedor nuevos (solo administradores)
    
    Args:
        producto: Datos del producto con categoría y proveedor nuevos
        db: Sesión de base de datos
        current_user: Usuario actual (debe ser admin)
        
    Returns:
        Producto: Producto creado
        
    Raises:
        HTTPException: Si hay errores en la creación
    """
    return await ProductoController.crear_producto_nuevo(producto, db)


@router.put("/{producto_id}", response_model=Producto)
async def actualizar_producto(
    producto_id: int,
    producto: ProductoUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Actualizar un producto (solo administradores)
    
    Args:
        producto_id: ID del producto a actualizar
        producto: Datos actualizados del producto
        db: Sesión de base de datos
        current_user: Usuario actual (debe ser admin)
        
    Returns:
        Producto: Producto actualizado
        
    Raises:
        HTTPException: Si hay errores en la actualización
    """
    return await ProductoController.actualizar_producto(producto_id, producto, db)


@router.post("/{producto_id}/imagen")
async def subir_imagen_producto(
    producto_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Subir imagen para un producto (solo administradores)
    
    Args:
        producto_id: ID del producto
        file: Archivo de imagen
        db: Sesión de base de datos
        current_user: Usuario actual (debe ser admin)
        
    Returns:
        dict: Información de la imagen subida
        
    Raises:
        HTTPException: Si hay errores en la subida
    """
    return await ProductoController.subir_imagen_producto(producto_id, file, db)


@router.delete("/{producto_id}")
async def eliminar_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Eliminar un producto (solo administradores)
    
    Args:
        producto_id: ID del producto a eliminar
        db: Sesión de base de datos
        current_user: Usuario actual (debe ser admin)
        
    Returns:
        dict: Mensaje de confirmación
        
    Raises:
        HTTPException: Si hay errores en la eliminación
    """
    return await ProductoController.eliminar_producto(producto_id, db)