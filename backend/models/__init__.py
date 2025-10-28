#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Paquete de modelos para la aplicación Hammernet
Contiene todos los modelos de datos organizados por entidad
"""

from .base import Base
from .usuario import UsuarioDB, Usuario, UsuarioCreate, UsuarioUpdate
from .categoria import CategoriaDB, Categoria, CategoriaCreate, CategoriaUpdate
from .proveedor import ProveedorDB, Proveedor, ProveedorCreate, ProveedorUpdate
from .producto import ProductoDB, Producto, ProductoCreate, ProductoUpdate
from .catalogo import ProductoCatalogo, AgregarACatalogo
from .mensaje import MensajeContactoDB, MensajeContacto, MensajeContactoCreate
from .venta import VentaDB, DetalleVentaDB, MovimientoInventarioDB, Venta, DetalleVenta, MovimientoInventario, VentaCreate, DetalleVentaCreate, MovimientoInventarioCreate
from .despacho import DespachoDB, Despacho, DespachoCreate, DespachoUpdate

__all__ = [
    "Base",
    "UsuarioDB", "Usuario", "UsuarioCreate", "UsuarioUpdate",
    "CategoriaDB", "Categoria", "CategoriaCreate", "CategoriaUpdate",
    "ProveedorDB", "Proveedor", "ProveedorCreate", "ProveedorUpdate",
    "ProductoDB", "Producto", "ProductoCreate", "ProductoUpdate",
    "ProductoCatalogo", "AgregarACatalogo",
    "MensajeContactoDB", "MensajeContacto", "MensajeContactoCreate",
    "VentaDB", "DetalleVentaDB", "MovimientoInventarioDB",
    "Venta", "DetalleVenta", "MovimientoInventario",
    "VentaCreate", "DetalleVentaCreate", "MovimientoInventarioCreate",
    "DespachoDB", "Despacho", "DespachoCreate", "DespachoUpdate"
]