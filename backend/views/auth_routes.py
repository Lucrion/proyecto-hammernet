#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Rutas de autenticación
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from config.database import get_db
from controllers.auth_controller import AuthController
from controllers.usuario_controller import UsuarioController
from models.usuario import Token, UsuarioCreate, Usuario
from config.constants import API_PREFIX

router = APIRouter(prefix=f"{API_PREFIX}/auth", tags=["Autenticación"])


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """ Endpoint para autenticar usuarios """
    return await AuthController.login(form_data, db)

@router.post("/login-cliente", response_model=Token)
async def login_cliente(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    return await AuthController.login_cliente(form_data, db)

@router.post("/login-trabajador", response_model=Token)
async def login_trabajador(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    return await AuthController.login_trabajador(form_data, db)

@router.post("/register", response_model=Usuario)
async def register(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db)
):
    usuario.role = "cliente"
    return await UsuarioController.crear_usuario(usuario, db)

@router.post("/register-and-login", response_model=Token)
async def register_and_login(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db)
):
    usuario.role = "cliente"
    nuevo_usuario = await UsuarioController.crear_usuario(usuario, db)
    from core.auth import crear_token
    token = crear_token(data={"sub": nuevo_usuario.rut})
    return Token(
        access_token=token,
        token_type="bearer",
        rut=nuevo_usuario.rut,
        nombre=nuevo_usuario.nombre,
        role=nuevo_usuario.role
    )
