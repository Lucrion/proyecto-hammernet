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


def _rut_a_int(rut) -> int:
    """Convierte un RUT con formato (con puntos/guion) a entero (solo dígitos).
    Acepta int y str; si es str, se extraen solo dígitos, descartando DV.
    """
    if rut is None:
        return None
    if isinstance(rut, int):
        return rut
    s = str(rut).strip()
    digits = ''.join(ch for ch in s if ch.isdigit())
    if not digits:
        return None
    # Si el string original contiene separadores/formato (guion, puntos, K/k), asumir DV presente y descartar último dígito
    has_format = ('-' in s) or ('.' in s) or ('k' in s.lower())
    if has_format and len(digits) >= 2:
        body = digits[:-1]
    else:
        # Si no hay formato, usar todos los dígitos tal cual (no asumir DV)
        body = digits
    return int(body) if body else None


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
            s = str(form_data.username).strip()
            usuario = None
            if '@' in s:
                usuario = db.query(UsuarioDB).filter(UsuarioDB.email == s).first()
            else:
                digits = ''.join(ch for ch in s if ch.isdigit())
                rut_body = digits[:-1] if len(digits) >= 2 else digits
                if rut_body:
                    usuario = db.query(UsuarioDB).filter(UsuarioDB.rut == int(rut_body)).first()
                if not usuario and digits:
                    try:
                        usuario = db.query(UsuarioDB).filter(UsuarioDB.rut == int(digits)).first()
                    except Exception:
                        usuario = None
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
            
            # Crear token con el RUT como 'sub' (como string)
            # Crear token usando el RUT si existe, de lo contrario el email
            subject = str(usuario.rut) if usuario.rut is not None else str(usuario.email)
            token = crear_token(data={"sub": subject})
            
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
                rut=usuario.rut,
                role=usuario.role
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno del servidor: {str(e)}"
            )
