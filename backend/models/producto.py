#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modelos relacionados con productos (unificado con inventario)
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, DECIMAL, Boolean, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from .base import Base


class ProductoDB(Base):
    """Modelo de base de datos para productos unificado con inventario"""
    __tablename__ = "productos"
    __table_args__ = (
        Index('ix_productos_nombre', 'nombre'),
        Index('ix_productos_catalogo', 'en_catalogo', 'estado'),
        Index('ix_productos_categoria', 'id_categoria'),
        Index('ix_productos_subcategoria', 'id_subcategoria'),
    )
    
    id_producto = Column(Integer, primary_key=True, index=True)
    
    # Información básica del producto
    nombre = Column(String(200), nullable=False)
    descripcion = Column(String, nullable=True)
    codigo_interno = Column(String(50), unique=True, nullable=True)
    imagen_url = Column(String(500), nullable=True)
    id_categoria = Column(Integer, ForeignKey("categorias.id_categoria"), nullable=False)
    id_proveedor = Column(Integer, ForeignKey("proveedores.id_proveedor"), nullable=True)
    id_subcategoria = Column(Integer, ForeignKey("subcategorias.id_subcategoria"), nullable=True)
    marca = Column(String(100), nullable=True)
    # Detalles adicionales
    garantia_meses = Column(Integer, nullable=True)
    modelo = Column(String(100), nullable=True)
    color = Column(String(50), nullable=True)
    material = Column(String(100), nullable=True)
    
    # Información de costos y precios
    costo_bruto = Column(DECIMAL(12,2), default=0, nullable=False)
    costo_neto = Column(DECIMAL(12,2), default=0, nullable=False)
    precio_venta = Column(DECIMAL(12,2), default=0, nullable=False)
    porcentaje_utilidad = Column(DECIMAL(5,2), default=0, nullable=True)
    utilidad_pesos = Column(DECIMAL(12,2), default=0, nullable=True)
    
    # Información de inventario (integrada)
    cantidad_disponible = Column(Integer, default=0, nullable=False)
    stock_minimo = Column(Integer, default=0, nullable=False)
    
    # Estados y fechas
    estado = Column(String(20), default="activo", nullable=False)
    en_catalogo = Column(Boolean, default=False, nullable=False)  # Nuevo campo para indicar si está en catálogo público
    caracteristicas = Column(String, nullable=True)  # Nuevo campo para características del producto
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now())
    fecha_ultima_venta = Column(DateTime, nullable=True)
    fecha_ultimo_ingreso = Column(DateTime, nullable=True)

    # Ofertas
    oferta_activa = Column(Boolean, default=False, nullable=False)
    tipo_oferta = Column(String(20), nullable=True)  # 'porcentaje' | 'fijo'
    valor_oferta = Column(DECIMAL(12,2), default=0, nullable=True)
    fecha_inicio_oferta = Column(DateTime, nullable=True)
    fecha_fin_oferta = Column(DateTime, nullable=True)
    
    # Relaciones
    categoria = relationship("CategoriaDB", back_populates="productos")
    subcategoria = relationship("SubCategoriaDB", back_populates="productos")
    proveedor = relationship("ProveedorDB", back_populates="productos")
    detalles_venta = relationship("DetalleVentaDB", back_populates="producto")
    movimientos_inventario = relationship("MovimientoInventarioDB", back_populates="producto")


# Modelos Pydantic para validación y serialización

class ProductoBase(BaseModel):
    """Modelo base para producto unificado"""
    nombre: str
    descripcion: Optional[str] = None
    codigo_interno: Optional[str] = None
    imagen_url: Optional[str] = None
    id_categoria: int
    id_proveedor: Optional[int] = None
    id_subcategoria: Optional[int] = None
    marca: Optional[str] = None
    # Detalles adicionales
    garantia_meses: Optional[int] = None
    modelo: Optional[str] = None
    color: Optional[str] = None
    material: Optional[str] = None
    
    # Costos y precios
    costo_bruto: Optional[float] = 0
    costo_neto: Optional[float] = 0
    precio_venta: float
    porcentaje_utilidad: Optional[float] = 0
    utilidad_pesos: Optional[float] = 0
    
    # Inventario
    cantidad_disponible: Optional[int] = 0
    stock_minimo: Optional[int] = 0
    
    # Estado
    estado: Optional[str] = "activo"
    en_catalogo: Optional[bool] = False  # Nuevo campo para indicar si está en catálogo público
    caracteristicas: Optional[str] = None  # Nuevo campo para características del producto
    # Ofertas
    oferta_activa: Optional[bool] = False
    tipo_oferta: Optional[str] = None
    valor_oferta: Optional[float] = 0
    fecha_inicio_oferta: Optional[datetime] = None
    fecha_fin_oferta: Optional[datetime] = None

    @validator(
        "costo_bruto", "costo_neto", "precio_venta", "porcentaje_utilidad", "utilidad_pesos", "valor_oferta",
        pre=True
    )
    def _cast_float_non_negative(cls, v):
        if v is None:
            return v
        try:
            v_cast = float(v)
        except (TypeError, ValueError):
            return v
        if v_cast < 0:
            raise ValueError("El valor no puede ser negativo")
        return v_cast

    @validator("cantidad_disponible", "stock_minimo", pre=True)
    def _cast_int_non_negative(cls, v):
        if v is None:
            return v
        try:
            v_cast = int(v)
        except (TypeError, ValueError):
            return v
        if v_cast < 0:
            raise ValueError("El valor no puede ser negativo")
        return v_cast


class ProductoCreate(ProductoBase):
    """Modelo para crear producto"""
    pass


class ProductoUpdate(BaseModel):
    """Modelo para actualizar producto"""
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    codigo_interno: Optional[str] = None
    imagen_url: Optional[str] = None
    id_categoria: Optional[int] = None
    id_proveedor: Optional[int] = None
    id_subcategoria: Optional[int] = None
    marca: Optional[str] = None
    # Detalles adicionales
    garantia_meses: Optional[int] = None
    modelo: Optional[str] = None
    color: Optional[str] = None
    material: Optional[str] = None
    
    # Costos y precios
    costo_bruto: Optional[float] = None
    costo_neto: Optional[float] = None
    precio_venta: Optional[float] = None
    porcentaje_utilidad: Optional[float] = None
    utilidad_pesos: Optional[float] = None
    
    # Inventario
    cantidad_disponible: Optional[int] = None
    stock_minimo: Optional[int] = None
    
    # Estado
    estado: Optional[str] = None
    en_catalogo: Optional[bool] = None  # Nuevo campo para indicar si está en catálogo público
    caracteristicas: Optional[str] = None  # Nuevo campo para características del producto
    # Ofertas
    oferta_activa: Optional[bool] = None
    tipo_oferta: Optional[str] = None
    valor_oferta: Optional[float] = None
    fecha_inicio_oferta: Optional[datetime] = None
    fecha_fin_oferta: Optional[datetime] = None

    @validator(
        "costo_bruto", "costo_neto", "precio_venta", "porcentaje_utilidad", "utilidad_pesos", "valor_oferta",
        pre=True
    )
    def _cast_float_non_negative_update(cls, v):
        if v is None:
            return v
        try:
            v_cast = float(v)
        except (TypeError, ValueError):
            return v
        if v_cast < 0:
            raise ValueError("El valor no puede ser negativo")
        return v_cast

    @validator("cantidad_disponible", "stock_minimo", pre=True)
    def _cast_int_non_negative_update(cls, v):
        if v is None:
            return v
        try:
            v_cast = int(v)
        except (TypeError, ValueError):
            return v
        if v_cast < 0:
            raise ValueError("El valor no puede ser negativo")
        return v_cast


class Producto(ProductoBase):
    """Modelo completo de producto con información de inventario"""
    id_producto: int
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None
    fecha_ultima_venta: Optional[datetime] = None
    fecha_ultimo_ingreso: Optional[datetime] = None
    categoria: Optional[str] = None  # Nombre de la categoría
    proveedor: Optional[str] = None  # Nombre del proveedor
    subcategoria: Optional[str] = None  # Nombre de la subcategoría
    
    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


# Modelo de compatibilidad para inventario (mantener para endpoints existentes)
class ProductoInventario(BaseModel):
    """Modelo de compatibilidad para inventario"""
    id_inventario: int  # Será igual a id_producto
    id_producto: int
    precio: float  # Será precio_venta
    cantidad: int  # Será cantidad_disponible
    fecha_registro: Optional[str] = None  # Será fecha_creacion
    producto: Optional[dict] = None
    
    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }