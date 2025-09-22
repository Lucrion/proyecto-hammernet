#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Rutas de mensajes de contacto
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from controllers.mensaje_controller import MensajeController
from models.mensaje import MensajeContacto, MensajeContactoCreate
from auth import get_current_user, require_admin

router = APIRouter(prefix="/mensajes", tags=["Mensajes de Contacto"])


@router.get("/", response_model=List[MensajeContacto])
async def obtener_mensajes(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Obtener todos los mensajes de contacto (solo administradores)
    
    Args:
        db: Sesión de base de datos
        current_user: Usuario actual (debe ser admin)
        
    Returns:
        List[MensajeContacto]: Lista de todos los mensajes
    """
    return await MensajeController.obtener_mensajes(db)


@router.get("/estadisticas")
async def obtener_estadisticas_mensajes(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Obtener estadísticas de mensajes (solo administradores)
    
    Args:
        db: Sesión de base de datos
        current_user: Usuario actual (debe ser admin)
        
    Returns:
        dict: Estadísticas de mensajes
    """
    return await MensajeController.obtener_estadisticas_mensajes(db)


@router.get("/{mensaje_id}", response_model=MensajeContacto)
async def obtener_mensaje(
    mensaje_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Obtener un mensaje por ID (solo administradores)
    
    Args:
        mensaje_id: ID del mensaje
        db: Sesión de base de datos
        current_user: Usuario actual (debe ser admin)
        
    Returns:
        MensajeContacto: Datos del mensaje
        
    Raises:
        HTTPException: Si el mensaje no existe
    """
    return await MensajeController.obtener_mensaje(mensaje_id, db)


@router.post("/", response_model=MensajeContacto)
async def crear_mensaje(
    mensaje: MensajeContactoCreate,
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo mensaje de contacto (público)
    
    Args:
        mensaje: Datos del mensaje a crear
        db: Sesión de base de datos
        
    Returns:
        MensajeContacto: Mensaje creado
        
    Raises:
        HTTPException: Si hay errores en la creación
    """
    return await MensajeController.crear_mensaje(mensaje, db)


@router.put("/{mensaje_id}/marcar-leido")
async def marcar_mensaje_como_leido(
    mensaje_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Marcar un mensaje como leído (solo administradores)
    
    Args:
        mensaje_id: ID del mensaje a marcar como leído
        db: Sesión de base de datos
        current_user: Usuario actual (debe ser admin)
        
    Returns:
        dict: Mensaje de confirmación
        
    Raises:
        HTTPException: Si hay errores en la actualización
    """
    return await MensajeController.marcar_como_leido(mensaje_id, db)


@router.delete("/{mensaje_id}")
async def eliminar_mensaje(
    mensaje_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Eliminar un mensaje (solo administradores)
    
    Args:
        mensaje_id: ID del mensaje a eliminar
        db: Sesión de base de datos
        current_user: Usuario actual (debe ser admin)
        
    Returns:
        dict: Mensaje de confirmación
        
    Raises:
        HTTPException: Si hay errores en la eliminación
    """
    return await MensajeController.eliminar_mensaje(mensaje_id, db)