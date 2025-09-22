#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modelos relacionados con proveedores
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional
from .base import Base


class ProveedorDB(Base):
    """Modelo de base de datos para proveedores"""
    __tablename__ = "proveedores"
    
    id_proveedor = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    rut = Column(String(20), nullable=True)
    razon_social = Column(String(200), nullable=True)
    sucursal = Column(String(100), nullable=True)
    direccion = Column(String(200), nullable=True)
    ciudad = Column(String(100), nullable=True)
    celular = Column(String(50), nullable=True)
    correo = Column(String(100), nullable=True)
    contacto = Column(String(100), nullable=True)
    telefono = Column(String(50), nullable=True)
    
    # Relación con productos
    productos = relationship("ProductoDB", back_populates="proveedor")


# Modelos Pydantic para validación y serialización

class ProveedorBase(BaseModel):
    """Modelo base para proveedor"""
    nombre: str
    rut: Optional[str] = None
    razon_social: Optional[str] = None
    sucursal: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    celular: Optional[str] = None
    correo: Optional[str] = None
    contacto: Optional[str] = None
    telefono: Optional[str] = None


class ProveedorCreate(ProveedorBase):
    """Modelo para crear proveedor"""
    pass


class ProveedorUpdate(BaseModel):
    """Modelo para actualizar proveedor"""
    nombre: Optional[str] = None
    rut: Optional[str] = None
    razon_social: Optional[str] = None
    sucursal: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    celular: Optional[str] = None
    correo: Optional[str] = None
    contacto: Optional[str] = None
    telefono: Optional[str] = None


class Proveedor(ProveedorBase):
    """Modelo de respuesta para proveedor"""
    id_proveedor: int
    
    class Config:
        orm_mode = True