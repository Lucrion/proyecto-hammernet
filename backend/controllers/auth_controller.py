#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Controlador de autenticación
Maneja el login y autenticación de usuarios
"""

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from models.usuario import UsuarioDB, Token
from controllers.auditoria_controller import registrar_evento
from core.auth import verificar_contraseña, crear_token


class AuthController:
    """Controlador para manejo de autenticación"""
    
    @staticmethod
    async def login(form_data: OAuth2PasswordRequestForm, db: Session) -> Token:
        """
        Autentica un usuario y devuelve un token de acceso
        
        Args:
            form_data: Datos del formulario de login
            db: Sesión de base de datos
            
        Returns:
            Token: Token de acceso con información del usuario
            
        Raises:
            HTTPException: Si las credenciales son incorrectas
        """
        try:
            # Buscar usuario
            usuario = db.query(UsuarioDB).filter(UsuarioDB.username == form_data.username).first()
            if not usuario:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Credenciales incorrectas"
                )
            
            # Verificar que el usuario esté activo
            if not usuario.activo:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario desactivado"
                )
            
            # Verificar contraseña
            if not verificar_contraseña(form_data.password, usuario.password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Credenciales incorrectas"
                )
            
            # Crear token
            token = crear_token(data={"sub": usuario.username})
            
            # Auditoría: login exitoso
            try:
                registrar_evento(
                    db,
                    accion="login",
                    usuario_id=usuario.id_usuario,
                    entidad_tipo="Usuario",
                    entidad_id=usuario.id_usuario,
                    detalle="Login exitoso",
                )
            except Exception:
                # No bloquear login si falla auditoría
                pass

            return Token(
                access_token=token,
                token_type="bearer",
                id_usuario=usuario.id_usuario,
                nombre=usuario.nombre,
                username=usuario.username,
                role=usuario.role
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno del servidor: {str(e)}"
            )