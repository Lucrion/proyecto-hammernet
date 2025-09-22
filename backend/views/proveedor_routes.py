#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Rutas de proveedores
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from controllers.proveedor_controller import ProveedorController
from models.proveedor import Proveedor, ProveedorCreate, ProveedorUpdate
from auth import get_current_user, require_admin

router = APIRouter(prefix="/proveedores", tags=["Proveedores"])


@router.get("/", response_model=List[Proveedor])
async def obtener_proveedores(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener todos los proveedores
    
    Args:
        db: Sesión de base de datos
        current_user: Usuario actual
        
    Returns:
        List[Proveedor]: Lista de todos los proveedores
    """
    return await ProveedorController.obtener_proveedores(db)


@router.get("/{proveedor_id}", response_model=Proveedor)
async def obtener_proveedor(
    proveedor_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener un proveedor por ID
    
    Args:
        proveedor_id: ID del proveedor
        db: Sesión de base de datos
        current_user: Usuario actual
        
    Returns:
        Proveedor: Datos del proveedor
        
    Raises:
        HTTPException: Si el proveedor no existe
    """
    return await ProveedorController.obtener_proveedor(proveedor_id, db)


@router.post("/", response_model=Proveedor)
async def crear_proveedor(
    proveedor: ProveedorCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Crear un nuevo proveedor (solo administradores)
    
    Args:
        proveedor: Datos del proveedor a crear
        db: Sesión de base de datos
        current_user: Usuario actual (debe ser admin)
        
    Returns:
        Proveedor: Proveedor creado
        
    Raises:
        HTTPException: Si hay errores en la creación
    """
    return await ProveedorController.crear_proveedor(proveedor, db)


@router.put("/{proveedor_id}", response_model=Proveedor)
async def actualizar_proveedor(
    proveedor_id: int,
    proveedor: ProveedorUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Actualizar un proveedor (solo administradores)
    
    Args:
        proveedor_id: ID del proveedor a actualizar
        proveedor: Datos actualizados del proveedor
        db: Sesión de base de datos
        current_user: Usuario actual (debe ser admin)
        
    Returns:
        Proveedor: Proveedor actualizado
        
    Raises:
        HTTPException: Si hay errores en la actualización
    """
    return await ProveedorController.actualizar_proveedor(proveedor_id, proveedor, db)


@router.delete("/{proveedor_id}")
async def eliminar_proveedor(
    proveedor_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Eliminar un proveedor (solo administradores)
    
    Args:
        proveedor_id: ID del proveedor a eliminar
        db: Sesión de base de datos
        current_user: Usuario actual (debe ser admin)
        
    Returns:
        dict: Mensaje de confirmación
        
    Raises:
        HTTPException: Si hay errores en la eliminación
    """
    return await ProveedorController.eliminar_proveedor(proveedor_id, db)