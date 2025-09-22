#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modelos relacionados con productos
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .base import Base


class ProductoDB(Base):
    """Modelo de base de datos para productos"""
    __tablename__ = "productos"
    
    id_producto = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(String(1000), nullable=True)
    codigo_interno = Column(String(50), unique=True, nullable=True)
    codigo_barras = Column(String(50), unique=True, nullable=True)
    imagen_url = Column(String(500), nullable=True)
    id_categoria = Column(Integer, ForeignKey("categorias.id_categoria"), nullable=True)
    id_proveedor = Column(Integer, ForeignKey("proveedores.id_proveedor"), nullable=True)
    estado = Column(String(20), default="activo", nullable=False)
    fecha_creacion = Column(DateTime, default=func.now())
    
    # Campos de costos y utilidad
    costo_bruto = Column(Integer, nullable=True)
    costo_neto = Column(Integer, nullable=True)
    porcentaje_utilidad = Column(Integer, nullable=True)  # %utilidad
    utilidad_pesos = Column(Integer, nullable=True)  # Utilidad en $
    cantidad_actual = Column(Integer, default=0, nullable=False)
    stock_minimo = Column(Integer, default=0, nullable=False)
    
    # Relaciones
    categoria = relationship("CategoriaDB", back_populates="productos")
    proveedor = relationship("ProveedorDB", back_populates="productos")
    inventarios = relationship("InventarioDB", back_populates="producto")


# Modelos Pydantic para validación y serialización

class ProductoBase(BaseModel):
    """Modelo base para producto"""
    nombre: str
    descripcion: Optional[str] = None
    codigo_barras: Optional[str] = None
    imagen_url: Optional[str] = None
    id_categoria: Optional[int] = None
    id_proveedor: Optional[int] = None
    estado: Optional[str] = "activo"
    costo_bruto: Optional[int] = None
    costo_neto: Optional[int] = None
    porcentaje_utilidad: Optional[int] = None
    utilidad_pesos: Optional[int] = None
    cantidad_actual: Optional[int] = 0
    stock_minimo: Optional[int] = 0


class ProductoCreate(ProductoBase):
    """Modelo para crear producto"""
    pass


class ProductoUpdate(BaseModel):
    """Modelo para actualizar producto"""
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    codigo_interno: Optional[str] = None
    codigo_barras: Optional[str] = None
    imagen_url: Optional[str] = None
    id_categoria: Optional[int] = None
    id_proveedor: Optional[int] = None
    estado: Optional[str] = None
    costo_bruto: Optional[int] = None
    costo_neto: Optional[int] = None
    porcentaje_utilidad: Optional[int] = None
    utilidad_pesos: Optional[int] = None
    cantidad_actual: Optional[int] = None
    stock_minimo: Optional[int] = None


class Producto(ProductoBase):
    """Modelo para respuesta de producto"""
    id_producto: int
    codigo_interno: Optional[str] = None
    fecha_creacion: Optional[str] = None
    categoria: Optional[str] = None  # Cambiado a string
    proveedor: Optional[str] = None  # Cambiado a string
    
    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


# Modelos adicionales para compatibilidad

class ProductoNuevoBase(BaseModel):
    """Modelo base para producto nuevo (compatibilidad)"""
    nombre: str
    descripcion: Optional[str] = None
    codigo_barras: Optional[str] = None
    imagen_url: Optional[str] = None
    id_categoria: Optional[int] = None
    id_proveedor: Optional[int] = None
    estado: Optional[str] = "activo"
    costo_bruto: Optional[int] = None
    costo_neto: Optional[int] = None
    porcentaje_utilidad: Optional[int] = None
    utilidad_pesos: Optional[int] = None
    cantidad_actual: Optional[int] = 0
    stock_minimo: Optional[int] = 0


class ProductoNuevoCreate(ProductoNuevoBase):
    """Modelo para crear producto nuevo"""
    pass


class ProductoNuevoUpdate(BaseModel):
    """Modelo para actualizar producto nuevo"""
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    codigo_barras: Optional[str] = None
    imagen_url: Optional[str] = None
    id_categoria: Optional[int] = None
    id_proveedor: Optional[int] = None
    estado: Optional[str] = None
    costo_bruto: Optional[int] = None
    costo_neto: Optional[int] = None
    porcentaje_utilidad: Optional[int] = None
    utilidad_pesos: Optional[int] = None
    cantidad_actual: Optional[int] = None
    stock_minimo: Optional[int] = None


class ProductoNuevo(ProductoNuevoBase):
    """Modelo de respuesta para producto nuevo"""
    id_producto: int
    fecha_creacion: Optional[str] = None
    categoria: Optional[dict] = None
    proveedor: Optional[dict] = None
    
    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }