#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Paquete de vistas (rutas) organizadas por módulos
"""

from .auth_routes import router as auth_router
from .usuario_routes import router as usuario_router
from .categoria_routes import router as categoria_router
from .subcategoria_routes import router as subcategoria_router
from .proveedor_routes import router as proveedor_router
from .producto_routes import router as producto_router
from .mensaje_routes import router as mensaje_router
from .despacho_routes import router as despacho_router
from .venta_routes import router as venta_router
from .auditoria_routes import router as auditoria_router
from .pago_routes import router as pago_router

__all__ = [
    "auth_router",
    "usuario_router", 
    "categoria_router",
    "subcategoria_router",
    "proveedor_router",
    "producto_router",
    "mensaje_router",
    "despacho_router",
    "venta_router",
    "auditoria_router",
    "pago_router"
]