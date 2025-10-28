#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modelos relacionados con ventas y movimientos de inventario
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Numeric, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from .base import Base


class VentaDB(Base):
    """Modelo de base de datos para ventas"""
    __tablename__ = "ventas"
    
    id_venta = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    fecha_venta = Column(DateTime, default=func.now(), nullable=False)
    total_venta = Column(Numeric(10, 2), nullable=False)
    estado = Column(String(20), default="completada", nullable=False)  # completada, cancelada, pendiente
    observaciones = Column(Text, nullable=True)
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relaciones
    usuario = relationship("UsuarioDB", back_populates="ventas")
    detalles_venta = relationship("DetalleVentaDB", back_populates="venta", cascade="all, delete-orphan")
    movimientos_inventario = relationship("MovimientoInventarioDB", back_populates="venta")


class DetalleVentaDB(Base):
    """Modelo de base de datos para detalles de venta"""
    __tablename__ = "detalles_venta"
    
    id_detalle = Column(Integer, primary_key=True, index=True)
    id_venta = Column(Integer, ForeignKey("ventas.id_venta"), nullable=False)
    id_producto = Column(Integer, ForeignKey("productos.id_producto"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)
    fecha_creacion = Column(DateTime, default=func.now())
    
    # Relaciones
    venta = relationship("VentaDB", back_populates="detalles_venta")
    producto = relationship("ProductoDB", back_populates="detalles_venta")


class MovimientoInventarioDB(Base):
    """Modelo de base de datos para movimientos de inventario"""
    __tablename__ = "movimientos_inventario"
    
    id_movimiento = Column(Integer, primary_key=True, index=True)
    id_producto = Column(Integer, ForeignKey("productos.id_producto"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_venta = Column(Integer, ForeignKey("ventas.id_venta"), nullable=True)  # Opcional para otros tipos de movimientos
    tipo_movimiento = Column(String(20), nullable=False)  # venta, entrada, ajuste, devolucion
    cantidad = Column(Integer, nullable=False)  # Positivo para entradas, negativo para salidas
    cantidad_anterior = Column(Integer, nullable=False)
    cantidad_nueva = Column(Integer, nullable=False)
    motivo = Column(String(255), nullable=True)
    fecha_movimiento = Column(DateTime, default=func.now(), nullable=False)
    fecha_creacion = Column(DateTime, default=func.now())
    
    # Relaciones
    producto = relationship("ProductoDB", back_populates="movimientos_inventario")
    usuario = relationship("UsuarioDB", back_populates="movimientos_inventario")
    venta = relationship("VentaDB", back_populates="movimientos_inventario")


# Modelos Pydantic para validación y serialización

class VentaBase(BaseModel):
    """Modelo base para venta"""
    id_usuario: int
    total_venta: Decimal
    estado: Optional[str] = "completada"
    observaciones: Optional[str] = None


class VentaCreate(VentaBase):
    """Modelo para crear venta"""
    detalles: List['DetalleVentaCreate']


class VentaUpdate(BaseModel):
    """Modelo para actualizar venta"""
    estado: Optional[str] = None
    observaciones: Optional[str] = None


class Venta(VentaBase):
    """Modelo completo de venta"""
    id_venta: int
    fecha_venta: datetime
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    usuario: Optional[str] = None  # Nombre del usuario
    detalles_venta: Optional[List['DetalleVenta']] = []
    
    class Config:
        from_attributes = True


class DetalleVentaBase(BaseModel):
    """Modelo base para detalle de venta"""
    id_producto: int
    cantidad: int
    precio_unitario: Decimal


class DetalleVentaCreate(DetalleVentaBase):
    """Modelo para crear detalle de venta"""
    pass


class DetalleVenta(DetalleVentaBase):
    """Modelo completo de detalle de venta"""
    id_detalle: int
    id_venta: int
    subtotal: Decimal
    fecha_creacion: datetime
    producto_nombre: Optional[str] = None  # Nombre del producto
    
    class Config:
        from_attributes = True


class MovimientoInventarioBase(BaseModel):
    """Modelo base para movimiento de inventario"""
    id_producto: int
    id_usuario: int
    tipo_movimiento: str
    cantidad: int
    cantidad_anterior: int
    cantidad_nueva: int
    motivo: Optional[str] = None


class MovimientoInventarioCreate(MovimientoInventarioBase):
    """Modelo para crear movimiento de inventario"""
    pass


class MovimientoInventario(MovimientoInventarioBase):
    """Modelo completo de movimiento de inventario"""
    id_movimiento: int
    id_venta: Optional[int] = None
    fecha_movimiento: datetime
    fecha_creacion: datetime
    producto_nombre: Optional[str] = None
    usuario_nombre: Optional[str] = None
    
    class Config:
        from_attributes = True


# Actualizar referencias forward
VentaCreate.update_forward_refs()
Venta.update_forward_refs()