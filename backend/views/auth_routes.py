#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Rutas de autenticación
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from controllers.auth_controller import AuthController
from models.usuario import Token

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Endpoint para autenticar usuarios
    
    Args:
        form_data: Datos del formulario de login (username, password)
        db: Sesión de base de datos
        
    Returns:
        Token: Token de acceso con información del usuario
        
    Raises:
        HTTPException: Si las credenciales son incorrectas
    """
    return await AuthController.login(form_data, db)