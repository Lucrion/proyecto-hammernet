#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Constantes de configuración compartidas

Se centraliza el prefijo de API para evitar repetir literales en los routers.
Permite sobreescribir vía variables de entorno si fuese necesario.
"""

import os

# Prefijo base para rutas de API
API_PREFIX = os.environ.get("API_PREFIX", "/api")