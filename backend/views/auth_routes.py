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

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """ Endpoint para autenticar usuarios """
    return await AuthController.login(form_data, db)