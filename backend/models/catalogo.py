#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modelos relacionados con el catálogo público de productos
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProductoCatalogo(BaseModel):
    """Modelo para productos en el catálogo público"""
    id_producto: int
    nombre: str
    descripcion: str
    imagen_url: str
    marca: str
    caracteristicas: str
    precio_venta: float
    categoria: str
    disponible: bool
    fecha_agregado_catalogo: Optional[datetime] = None
    
    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class AgregarACatalogo(BaseModel):
    """Modelo para agregar un producto del inventario al catálogo"""
    descripcion: str
    imagen_url: Optional[str] = None
    imagen_base64: Optional[str] = None
    marca: str
    caracteristicas: str
    
    class Config:
        schema_extra = {
            "example": {
                "descripcion": "Martillo de acero forjado con mango ergonómico",
                "imagen_url": "https://example.com/martillo.jpg",
                "imagen_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD...",
                "marca": "Stanley",
                "caracteristicas": "Peso: 500g, Mango antideslizante, Cabeza forjada"
            }
        }