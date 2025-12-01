#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modelos relacionados con ventas y movimientos de inventario
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Numeric, Text, Index, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from .base import Base


class VentaDB(Base):
    """Modelo de base de datos para ventas"""
    __tablename__ = "ventas"
    __table_args__ = (
        Index('ix_ventas_fecha_venta', 'fecha_venta'),
        Index('ix_ventas_estado', 'estado'),
        Index('ix_ventas_usuario', 'rut_usuario'),
        Index('ix_ventas_estado_envio', 'estado_envio'),
        Index('ix_ventas_repartidor', 'repartidor_rut'),
        Index('ix_ventas_despacho', 'despacho_id'),
        Index('ix_ventas_fecha_entrega', 'fecha_entrega'),
    )
    
    id_venta = Column(Integer, primary_key=True, index=True)
    rut_usuario = Column(String(9), ForeignKey("usuarios.rut"), nullable=True)
    fecha_venta = Column(DateTime, default=func.now(), nullable=False)
    total_venta = Column(Numeric(10, 2), nullable=False)
    estado = Column(String(20), default="completada", nullable=False)  # completada, cancelada, pendiente
    observaciones = Column(Text, nullable=True)
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())
    despacho_id = Column(Integer, ForeignKey("despachos.id_despacho"), nullable=True)
    metodo_entrega = Column(String(20), default="despacho", nullable=True)
    estado_envio = Column(String(30), default="pendiente", nullable=True)
    repartidor_rut = Column(String(9), ForeignKey("usuarios.rut"), nullable=True)
    ventana_inicio = Column(DateTime, nullable=True)
    ventana_fin = Column(DateTime, nullable=True)
    fecha_asignacion = Column(DateTime, nullable=True)
    fecha_despacho = Column(DateTime, nullable=True)
    fecha_entrega = Column(DateTime, nullable=True)
    prueba_entrega_url = Column(String(255), nullable=True)
    geo_entrega_lat = Column(Numeric(9, 6), nullable=True)
    geo_entrega_lng = Column(Numeric(9, 6), nullable=True)
    motivo_no_entrega = Column(String(255), nullable=True)
    
    # Relaciones
    usuario = relationship("UsuarioDB", foreign_keys=[rut_usuario], back_populates="ventas")
    repartidor = relationship("UsuarioDB", foreign_keys=[repartidor_rut])
    direccion_despacho = relationship("DespachoDB")
    detalles_venta = relationship("DetalleVentaDB", back_populates="venta", cascade="all, delete-orphan")
    movimientos_inventario = relationship("MovimientoInventarioDB", back_populates="venta")
    pagos = relationship("PagoDB", back_populates="venta")


class DetalleVentaDB(Base):
    """Modelo de base de datos para detalles de venta"""
    __tablename__ = "detalles_venta"
    __table_args__ = (
        Index('ix_detalles_venta_id_venta', 'id_venta'),
    )
    
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
    __table_args__ = (
        Index('ix_movimientos_producto_fecha', 'id_producto', 'fecha_movimiento'),
    )
    
    id_movimiento = Column(Integer, primary_key=True, index=True)
    id_producto = Column(Integer, ForeignKey("productos.id_producto"), nullable=False)
    rut_usuario = Column(String(9), ForeignKey("usuarios.rut"), nullable=True)
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
    rut_usuario: Optional[str] = None
    total_venta: Decimal
    estado: Optional[str] = "completada"
    observaciones: Optional[str] = None
    despacho_id: Optional[int] = None
    metodo_entrega: Optional[str] = None
    estado_envio: Optional[str] = None
    repartidor_rut: Optional[str] = None
    ventana_inicio: Optional[datetime] = None
    ventana_fin: Optional[datetime] = None


class VentaCreate(VentaBase):
    """Modelo para crear venta"""
    detalles: List['DetalleVentaCreate']


class VentaGuestCreate(BaseModel):
    """Modelo para crear venta como invitado (sin id_usuario)"""
    total_venta: Decimal
    estado: Optional[str] = "completada"
    observaciones: Optional[str] = None
    detalles: List['DetalleVentaCreate']
    guest_info: Optional[dict] = None  # Datos del cliente invitado y entrega


class VentaUpdate(BaseModel):
    """Modelo para actualizar venta"""
    estado: Optional[str] = None
    observaciones: Optional[str] = None
    estado_envio: Optional[str] = None
    despacho_id: Optional[int] = None
    repartidor_rut: Optional[str] = None
    ventana_inicio: Optional[datetime] = None
    ventana_fin: Optional[datetime] = None
    prueba_entrega_url: Optional[str] = None
    geo_entrega_lat: Optional[float] = None
    geo_entrega_lng: Optional[float] = None
    motivo_no_entrega: Optional[str] = None


class Venta(VentaBase):
    """Modelo completo de venta"""
    id_venta: int
    fecha_venta: datetime
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    usuario_rut: Optional[str] = None
    usuario_nombre: Optional[str] = None
    cliente_nombre: Optional[str] = None
    repartidor_nombre: Optional[str] = None
    usuario_apellido: Optional[str] = None
    cliente_apellido: Optional[str] = None
    repartidor_apellido: Optional[str] = None
    fecha_asignacion: Optional[datetime] = None
    fecha_despacho: Optional[datetime] = None
    fecha_entrega: Optional[datetime] = None
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
    rut_usuario: Optional[str] = None
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
VentaGuestCreate.update_forward_refs()
