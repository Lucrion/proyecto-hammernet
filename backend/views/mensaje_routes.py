#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Rutas de mensajes """

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from config.database import get_db
from controllers.mensaje_controller import MensajeController
from models.mensaje import MensajeContacto, MensajeContactoCreate
# TODO: Reactivar después - from auth import get_current_user, require_admin
from config.constants import API_PREFIX

router = APIRouter(prefix=f"{API_PREFIX}/mensajes", tags=["Mensajes"])


@router.get("/", response_model=List[MensajeContacto])
async def obtener_mensajes(
    db: Session = Depends(get_db),
    # TODO: Reactivar después - current_user: dict = Depends(require_admin)
):
    """Obtener todos los mensajes (solo administradores)"""
    return await MensajeController.obtener_mensajes(db)


@router.get("/{mensaje_id}", response_model=MensajeContacto)
async def obtener_mensaje(
    mensaje_id: int,
    db: Session = Depends(get_db),
    # TODO: Reactivar después - current_user: dict = Depends(require_admin)
):
    """Obtener un mensaje por ID (solo administradores)"""
    return await MensajeController.obtener_mensaje(mensaje_id, db)


@router.post("/", response_model=MensajeContacto)
async def crear_mensaje(
    mensaje: MensajeContactoCreate,
    db: Session = Depends(get_db),
    # TODO: Reactivar después - current_user: dict = Depends(require_admin)
):
    """Crear un nuevo mensaje (solo administradores)"""
    return await MensajeController.crear_mensaje(mensaje, db)


@router.put("/{mensaje_id}/marcar-leido")
async def marcar_mensaje_leido(
    mensaje_id: int,
    db: Session = Depends(get_db),
    # TODO: Reactivar después - current_user: dict = Depends(require_admin)
):
    """Marcar un mensaje como leído (solo administradores)"""
    return await MensajeController.marcar_como_leido(mensaje_id, db)


@router.delete("/{mensaje_id}")
async def eliminar_mensaje(
    mensaje_id: int,
    db: Session = Depends(get_db),
    # TODO: Reactivar después - current_user: dict = Depends(require_admin)
):
    """Eliminar un mensaje (solo administradores)"""
    return await MensajeController.eliminar_mensaje(mensaje_id, db)