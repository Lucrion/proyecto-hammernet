#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modelos relacionados con usuarios
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .base import Base


class UsuarioDB(Base):
    """Modelo de base de datos para usuarios"""
    __tablename__ = "usuarios"
    rut = Column(String(9), primary_key=True, unique=True, index=True, nullable=False)
    id_rol = Column(Integer, ForeignKey("roles.id_rol"), nullable=True)
    nombre = Column(String(50), nullable=False)
    apellido = Column(String(50), nullable=True)
    email = Column(String(120), unique=False, nullable=True)
    telefono = Column(String(20), nullable=True)
    password = Column(String(255), nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=func.now())
    
    # Relaciones
    ventas = relationship("VentaDB", back_populates="usuario", primaryjoin="UsuarioDB.rut==VentaDB.rut_usuario")
    ventas_como_cliente = relationship("VentaDB", primaryjoin="UsuarioDB.rut==VentaDB.cliente_rut")
    movimientos_inventario = relationship("MovimientoInventarioDB", back_populates="usuario")
    direcciones_despacho = relationship("DespachoDB", back_populates="usuario", cascade="all, delete-orphan")
    rol_ref = relationship("RolDB", back_populates="usuarios")


# Modelos Pydantic para validación y serialización

class UsuarioBase(BaseModel):
    """Modelo base para usuario"""
    nombre: str
    apellido: Optional[str] = None
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
    rut: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None


class Usuario(UsuarioBase):
    """Modelo completo para usuario"""
    rut: Optional[str] = None
    activo: Optional[bool] = True
    fecha_creacion: Optional[str] = None
    
    class Config:
        from_attributes = True


class UsuarioLogin(BaseModel):
    """Modelo para login de usuario"""
    rut: str
    password: str


class Token(BaseModel):
    """Modelo para token de autenticación"""
    access_token: str
    token_type: str
    rut: Optional[str] = None
    nombre: str
    role: str
