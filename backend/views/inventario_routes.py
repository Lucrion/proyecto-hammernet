#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Rutas de inventario
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from controllers.inventario_controller import InventarioController
from models.inventario import Inventario, InventarioCreate, InventarioUpdate
from auth import get_current_user, require_admin

router = APIRouter(prefix="/inventario", tags=["Inventario"])


@router.get("/", response_model=List[Inventario])
async def obtener_inventario(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener todo el inventario
    
    Args:
        db: Sesión de base de datos
        current_user: Usuario actual
        
    Returns:
        List[Inventario]: Lista de todo el inventario
    """
    return await InventarioController.obtener_inventario(db)


@router.get("/resumen")
async def obtener_resumen_inventario(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener resumen del inventario con estadísticas
    
    Args:
        db: Sesión de base de datos
        current_user: Usuario actual
        
    Returns:
        dict: Resumen con estadísticas del inventario
    """
    return await InventarioController.obtener_resumen_inventario(db)


@router.get("/{inventario_id}", response_model=Inventario)
async def obtener_item_inventario(
    inventario_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener un item del inventario por ID
    
    Args:
        inventario_id: ID del item de inventario
        db: Sesión de base de datos
        current_user: Usuario actual
        
    Returns:
        Inventario: Datos del item de inventario
        
    Raises:
        HTTPException: Si el item no existe
    """
    return await InventarioController.obtener_item_inventario(inventario_id, db)


@router.post("/", response_model=Inventario)
async def crear_item_inventario(
    inventario: InventarioCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Crear un nuevo item de inventario (solo administradores)
    
    Args:
        inventario: Datos del item de inventario a crear
        db: Sesión de base de datos
        current_user: Usuario actual (debe ser admin)
        
    Returns:
        Inventario: Item de inventario creado
        
    Raises:
        HTTPException: Si hay errores en la creación
    """
    return await InventarioController.crear_item_inventario(inventario, db)


@router.put("/{inventario_id}", response_model=Inventario)
async def actualizar_item_inventario(
    inventario_id: int,
    inventario: InventarioUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Actualizar un item de inventario (solo administradores)
    
    Args:
        inventario_id: ID del item de inventario a actualizar
        inventario: Datos actualizados del item de inventario
        db: Sesión de base de datos
        current_user: Usuario actual (debe ser admin)
        
    Returns:
        Inventario: Item de inventario actualizado
        
    Raises:
        HTTPException: Si hay errores en la actualización
    """
    return await InventarioController.actualizar_item_inventario(inventario_id, inventario, db)


@router.delete("/{inventario_id}")
async def eliminar_item_inventario(
    inventario_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Eliminar un item de inventario (solo administradores)
    
    Args:
        inventario_id: ID del item de inventario a eliminar
        db: Sesión de base de datos
        current_user: Usuario actual (debe ser admin)
        
    Returns:
        dict: Mensaje de confirmación
        
    Raises:
        HTTPException: Si hay errores en la eliminación
    """
    return await InventarioController.eliminar_item_inventario(inventario_id, db)