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
from database import get_db
from sqlalchemy.orm import Session

# Configuración del hash de contraseñas usando bcrypt
# bcrypt es un algoritmo de hashing seguro diseñado específicamente para contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración de JWT (JSON Web Tokens)
# La clave secreta debe ser segura y cambiada en producción
SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
ALGORITHM = "HS256"  # Algoritmo de firma HMAC-SHA256
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Configuración del esquema OAuth2 para FastAPI
# Esto permite usar el endpoint 'login' para obtener tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verificar_contraseña(plain_password, hashed_password):
    """Verifica si la contraseña en texto plano coincide con el hash almacenado.
    
    Esta función maneja dos casos:
    1. Contraseñas hasheadas con bcrypt (comienzan con '$2')
    2. Contraseñas en texto plano (compatibilidad con datos antiguos)
    
    Args:
        plain_password: Contraseña en texto plano proporcionada por el usuario
        hashed_password: Hash o contraseña almacenada en la base de datos
        
    Returns:
        bool: True si la contraseña coincide, False en caso contrario
    """
    # Compatibilidad con contraseñas en texto plano (no hasheadas)
    # Si la contraseña almacenada no es un hash bcrypt (no comienza con $2)
    # entonces comparamos directamente (para contraseñas en texto plano)
    if not hashed_password.startswith("$2"):
        return plain_password == hashed_password
    
    # Si es un hash bcrypt, usamos el verificador de passlib
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        # Si hay un error al verificar (por ejemplo, el hash no es válido)
        print(f"Error al verificar contraseña: {e}")
        return False

def hash_contraseña(password):
    """Genera un hash seguro de la contraseña usando bcrypt.
    
    Args:
        password: Contraseña en texto plano a hashear
        
    Returns:
        str: Hash de la contraseña generado con bcrypt
    """
    return pwd_context.hash(password)

def crear_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crea un token JWT (JSON Web Token) para autenticación.
    
    Args:
        data: Diccionario con los datos a incluir en el token (debe contener 'sub' con el username)
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
        dict: Diccionario con el username extraído del token, o None si el token es inválido
    """
    try:
        # Decodificar el token usando la clave secreta y el algoritmo configurado
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extraer el username del campo 'sub' (subject)
        username: str = payload.get("sub")
        if username is None:
            return None
            
        return {"username": username}
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
    
    # Extraer el username del token verificado
    username = user_data["username"]

    # Buscar el usuario en la base de datos
    from models import UsuarioDB
    user = db.query(UsuarioDB).filter(UsuarioDB.username == username).first()
    if user is None:
        raise credentials_exception
    return user