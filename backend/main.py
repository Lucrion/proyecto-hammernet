#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
import uvicorn
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Importar módulos personalizados
from config.database import Base, engine
from config.cloudinary_config import configure_cloudinary
# Registrar todos los modelos antes de crear tablas para evitar errores de mapeo en producción
from models import *  # noqa: F401,F403

# Importar las rutas organizadas
from views.auth_routes import router as auth_router
from views.usuario_routes import router as usuario_router
from views.categoria_routes import router as categoria_router
from views.subcategoria_routes import router as subcategoria_router
from views.proveedor_routes import router as proveedor_router
from views.producto_routes import router as producto_router
from views.mensaje_routes import router as mensaje_router
from views.venta_routes import router as venta_router
from views.despacho_routes import router as despacho_router
from views.auditoria_routes import router as auditoria_router
from views.dashboard_routes import router as dashboard_router
from views.pago_routes import router as pago_router
from views.analytics_routes import router as analytics_router

# Verificar que las variables de entorno de Cloudinary estén configuradas
cloudinary_vars = {
    "CLOUDINARY_CLOUD_NAME": os.environ.get("CLOUDINARY_CLOUD_NAME"),
    "CLOUDINARY_API_KEY": os.environ.get("CLOUDINARY_API_KEY"),
    "CLOUDINARY_API_SECRET": os.environ.get("CLOUDINARY_API_SECRET")
}

for var_name, var_value in cloudinary_vars.items():
    if not var_value:
        print(f"ADVERTENCIA: La variable de entorno {var_name} no está configurada")

# Configurar Cloudinary para almacenamiento de imágenes
configure_cloudinary()

# Inicializar la aplicación FastAPI con metadatos
app = FastAPI(
    title="API de Hammernet",
    description="API para la gestión de productos y usuarios de Hammernet",
    version="1.0.0",
    root_path=os.environ.get("ROOT_PATH", "")
)

app.add_middleware(GZipMiddleware, minimum_size=500)

# Crear las tablas en la base de datos (solo si no existen)
try:
    Base.metadata.create_all(bind=engine)
    # Ajuste de compatibilidad de esquema: asegurar columna id_rol en usuarios
    from sqlalchemy import text
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS id_rol INTEGER"))
        except Exception as ie:
            print(f"⚠️  No se pudo asegurar columna id_rol en usuarios: {ie}")
    print("🔄 Servidor iniciado - Base de datos verificada")
except Exception as e:
    print(f"❌ Error al inicializar base de datos: {e}")

# Configurar CORS
origins_str = os.getenv("ALLOWED_ORIGINS", "https://ferreteria-patricio.onrender.com,https://hammernet.onrender.com")
origins = [origin.strip() for origin in origins_str.split(",")]

# Agregar localhost para desarrollo si no está en producción
if os.getenv("ENVIRONMENT") != "production":
    origins.extend([
        "http://localhost:4321",
        "http://localhost:4322",
        "http://localhost:8000",
        "http://127.0.0.1:4321",
        "http://127.0.0.1:4322",
        "http://127.0.0.1:8000"
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Requested-With", "Access-Control-Allow-Origin"],
    expose_headers=["Authorization"],
    max_age=3600
)

@app.middleware("http")
async def cache_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    try:
        path = request.url.path or ""
        method = request.method.upper()
        if method == "GET":
            if path.startswith("/api/productos"):
                response.headers["Cache-Control"] = "public, max-age=60"
            elif path.startswith("/api/dashboard"):
                response.headers["Cache-Control"] = "public, max-age=30"
            elif path.startswith("/api/ventas"):
                response.headers["Cache-Control"] = "no-cache"
        return response
    except Exception:
        return response

# Endpoint de salud del sistema
@app.get("/health", tags=["Sistema"])
@app.get("/api/health", tags=["Sistema"])
async def health_check():
    """
    Endpoint para verificar el estado de la API
    
    Returns:
        dict: Estado de la API y mensaje
    """
    return {
        "status": "ok",
        "message": "API de Hammernet funcionando correctamente",
        "version": "1.0.0"
    }

# Incluir las rutas en la aplicación
app.include_router(auth_router)
app.include_router(usuario_router)
app.include_router(categoria_router)
app.include_router(subcategoria_router)
app.include_router(proveedor_router)
app.include_router(producto_router)
app.include_router(mensaje_router)
app.include_router(venta_router)
app.include_router(pago_router)
app.include_router(analytics_router)
app.include_router(despacho_router)
app.include_router(auditoria_router)
app.include_router(dashboard_router)

if __name__ == "__main__":
    # Obtener configuración del servidor desde variables de entorno
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("main:app", host=host, port=port, reload=True)
