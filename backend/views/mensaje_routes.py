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

router = APIRouter(prefix="/api/mensajes", tags=["Mensajes de Contacto"])


@router.get("/", response_model=List[MensajeContacto])
async def obtener_mensajes(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """ Obtener todos los mensajes de contacto (solo administradores) """
    return await MensajeController.obtener_mensajes(db)


@router.get("/estadisticas")
async def obtener_estadisticas_mensajes(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """ Obtener estadísticas de mensajes (solo administradores) """
    return await MensajeController.obtener_estadisticas_mensajes(db)


@router.get("/no-leidos", response_model=List[MensajeContacto])
async def obtener_mensajes_no_leidos(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """ Obtener mensajes no leídos (solo administradores) """
    return await MensajeController.obtener_mensajes_no_leidos(db)


@router.get("/{mensaje_id}", response_model=MensajeContacto)
async def obtener_mensaje(
    mensaje_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """ Obtener un mensaje específico por ID (solo administradores) """
    return await MensajeController.obtener_mensaje(mensaje_id, db)


@router.post("/", response_model=MensajeContacto)
async def crear_mensaje(
    mensaje: MensajeContactoCreate,
    db: Session = Depends(get_db)
):
    """ Crear un nuevo mensaje de contacto (público) """
    return await MensajeController.crear_mensaje(mensaje, db)


@router.put("/{mensaje_id}/marcar-leido")
async def marcar_mensaje_leido(
    mensaje_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """ Marcar un mensaje como leído (solo administradores) """
    return await MensajeController.marcar_mensaje_leido(mensaje_id, db)


@router.put("/{mensaje_id}/marcar-no-leido")
async def marcar_mensaje_no_leido(
    mensaje_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """ Marcar un mensaje como no leído (solo administradores) """
    return await MensajeController.marcar_mensaje_no_leido(mensaje_id, db)


@router.delete("/{mensaje_id}")
async def eliminar_mensaje(
    mensaje_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """ Eliminar un mensaje (solo administradores) """
    return await MensajeController.eliminar_mensaje(mensaje_id, db)