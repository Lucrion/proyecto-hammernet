#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modelos relacionados con inventario
"""

from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .base import Base


class InventarioDB(Base):
    """Modelo de base de datos para inventario"""
    __tablename__ = "inventario"
    
    id_inventario = Column(Integer, primary_key=True, index=True)
    id_producto = Column(Integer, ForeignKey("productos.id_producto"), nullable=False)
    precio = Column(Integer, nullable=False)
    cantidad = Column(Integer, nullable=False)
    fecha_registro = Column(DateTime, default=func.now())
    
    # Relación
    producto = relationship("ProductoDB", back_populates="inventarios")


# Modelos Pydantic para validación y serialización

class InventarioBase(BaseModel):
    """Modelo base para inventario"""
    id_producto: int
    precio: int
    cantidad: int


class InventarioCreate(InventarioBase):
    """Modelo para crear inventario"""
    pass


class InventarioUpdate(BaseModel):
    """Modelo para actualizar inventario"""
    precio: Optional[int] = None
    cantidad: Optional[int] = None


class Inventario(InventarioBase):
    """Modelo de respuesta para inventario"""
    id_inventario: int
    fecha_registro: Optional[str] = None
    producto: Optional[dict] = None
    
    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }