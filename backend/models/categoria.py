#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modelos relacionados con categorías
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional
from .base import Base


class CategoriaDB(Base):
    """Modelo de base de datos para categorías"""
    __tablename__ = "categorias"
    
    id_categoria = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(500), nullable=True)
    
    # Relación con productos
    productos = relationship("ProductoDB", back_populates="categoria")
    # Relación con subcategorías
    subcategorias = relationship("SubCategoriaDB", back_populates="categoria", cascade="all, delete-orphan")


# Modelos Pydantic para validación y serialización

class CategoriaBase(BaseModel):
    """Modelo base para categoría"""
    nombre: str
    descripcion: Optional[str] = None


class CategoriaCreate(CategoriaBase):
    """Modelo para crear categoría"""
    pass


class CategoriaUpdate(BaseModel):
    """Modelo para actualizar categoría"""
    nombre: Optional[str] = None
    descripcion: Optional[str] = None


class Categoria(CategoriaBase):
    """Modelo de respuesta para categoría"""
    id_categoria: int
    
    class Config:
        orm_mode = True