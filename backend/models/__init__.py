#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Paquete de modelos para la aplicación Hammernet
Contiene todos los modelos de datos organizados por entidad
"""

from .base import Base
from .usuario import UsuarioDB, Usuario, UsuarioCreate, UsuarioUpdate
from .categoria import CategoriaDB, Categoria, CategoriaCreate, CategoriaUpdate
from .subcategoria import SubCategoriaDB, SubCategoria, SubCategoriaCreate, SubCategoriaUpdate
from .proveedor import ProveedorDB, Proveedor, ProveedorCreate, ProveedorUpdate
from .producto import ProductoDB, Producto, ProductoCreate, ProductoUpdate
from .catalogo import ProductoCatalogo, AgregarACatalogo
from .mensaje import MensajeContactoDB, MensajeContacto, MensajeContactoCreate
from .venta import VentaDB, DetalleVentaDB, MovimientoInventarioDB, Venta, DetalleVenta, MovimientoInventario, VentaCreate, DetalleVentaCreate, MovimientoInventarioCreate
from .pago import PagoDB, Pago, PagoCreate
from .despacho import DespachoDB, Despacho, DespachoCreate, DespachoUpdate
from .auditoria import AuditoriaDB, Auditoria
from .rol import RolDB, Rol
from .permiso import PermisoDB, Permiso
from .rol_permiso import RolPermisoDB

__all__ = [
    "Base",
    "UsuarioDB", "Usuario", "UsuarioCreate", "UsuarioUpdate",
    "CategoriaDB", "Categoria", "CategoriaCreate", "CategoriaUpdate",
    "SubCategoriaDB", "SubCategoria", "SubCategoriaCreate", "SubCategoriaUpdate",
    "ProveedorDB", "Proveedor", "ProveedorCreate", "ProveedorUpdate",
    "ProductoDB", "Producto", "ProductoCreate", "ProductoUpdate",
    "ProductoCatalogo", "AgregarACatalogo",
    "MensajeContactoDB", "MensajeContacto", "MensajeContactoCreate",
    "VentaDB", "DetalleVentaDB", "MovimientoInventarioDB",
    "Venta", "DetalleVenta", "MovimientoInventario",
    "VentaCreate", "DetalleVentaCreate", "MovimientoInventarioCreate",
    "PagoDB", "Pago", "PagoCreate",
    "DespachoDB", "Despacho", "DespachoCreate", "DespachoUpdate",
    "AuditoriaDB", "Auditoria",
    "RolDB", "Rol",
    "PermisoDB", "Permiso",
    "RolPermisoDB",
]
