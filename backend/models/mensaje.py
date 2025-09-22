#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modelos relacionados con mensajes de contacto
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from pydantic import BaseModel, Field, EmailStr
from .base import Base


class MensajeContactoDB(Base):
    """Modelo de base de datos para mensajes de contacto"""
    __tablename__ = "mensajes_contacto"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    asunto = Column(String(200), nullable=False)
    mensaje = Column(String(1000), nullable=False)
    fecha_envio = Column(DateTime, default=func.now())
    leido = Column(Boolean, default=False)


# Modelos Pydantic para validación y serialización

class MensajeContactoBase(BaseModel):
    """Modelo base para mensaje de contacto"""
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre del remitente")
    apellido: str = Field(..., min_length=2, max_length=50, description="Apellido del remitente")
    email: EmailStr = Field(..., description="Correo electrónico del remitente")
    asunto: str = Field(..., min_length=5, max_length=200, description="Asunto del mensaje")
    mensaje: str = Field(..., min_length=10, max_length=1000, description="Contenido del mensaje")

    class Config:
        schema_extra = {
            'example': {
                'nombre': 'Juan',
                'apellido': 'Pérez',
                'email': 'juan.perez@example.com',
                'asunto': 'Consulta sobre productos',
                'mensaje': 'Me gustaría obtener más información sobre sus productos.'
            }
        }


class MensajeContactoCreate(MensajeContactoBase):
    """Modelo para crear mensaje de contacto"""
    pass


class MensajeContacto(MensajeContactoBase):
    """Modelo de respuesta para mensaje de contacto"""
    id: int
    fecha_envio: str
    leido: bool
    
    class Config:
        orm_mode = True