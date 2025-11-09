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
from .usuario_controller import _rut_a_int


def _to_cents(value: Optional[Union[int, float, str, Decimal]]) -> int:
    """Convierte valores monetarios a enteros (centavos).
    - Acepta int (se asume ya en pesos) -> pesos*100
    - float/Decimal -> redondea a 2 decimales y multiplica por 100
    - str -> intenta parsear decimal seguro
    - None -> 0
    """
    if value is None:
        return 0
    try:
        if isinstance(value, int):
            return value * 100
        if isinstance(value, Decimal):
            return int(round(float(value) * 100))
        if isinstance(value, float):
            return int(round(value * 100))
        # cadenas: pueden venir como "59990" o "59990.50"
        if isinstance(value, str):
            # limpiar separadores comunes
            v = value.strip().replace(",", "")
            return int(round(float(v) * 100))
    except Exception:
        return 0
    return 0


def serialize_usuario(u: UsuarioDB) -> Usuario:
    """Serializa UsuarioDB a Usuario Pydantic, normalizando RUT y fechas."""
    return Usuario(
        id_usuario=u.id_usuario,
        nombre=u.nombre,
        apellido=u.apellido,
        rut=_rut_a_int(u.rut),
        email=u.email,
        telefono=u.telefono,
        role=u.role,
        activo=u.activo,
        fecha_creacion=u.fecha_creacion.isoformat() if getattr(u, "fecha_creacion", None) else None,
    )


def serialize_producto_inventario(p: ProductoDB) -> ProductoInventario:
    """Serializa ProductoDB a ProductoInventario, expresando dinero en centavos (int)."""
    return ProductoInventario(
        id_inventario=p.id_producto,
        id_producto=p.id_producto,
        precio=_to_cents(p.precio_venta),
        cantidad=p.cantidad_disponible if p.cantidad_disponible else 0,
        fecha_registro=p.fecha_creacion.isoformat() if getattr(p, "fecha_creacion", None) else None,
        producto={
            "id_producto": p.id_producto,
            "nombre": p.nombre,
            "descripcion": p.descripcion,
            "codigo_interno": p.codigo_interno,
            "imagen_url": p.imagen_url,
            "id_categoria": p.id_categoria,
            "id_proveedor": p.id_proveedor,
            "marca": p.marca,
            "costo_bruto": _to_cents(p.costo_bruto),
            "costo_neto": _to_cents(p.costo_neto),
            "precio_venta": _to_cents(p.precio_venta),
            "porcentaje_utilidad": float(p.porcentaje_utilidad or 0),
            "utilidad_pesos": _to_cents(p.utilidad_pesos),
            "cantidad_disponible": p.cantidad_disponible if p.cantidad_disponible else 0,
            "stock_minimo": p.stock_minimo if p.stock_minimo else 0,
            "estado": p.estado,
            "categoria": p.categoria.nombre if getattr(p, "categoria", None) else None,
            "proveedor": p.proveedor.nombre if getattr(p, "proveedor", None) else None,
        },
    )