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
    # Detalles adicionales
    garantia_meses: Optional[int] = None
    modelo: Optional[str] = None
    color: Optional[str] = None
    material: Optional[str] = None
    precio_venta: float
    id_categoria: int
    id_subcategoria: Optional[int] = None
    disponible: bool
    fecha_agregado_catalogo: Optional[datetime] = None
    # Ofertas
    oferta_activa: Optional[bool] = False
    tipo_oferta: Optional[str] = None
    valor_oferta: Optional[float] = 0
    precio_final: Optional[float] = None
    
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
    # Detalles adicionales
    garantia_meses: Optional[int] = None
    modelo: Optional[str] = None
    color: Optional[str] = None
    material: Optional[str] = None
    # Ofertas (opcionales al catalogar)
    oferta_activa: Optional[bool] = False
    tipo_oferta: Optional[str] = None  # 'porcentaje' | 'fijo'
    valor_oferta: Optional[float] = None
    fecha_inicio_oferta: Optional[datetime] = None
    fecha_fin_oferta: Optional[datetime] = None
    
    class Config:
        schema_extra = {
            "example": {
                "descripcion": "Martillo de acero forjado con mango ergonómico",
                "imagen_url": "https://example.com/martillo.jpg",
                "imagen_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD...",
                "marca": "Stanley",
                "caracteristicas": "Peso: 500g, Mango antideslizante, Cabeza forjada",
                "garantia_meses": 12,
                "modelo": "ST-500",
                "color": "Negro",
                "material": "Acero",
                "oferta_activa": True,
                "tipo_oferta": "porcentaje",
                "valor_oferta": 15,
                "fecha_inicio_oferta": "2024-10-01T00:00:00Z",
                "fecha_fin_oferta": "2024-10-31T23:59:59Z"
            }
        }