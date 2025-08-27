#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Punto de entrada ASGI para la aplicación FastAPI.

Este archivo define la interfaz ASGI (Asynchronous Server Gateway Interface) para la aplicación,
lo que permite ejecutarla con servidores ASGI como Uvicorn, Hypercorn o Daphne.

Se utiliza principalmente en entornos de producción donde se requiere una configuración
de servidor más robusta y escalable. También es el punto de entrada utilizado por
plataformas de despliegue como Heroku, Render, o servicios que implementan el estándar ASGI.

La aplicación se importa directamente desde el módulo main.
"""

# Importar la aplicación FastAPI desde el módulo principal
from main import app

# Permitir la ejecución directa para desarrollo
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)