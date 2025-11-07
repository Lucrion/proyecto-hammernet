#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modelos de auditoría
Registra eventos del sistema: login, CRUD de productos, cambios de inventario
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .base import Base


class AuditoriaDB(Base):
    """Tabla de auditoría de eventos"""
    __tablename__ = "auditoria"

    id_evento = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, nullable=True, index=True)
    accion = Column(String(100), nullable=False, index=True)
    entidad_tipo = Column(String(100), nullable=True, index=True)
    entidad_id = Column(Integer, nullable=True, index=True)
    detalle = Column(String, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    fecha_evento = Column(DateTime, default=func.now(), index=True)


class AuditoriaBase(BaseModel):
    usuario_id: Optional[int] = Field(None, description="ID del usuario asociado al evento")
    accion: str = Field(..., description="Acción realizada (login, crear, actualizar, eliminar, inventario)")
    entidad_tipo: Optional[str] = Field(None, description="Tipo de entidad afectada (Producto, Inventario, Usuario, etc.)")
    entidad_id: Optional[int] = Field(None, description="ID de la entidad afectada")
    detalle: Optional[str] = Field(None, description="Detalle adicional del evento en formato texto/JSON")
    ip_address: Optional[str] = Field(None, description="Dirección IP del cliente")
    user_agent: Optional[str] = Field(None, description="User-Agent del cliente")


class AuditoriaCreate(AuditoriaBase):
    pass


class Auditoria(AuditoriaBase):
    id_evento: int
    fecha_evento: datetime

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }