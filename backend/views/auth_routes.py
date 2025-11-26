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
from controllers.google_auth_controller import GoogleAuthController
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
    """Registro de usuarios con rol 'cliente'"""
    # Forzar rol cliente aunque envíen otro
    usuario.role = "cliente"
    return await UsuarioController.crear_usuario(usuario, db)

@router.post("/register-and-login", response_model=Token)
async def register_and_login(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db)
):
    """Registro de usuario y retorno de Token para autologin"""
    usuario.role = "cliente"
    nuevo_usuario = await UsuarioController.crear_usuario(usuario, db)
    # Crear token para autologin usando RUT
    from core.auth import crear_token
    token = crear_token(data={"sub": nuevo_usuario.rut})
    return Token(
        access_token=token,
        token_type="bearer",
        id_usuario=nuevo_usuario.id_usuario,
        nombre=nuevo_usuario.nombre,
        rut=nuevo_usuario.rut,
        role=nuevo_usuario.role
    )

@router.get("/google")
async def google_auth():
    """Inicia el flujo de autenticación con Google"""
    try:
        google_controller = GoogleAuthController()
        auth_url = google_controller.get_google_auth_url()
        # Redirigir directamente a Google para simplificar el flujo desde el frontend
        return RedirectResponse(url=auth_url, status_code=302)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al iniciar autenticación con Google: {str(e)}")

@router.get("/google/callback")
async def google_callback(
    code: str,
    db: Session = Depends(get_db)
):
    """Maneja el callback de Google OAuth"""
    try:
        google_controller = GoogleAuthController()
        result = await google_controller.handle_google_callback(code, db)
        
        # Redirigir al frontend con el token
        import os
        frontend_base = os.environ.get("FRONTEND_URL", "https://ferreteria-patricio.onrender.com")
        frontend_url = f"{frontend_base}/login?token={result['access_token']}&success=true"
        return RedirectResponse(url=frontend_url)
        
    except Exception as e:
        # Redirigir al frontend con error
        import os
        frontend_base = os.environ.get("FRONTEND_URL", "https://ferreteria-patricio.onrender.com")
        frontend_url = f"{frontend_base}/login?error={str(e)}"
        return RedirectResponse(url=frontend_url)
