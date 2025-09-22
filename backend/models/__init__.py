#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Paquete de modelos para la aplicación Hammernet
Contiene todos los modelos de datos organizados por entidad
"""

from .base import Base
from .usuario import UsuarioDB, Usuario, UsuarioCreate, UsuarioLogin, Token
from .categoria import CategoriaDB, Categoria, CategoriaCreate, CategoriaUpdate
from .proveedor import ProveedorDB, Proveedor, ProveedorCreate, ProveedorUpdate
from .producto import ProductoDB, Producto, ProductoCreate, ProductoUpdate, ProductoBase, ProductoNuevo, ProductoNuevoCreate, ProductoNuevoUpdate
from .inventario import InventarioDB, Inventario, InventarioCreate, InventarioUpdate
from .mensaje import MensajeContactoDB, MensajeContacto, MensajeContactoCreate

__all__ = [
    # Base
    'Base',
    
    # Usuario
    'UsuarioDB', 'Usuario', 'UsuarioCreate', 'UsuarioLogin', 'Token',
    
    # Categoria
    'CategoriaDB', 'Categoria', 'CategoriaCreate', 'CategoriaUpdate',
    
    # Proveedor
    'ProveedorDB', 'Proveedor', 'ProveedorCreate', 'ProveedorUpdate',
    
    # Producto
    'ProductoDB', 'Producto', 'ProductoCreate', 'ProductoUpdate', 'ProductoBase',
    'ProductoNuevo', 'ProductoNuevoCreate', 'ProductoNuevoUpdate',
    
    # Inventario
    'InventarioDB', 'Inventario', 'InventarioCreate', 'InventarioUpdate',
    
    # Mensaje
    'MensajeContactoDB', 'MensajeContacto', 'MensajeContactoCreate'
]