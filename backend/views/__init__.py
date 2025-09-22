#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Paquete de vistas (rutas) organizadas por módulos
"""

from .auth_routes import router as auth_router
from .usuario_routes import router as usuario_router
from .categoria_routes import router as categoria_router
from .proveedor_routes import router as proveedor_router
from .producto_routes import router as producto_router
from .inventario_routes import router as inventario_router
from .mensaje_routes import router as mensaje_router

__all__ = [
    "auth_router",
    "usuario_router", 
    "categoria_router",
    "proveedor_router",
    "producto_router",
    "inventario_router",
    "mensaje_router"
]