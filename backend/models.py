#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProductoDB(Base):
    __tablename__ = "productos"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(255))
    caracteristicas = Column(String(255))
    precio = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    categoria = Column(String(50))
    imagen = Column(String(255))
    fecha_creacion = Column(DateTime, default=func.now())

class UsuarioDB(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    fecha_creacion = Column(DateTime, default=func.now())

class ProductoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    caracteristicas: Optional[str] = None
    precio: float
    imagen: Optional[str] = None
    categoria: Optional[str] = None
    stock: Optional[int] = 0

class ProductoCreate(ProductoBase):
    pass

class Producto(ProductoBase):
    id: int
    fecha_creacion: Optional[str] = None
    
    class Config:
        orm_mode = True

class UsuarioBase(BaseModel):
    nombre: str
    username: str
    role: str

class UsuarioCreate(UsuarioBase):
    password: str

class Usuario(UsuarioBase):
    id: int
    fecha_creacion: Optional[str] = None
    
    class Config:
        orm_mode = True

class UsuarioLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    id: int
    nombre: str
    username: str
    role: str

class MensajeContactoDB(Base):
    __tablename__ = "mensajes_contacto"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    asunto = Column(String(200), nullable=False)
    mensaje = Column(String(1000), nullable=False)
    fecha_envio = Column(DateTime, default=func.now())
    leido = Column(Boolean, default=False)

from pydantic import BaseModel, Field, EmailStr

class MensajeContactoBase(BaseModel):
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
    pass

class MensajeContacto(MensajeContactoBase):
    id: int
    fecha_envio: str
    leido: bool
    
    class Config:
        orm_mode = True