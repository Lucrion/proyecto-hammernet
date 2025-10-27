#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modelos relacionados con usuarios
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .base import Base


class UsuarioDB(Base):
    """Modelo de base de datos para usuarios"""
    __tablename__ = "usuarios"
    
    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    apellido = Column(String(50), nullable=True)
    # Para compatibilidad con OAuth2 de FastAPI, seguimos usando 'username'
    # pero guardaremos el RUT normalizado aquí
    username = Column(String(50), unique=True, index=True, nullable=False)
    rut = Column(String(20), unique=True, index=True, nullable=True)
    email = Column(String(120), unique=False, nullable=True)
    telefono = Column(String(20), nullable=True)
    password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=func.now())
    
    # Relaciones
    ventas = relationship("VentaDB", back_populates="usuario")
    movimientos_inventario = relationship("MovimientoInventarioDB", back_populates="usuario")


# Modelos Pydantic para validación y serialización

class UsuarioBase(BaseModel):
    """Modelo base para usuario"""
    nombre: str
    apellido: Optional[str] = None
    username: str
    rut: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    role: str


class UsuarioCreate(UsuarioBase):
    """Modelo para crear usuario"""
    password: str
    confirm_password: Optional[str] = None


class UsuarioUpdate(BaseModel):
    """Modelo para actualizar usuario"""
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    username: Optional[str] = None
    rut: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None


class Usuario(UsuarioBase):
    """Modelo completo para usuario"""
    id_usuario: int
    activo: Optional[bool] = True
    fecha_creacion: Optional[str] = None
    
    class Config:
        from_attributes = True


class UsuarioLogin(BaseModel):
    """Modelo para login de usuario"""
    username: str
    password: str


class Token(BaseModel):
    """Modelo para token de autenticación"""
    access_token: str
    token_type: str
    id_usuario: int
    nombre: str
    username: str
    role: str