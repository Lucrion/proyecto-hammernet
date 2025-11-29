#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Serializadores reutilizables para modelos de BD a DTOs Pydantic o dicts
"""

from typing import Optional, Union
from decimal import Decimal
from models.usuario import Usuario
from models.producto import ProductoInventario
from models.usuario import UsuarioDB
from models.producto import ProductoDB
from .usuario_controller import _rut_normalizado


def _to_pesos_int(value: Optional[Union[int, float, str, Decimal]]) -> int:
    """Convierte valores monetarios a pesos chilenos enteros (sin centavos).
    - int -> se usa tal cual (ya en pesos)
    - float/Decimal -> se redondea al entero más cercano
    - str -> parsea y redondea
    - None -> 0
    """
    if value is None:
        return 0
    try:
        if isinstance(value, int):
            return value
        if isinstance(value, Decimal):
            return int(round(float(value)))
        if isinstance(value, float):
            return int(round(value))
        if isinstance(value, str):
            v = value.strip().replace(",", "")
            return int(round(float(v)))
    except Exception:
        return 0
    return 0


def serialize_usuario(u: UsuarioDB) -> Usuario:
    """Serializa UsuarioDB a Usuario Pydantic, normalizando RUT y fechas."""
    return Usuario(
        rut=str(u.rut) if u.rut is not None else None,
        nombre=u.nombre,
        apellido=u.apellido,
        email=u.email,
        telefono=u.telefono,
        role=u.role,
        activo=u.activo,
        fecha_creacion=u.fecha_creacion.isoformat() if getattr(u, "fecha_creacion", None) else None,
    )


def serialize_producto_inventario(p: ProductoDB) -> ProductoInventario:
    """Serializa ProductoDB a ProductoInventario en pesos chilenos (enteros)."""
    return ProductoInventario(
        id_inventario=p.id_producto,
        id_producto=p.id_producto,
        precio=_to_pesos_int(p.precio_venta),
        cantidad=p.cantidad_disponible if p.cantidad_disponible else 0,
        fecha_registro=p.fecha_creacion.isoformat() if getattr(p, "fecha_creacion", None) else None,
        producto={
            "id_producto": p.id_producto,
            "nombre": p.nombre,
            "descripcion": p.descripcion,
            "codigo_interno": p.codigo_interno,
            "imagen_url": p.imagen_url,
            "id_categoria": p.id_categoria,
            "id_subcategoria": getattr(p, "id_subcategoria"),
            "id_proveedor": p.id_proveedor,
            "marca": p.marca,
            "costo_bruto": _to_pesos_int(p.costo_bruto),
            "costo_neto": _to_pesos_int(p.costo_neto),
            "precio_venta": _to_pesos_int(p.precio_venta),
            "porcentaje_utilidad": float(p.porcentaje_utilidad or 0),
            "utilidad_pesos": _to_pesos_int(p.utilidad_pesos),
            "cantidad_disponible": p.cantidad_disponible if p.cantidad_disponible else 0,
            "stock_minimo": p.stock_minimo if p.stock_minimo else 0,
            "estado": p.estado,
            "categoria": p.categoria.nombre if getattr(p, "categoria", None) else None,
            "subcategoria": p.subcategoria.nombre if getattr(p, "subcategoria", None) else None,
            "proveedor": p.proveedor.nombre if getattr(p, "proveedor", None) else None,
        },
    )
