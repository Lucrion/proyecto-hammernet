#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modelos relacionados con subcategorías
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional
from .base import Base


class SubCategoriaDB(Base):
    """Modelo de base de datos para subcategorías"""
    __tablename__ = "subcategorias"

    id_subcategoria = Column(Integer, primary_key=True, index=True)
    id_categoria = Column(Integer, ForeignKey("categorias.id_categoria"), nullable=False)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(500), nullable=True)

    # Relaciones
    categoria = relationship("CategoriaDB", back_populates="subcategorias")
    # Relación inversa con productos
    productos = relationship("ProductoDB", back_populates="subcategoria")


# Modelos Pydantic

class SubCategoriaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    id_categoria: int


class SubCategoriaCreate(SubCategoriaBase):
    pass


class SubCategoriaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    id_categoria: Optional[int] = None


class SubCategoria(SubCategoriaBase):
    id_subcategoria: int

    class Config:
        orm_mode = True