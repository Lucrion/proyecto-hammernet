#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modelo y esquemas para direcciones de despacho de usuarios
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .base import Base


class DespachoDB(Base):
    """Dirección de despacho asociada a un usuario (1:N)"""
    __tablename__ = "despachos"

    id_despacho = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False, index=True)

    # Campos de dirección
    buscar = Column(String(255), nullable=True)  # Texto completo ingresado/seleccionado
    calle = Column(String(120), nullable=False)
    numero = Column(String(30), nullable=False)
    depto = Column(String(60), nullable=True)
    adicional = Column(String(255), nullable=True)

    # Metadatos
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relación inversa
    usuario = relationship("UsuarioDB", back_populates="direcciones_despacho")


# Esquemas Pydantic
class DespachoBase(BaseModel):
    buscar: Optional[str] = None
    calle: str
    numero: str
    depto: Optional[str] = None
    adicional: Optional[str] = None


class DespachoCreate(DespachoBase):
    pass


class DespachoUpdate(BaseModel):
    buscar: Optional[str] = None
    calle: Optional[str] = None
    numero: Optional[str] = None
    depto: Optional[str] = None
    adicional: Optional[str] = None


class Despacho(DespachoBase):
    id_despacho: int
    id_usuario: int
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        orm_mode = True