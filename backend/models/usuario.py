#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modelos relacionados con usuarios
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .base import Base


class UsuarioDB(Base):
    """Modelo de base de datos para usuarios"""
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    fecha_creacion = Column(DateTime, default=func.now())


# Modelos Pydantic para validación y serialización

class UsuarioBase(BaseModel):
    """Modelo base para usuario"""
    nombre: str
    username: str
    role: str


class UsuarioCreate(UsuarioBase):
    """Modelo para crear usuario"""
    password: str


class UsuarioUpdate(BaseModel):
    """Modelo para actualizar usuario"""
    nombre: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None


class Usuario(UsuarioBase):
    """Modelo de respuesta para usuario"""
    id: int
    fecha_creacion: Optional[str] = None
    
    class Config:
        orm_mode = True


class UsuarioLogin(BaseModel):
    """Modelo para login de usuario"""
    username: str
    password: str


class Token(BaseModel):
    """Modelo para token de autenticación"""
    access_token: str
    token_type: str
    id: int
    nombre: str
    username: str
    role: str