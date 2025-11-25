#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de autenticación y autorización para la API de Hammernet.

Este módulo implementa un sistema completo de autenticación y autorización mediante
JSON Web Tokens (JWT) y gestión segura de contraseñas con hashing bcrypt. Proporciona:

1. Funciones para verificar y hashear contraseñas de forma segura
2. Generación y verificación de tokens JWT para autenticación sin estado
3. Middleware para proteger rutas que requieren autenticación
4. Compatibilidad con almacenamiento en base de datos SQL o archivos JSON

El sistema está diseñado para ser seguro y flexible, permitiendo su uso tanto
en entornos de desarrollo como de producción, con configuración a través de
variables de entorno.
"""

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
import json
import os
from config.database import get_db
from sqlalchemy.orm import Session

# Configuración del hash de contraseñas usando PBKDF2-SHA256
# PBKDF2 es un algoritmo de derivación de clave robusto para contraseñas
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Configuración de JWT (JSON Web Tokens)
# La clave secreta debe ser segura y cambiada en producción
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "clave_por_defecto_desarrollo_no_usar_en_produccion")
ALGORITHM = "HS256"  # Algoritmo de firma HMAC-SHA256
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Configuración del esquema OAuth2 para FastAPI
# Esto permite usar el endpoint 'login' para obtener tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def verificar_contraseña(plain_password, hashed_password):
    """Verifica si la contraseña en texto plano coincide con el hash almacenado.
    
    Maneja los siguientes casos:
    1. Hash PBKDF2-SHA256 (nuevo esquema: comienza con '$pbkdf2-sha256$')
    2. Hash bcrypt (compatibilidad temporal: comienza con '$2')
    3. Texto plano (compatibilidad con datos antiguos)
    """
    try:
        # PBKDF2-SHA256 (nuevo esquema)
        if hashed_password.startswith("$pbkdf2-sha256$"):
            return pwd_context.verify(plain_password, hashed_password)
        
        # Compatibilidad temporal con bcrypt sin usar el handler de passlib
        if hashed_password.startswith("$2"):
            try:
                import bcrypt
                return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
            except Exception as e:
                print(f"Error al verificar contraseña (bcrypt): {e}")
                return False
        
        # Compatibilidad con contraseñas en texto plano (no hasheadas)
        return plain_password == hashed_password
    except Exception as e:
        print(f"Error al verificar contraseña: {e}")
        return False

def hash_contraseña(password):
    """Genera un hash seguro de la contraseña usando PBKDF2-SHA256."""
    return pwd_context.hash(password)

def crear_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crea un token JWT (JSON Web Token) para autenticación.
    
    Args:
        data: Diccionario con los datos a incluir en el token (debe contener 'sub' con el RUT)
        expires_delta: Tiempo de expiración personalizado (opcional)
        
    Returns:
        str: Token JWT codificado
    """
    # Crear una copia de los datos para no modificar el original
    to_encode = data.copy()
    
    # Calcular tiempo de expiración (valor por defecto o personalizado)
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    
    # Agregar tiempo de expiración al payload
    to_encode.update({"exp": expire})
    
    # Codificar el token con la clave secreta y el algoritmo configurado
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def verificar_token(token: str):
    """Verifica y decodifica un token JWT.
    
    Args:
        token: Token JWT a verificar
        
    Returns:
        dict: Diccionario con el rut extraído del token, o None si el token es inválido
    """
    try:
        # Decodificar el token usando la clave secreta y el algoritmo configurado
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extraer el valor del campo 'sub' (puede ser RUT o email según flujo)
        subject: str = payload.get("sub")
        if subject is None:
            return None
            
        return {"rut": subject}
    except JWTError:
        # Si hay cualquier error en la decodificación, el token es inválido
        return None

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Obtiene el usuario actual a partir del token JWT.
    
    Esta función actúa como una dependencia inyectable en FastAPI para proteger rutas.
    Verifica el token JWT y busca el usuario correspondiente en la base de datos o en JSON.
    
    Args:
        token: Token JWT obtenido del header Authorization (inyectado por FastAPI)
        db: Sesión de base de datos (inyectada por FastAPI)
        
    Returns:
        dict | UsuarioDB: Datos del usuario autenticado
        
    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    # Excepción estándar para credenciales inválidas
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},  # Requerido por el estándar OAuth2
    )
    
    # Verificar el token JWT
    user_data = verificar_token(token)
    if user_data is None:
        raise credentials_exception

    # Extraer el subject del token (puede ser RUT numérico o email)
    subject = user_data["rut"]

    # Intentar interpretar el subject como RUT entero
    rut_int = None
    try:
        rut_int = int(str(subject))
    except Exception:
        rut_int = None

    # Buscar el usuario en la base de datos
    from models import UsuarioDB
    user = None
    if rut_int is not None:
        user = db.query(UsuarioDB).filter(UsuarioDB.rut == rut_int).first()
    
    # Compatibilidad: si no se encontró por RUT, intentar por email
    if user is None:
        user = db.query(UsuarioDB).filter(UsuarioDB.email == str(subject)).first()

    if user is None:
        raise credentials_exception
    return user

def verificar_permisos_admin(current_user, accion: str = "realizar esta acción"):
    """Verifica permisos de administrador.
    
    TEMPORALMENTE DESACTIVADO: Se omite la verificación de rol para avanzar más rápido.
    Las comprobaciones originales quedan comentadas y se reactivarán más adelante.
    """
    # ORIGINAL:
    # if current_user.role != "administrador":
    #     raise HTTPException(
    #         status_code=403,
    #         detail=f"No tienes permisos para {accion}"
    #     )
    if getattr(current_user, "role", None) != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No tienes permisos para {accion}"
        )
    return True

def es_administrador(current_user) -> bool:
    """Verifica si el usuario actual es administrador.
    
    Args:
        current_user: Usuario actual obtenido de get_current_user
        
    Returns:
        bool: True si el usuario es administrador, False en caso contrario
    """
    try:
        if getattr(current_user, "role", None) == "administrador":
            return True
        if getattr(current_user, "rol_ref", None) and getattr(current_user.rol_ref, "nombre", None) == "administrador":
            return True
    except Exception:
        pass
    return False


async def require_admin(current_user = Depends(get_current_user)):
    """Dependencia de administrador.
    
    TEMPORALMENTE DESACTIVADO: No se bloqueará por rol. Se retorna el usuario actual.
    Nota: Esta función mantiene la autenticación (requiere token válido) vía get_current_user.
    """
    # ORIGINAL:
    # if current_user.role != "administrador":
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="No tienes permisos de administrador para realizar esta acción"
    #     )
    if not es_administrador(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos de administrador para realizar esta acción")
    return current_user

# Validación estricta de clave JWT en producción
ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
if ENVIRONMENT == "production" and SECRET_KEY == "clave_por_defecto_desarrollo_no_usar_en_produccion":
    raise RuntimeError("JWT_SECRET_KEY no configurado en producción")