#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from typing import List, Optional
from sqlalchemy.orm import Session
import uvicorn
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Importar módulos personalizados
from database import get_db, Base, engine
from models import (Producto, ProductoCreate, ProductoBase, Usuario, UsuarioCreate, 
    UsuarioLogin, Token, ProductoDB, UsuarioDB, MensajeContacto, MensajeContactoCreate, 
    MensajeContactoDB)
from auth import hash_contraseña, verificar_contraseña, crear_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
from cloudinary_config import configure_cloudinary, upload_image

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

# Crear tablas en la base de datos
try:
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas correctamente en la base de datos")
except Exception as e:
    print(f"Error al crear tablas: {e}")

# Configurar CORS
origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:4321,http://localhost:8000")
origins = origins_str.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Requested-With", "Access-Control-Allow-Origin"],
    expose_headers=["Authorization"],
    max_age=3600
)

@app.get("/health", tags=["Sistema"])
async def health_check():
    return {"status": "ok"}

@app.get("/productos", response_model=List[Producto], tags=["Productos"])
async def get_productos(db: Session = Depends(get_db)):
    try:
        productos_db = db.query(ProductoDB).all()
        productos = [
            {
                "id": p.id,
                "nombre": p.nombre,
                "descripcion": p.descripcion,
                "caracteristicas": p.caracteristicas,
                "precio": p.precio,
                "stock": p.stock,
                "categoria": p.categoria,
                "imagen": p.imagen,
                "fecha_creacion": p.fecha_creacion.isoformat() if p.fecha_creacion else datetime.now().isoformat()
            } for p in productos_db
        ]
        return productos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/productos/{producto_id}", response_model=Producto, tags=["Productos"])
async def get_producto(producto_id: int, db: Session = Depends(get_db)):
    try:
        producto_db = db.query(ProductoDB).filter(ProductoDB.id == producto_id).first()
        if not producto_db:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
            
        return {
            "id": producto_db.id,
            "nombre": producto_db.nombre,
            "descripcion": producto_db.descripcion,
            "caracteristicas": producto_db.caracteristicas,
            "precio": producto_db.precio,
            "stock": producto_db.stock,
            "categoria": producto_db.categoria,
            "imagen": producto_db.imagen,
            "fecha_creacion": producto_db.fecha_creacion.isoformat() if producto_db.fecha_creacion else datetime.now().isoformat()
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/productos", response_model=Producto, tags=["Productos"])
async def create_producto(
    nombre: str = Form(...),
    descripcion: str = Form(...),
    caracteristicas: str = Form(...),
    precio: float = Form(...),
    stock: int = Form(...),
    categoria: str = Form(...),
    imagen: UploadFile = File(default=None),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Verificar que el usuario actual es administrador
        if current_user.role != "administrador":
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos para crear productos"
            )
            
        # Procesar imagen si se proporciona
        imagen_url = None
        if imagen and hasattr(imagen, 'file') and imagen.filename:
            print(f"Subiendo imagen para nuevo producto: {nombre}")
            # Subir imagen a Cloudinary
            imagen_url = await upload_image(imagen)
            print(f"URL de imagen obtenida: {imagen_url}")
            if not imagen_url:
                raise HTTPException(status_code=500, detail="Error al subir la imagen a Cloudinary")
        else:
            print(f"No se proporcionó imagen para el nuevo producto: {nombre}")
            
        # Crear nuevo producto
        nuevo_producto = ProductoDB(
            nombre=nombre,
            descripcion=descripcion,
            caracteristicas=caracteristicas,
            precio=precio,
            stock=stock,
            categoria=categoria,
            imagen=imagen_url,  # Asegurarse de que imagen_url no sea None
            fecha_creacion=datetime.now()
        )
        
        # Verificar que la imagen se ha guardado correctamente
        print(f"Guardando producto con imagen_url: {imagen_url}")
        if imagen_url is None:
            print("ADVERTENCIA: Se está guardando un producto sin imagen")
        
        db.add(nuevo_producto)
        db.commit()
        db.refresh(nuevo_producto)
        
        return {
            "id": nuevo_producto.id,
            "nombre": nuevo_producto.nombre,
            "descripcion": nuevo_producto.descripcion,
            "caracteristicas": nuevo_producto.caracteristicas,
            "precio": nuevo_producto.precio,
            "stock": nuevo_producto.stock,
            "categoria": nuevo_producto.categoria,
            "imagen": nuevo_producto.imagen,
            "fecha_creacion": nuevo_producto.fecha_creacion.isoformat()
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/productos/{producto_id}", response_model=Producto, tags=["Productos"])
async def update_producto(
    producto_id: int,
    nombre: str = Form(...),
    descripcion: str = Form(...),
    caracteristicas: str = Form(...),
    precio: float = Form(...),
    stock: int = Form(...),
    categoria: str = Form(...),
    imagen: UploadFile = File(default=None),
    imagen_actual: str = Form(default=None),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Verificar que el usuario actual es administrador
        if current_user.role != "administrador":
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos para actualizar productos"
            )
            
        # Buscar el producto a actualizar
        producto_db = db.query(ProductoDB).filter(ProductoDB.id == producto_id).first()
        if not producto_db:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
            
        # Procesar imagen
        imagen_url = None
        
        # Caso 1: Se proporciona una nueva imagen
        if imagen and hasattr(imagen, 'file') and imagen.filename:
            print(f"Subiendo nueva imagen para producto {producto_id}")
            # Subir nueva imagen a Cloudinary
            imagen_url = await upload_image(imagen)
            if not imagen_url:
                raise HTTPException(status_code=500, detail="Error al subir la imagen a Cloudinary")
        # Caso 2: Se mantiene la imagen actual
        elif imagen_actual:
            print(f"Manteniendo imagen actual para producto {producto_id}: {imagen_actual}")
            imagen_url = imagen_actual
        # Caso 3: No hay imagen nueva ni actual
        else:
            print(f"No se proporcionó imagen para producto {producto_id}")
            imagen_url = None
            
        # Actualizar campos
        producto_db.nombre = nombre
        producto_db.descripcion = descripcion
        producto_db.caracteristicas = caracteristicas
        producto_db.precio = precio
        producto_db.stock = stock
        producto_db.categoria = categoria
        producto_db.imagen = imagen_url
            
        db.commit()
        db.refresh(producto_db)
        
        return {
            "id": producto_db.id,
            "nombre": producto_db.nombre,
            "descripcion": producto_db.descripcion,
            "caracteristicas": producto_db.caracteristicas,
            "precio": producto_db.precio,
            "stock": producto_db.stock,
            "categoria": producto_db.categoria,
            "imagen": producto_db.imagen,
            "fecha_creacion": producto_db.fecha_creacion.isoformat() if producto_db.fecha_creacion else datetime.now().isoformat()
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/productos/{producto_id}", response_model=dict, tags=["Productos"])
async def delete_producto(producto_id: int, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        # Verificar que el usuario actual es administrador
        if current_user.role != "administrador":
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos para eliminar productos"
            )
            
        # Buscar el producto a eliminar
        producto_db = db.query(ProductoDB).filter(ProductoDB.id == producto_id).first()
        if not producto_db:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
            
        # Eliminar el producto
        db.delete(producto_db)
        db.commit()
        
        return {"message": "Producto eliminado correctamente"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login", response_model=Token, tags=["Autenticación"])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        # Buscar usuario
        usuario = db.query(UsuarioDB).filter(UsuarioDB.username == form_data.username).first()
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas"
            )
        
        # Verificar contraseña
        if not verificar_contraseña(form_data.password, usuario.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas"
            )
        
        # Crear token de acceso
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = crear_token(
            data={"sub": usuario.username},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "id": usuario.id,
            "nombre": usuario.nombre,
            "username": usuario.username,
            "role": usuario.role
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/usuarios", response_model=List[Usuario], tags=["Usuarios"])
async def get_usuarios(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        # Verificar que el usuario actual es administrador
        if current_user.role != "administrador":
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos para ver la lista de usuarios"
            )
            
        usuarios_db = db.query(UsuarioDB).all()
        usuarios = [
            {
                "id": u.id,
                "nombre": u.nombre,
                "username": u.username,
                "role": u.role,
                "fecha_creacion": u.fecha_creacion.isoformat() if u.fecha_creacion else datetime.now().isoformat()
            } for u in usuarios_db
        ]
        return usuarios
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/usuarios/{usuario_id}", response_model=Usuario, tags=["Usuarios"])
async def get_usuario(usuario_id: int, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        # Verificar que el usuario actual es administrador
        if current_user.role != "administrador":
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos para ver los detalles de usuarios"
            )
            
        usuario_db = db.query(UsuarioDB).filter(UsuarioDB.id == usuario_id).first()
        if not usuario_db:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
        return {
            "id": usuario_db.id,
            "nombre": usuario_db.nombre,
            "username": usuario_db.username,
            "role": usuario_db.role,
            "fecha_creacion": usuario_db.fecha_creacion.isoformat() if usuario_db.fecha_creacion else datetime.now().isoformat()
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/usuarios", response_model=Usuario, tags=["Usuarios"])
async def create_usuario(usuario: UsuarioCreate, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        # Verificar que el usuario actual es administrador
        if current_user.role != "administrador":
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos para crear usuarios"
            )
            
        # Verificar si el nombre de usuario ya existe
        existing_user = db.query(UsuarioDB).filter(UsuarioDB.username == usuario.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="El nombre de usuario ya está en uso")
            
        # Crear nuevo usuario
        hashed_password = hash_contraseña(usuario.password)
        nuevo_usuario = UsuarioDB(
            nombre=usuario.nombre,
            username=usuario.username,
            password=hashed_password,
            role=usuario.role,
            fecha_creacion=datetime.now()
        )
        
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        
        return {
            "id": nuevo_usuario.id,
            "nombre": nuevo_usuario.nombre,
            "username": nuevo_usuario.username,
            "role": nuevo_usuario.role,
            "fecha_creacion": nuevo_usuario.fecha_creacion.isoformat()
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/usuarios/{usuario_id}", response_model=Usuario, tags=["Usuarios"])
async def update_usuario(usuario_id: int, usuario_update: dict, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        # Verificar que el usuario actual es administrador
        if current_user.role != "administrador":
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos para actualizar usuarios"
            )
            
        # Buscar el usuario a actualizar
        usuario_db = db.query(UsuarioDB).filter(UsuarioDB.id == usuario_id).first()
        if not usuario_db:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
        # Actualizar campos
        if "nombre" in usuario_update:
            usuario_db.nombre = usuario_update["nombre"]
        if "username" in usuario_update:
            # Verificar si el nuevo nombre de usuario ya existe
            if usuario_update["username"] != usuario_db.username:
                existing_user = db.query(UsuarioDB).filter(UsuarioDB.username == usuario_update["username"]).first()
                if existing_user:
                    raise HTTPException(status_code=400, detail="El nombre de usuario ya está en uso")
            usuario_db.username = usuario_update["username"]
        if "password" in usuario_update and usuario_update["password"]:
            usuario_db.password = hash_contraseña(usuario_update["password"])
        if "role" in usuario_update:
            usuario_db.role = usuario_update["role"]
            
        db.commit()
        db.refresh(usuario_db)
        
        return {
            "id": usuario_db.id,
            "nombre": usuario_db.nombre,
            "username": usuario_db.username,
            "role": usuario_db.role,
            "fecha_creacion": usuario_db.fecha_creacion.isoformat() if usuario_db.fecha_creacion else datetime.now().isoformat()
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/usuarios/{usuario_id}", response_model=dict, tags=["Usuarios"])
async def delete_usuario(usuario_id: int, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        # Verificar que el usuario actual es administrador
        if current_user.role != "administrador":
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos para eliminar usuarios"
            )
            
        # Buscar el usuario a eliminar
        usuario_db = db.query(UsuarioDB).filter(UsuarioDB.id == usuario_id).first()
        if not usuario_db:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
        # No permitir eliminar al propio usuario
        if usuario_db.username == current_user.username:
            raise HTTPException(status_code=400, detail="No puedes eliminar tu propio usuario")
            
        # Eliminar el usuario
        db.delete(usuario_db)
        db.commit()
        
        return {"message": "Usuario eliminado correctamente"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mensajes", response_model=MensajeContacto, tags=["Mensajes"])
async def create_mensaje(mensaje: MensajeContactoCreate, db: Session = Depends(get_db)):
    try:
        nuevo_mensaje = MensajeContactoDB(
            nombre=mensaje.nombre,
            apellido=mensaje.apellido,
            email=mensaje.email,
            asunto=mensaje.asunto,
            mensaje=mensaje.mensaje,
            fecha_envio=datetime.now(),
            leido=False
        )
        
        db.add(nuevo_mensaje)
        db.commit()
        db.refresh(nuevo_mensaje)
        
        return {
            "id": nuevo_mensaje.id,
            "nombre": nuevo_mensaje.nombre,
            "apellido": nuevo_mensaje.apellido,
            "email": nuevo_mensaje.email,
            "asunto": nuevo_mensaje.asunto,
            "mensaje": nuevo_mensaje.mensaje,
            "fecha_envio": nuevo_mensaje.fecha_envio.isoformat(),
            "leido": nuevo_mensaje.leido
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/mensajes", response_model=List[MensajeContacto], tags=["Mensajes"])
async def get_mensajes(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    # Verificar que el usuario actual es administrador
    if current_user.role != "administrador":
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para ver los mensajes"
        )
        
    mensajes_db = db.query(MensajeContactoDB).order_by(MensajeContactoDB.fecha_envio.desc()).all()
    mensajes = [
        {
            "id": m.id,
            "nombre": m.nombre,
            "apellido": m.apellido,
            "email": m.email,
            "asunto": m.asunto,
            "mensaje": m.mensaje,
            "fecha_envio": m.fecha_envio.isoformat(),
            "leido": m.leido
        } for m in mensajes_db
    ]
        
    return mensajes

@app.put("/mensajes/{mensaje_id}/leer", response_model=MensajeContacto, tags=["Mensajes"])
async def mark_mensaje_as_read(mensaje_id: int, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        # Verificar que el usuario actual es administrador
        if current_user.role != "administrador":
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos para marcar mensajes como leídos"
            )
            
        mensaje_db = db.query(MensajeContactoDB).filter(MensajeContactoDB.id == mensaje_id).first()
        if not mensaje_db:
            raise HTTPException(status_code=404, detail="Mensaje no encontrado")
        
        mensaje_db.leido = True
        db.commit()
        db.refresh(mensaje_db)
        
        return {
            "id": mensaje_db.id,
            "nombre": mensaje_db.nombre,
            "apellido": mensaje_db.apellido,
            "email": mensaje_db.email,
            "asunto": mensaje_db.asunto,
            "mensaje": mensaje_db.mensaje,
            "fecha_envio": mensaje_db.fecha_envio.isoformat(),
            "leido": mensaje_db.leido
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/mensajes/{mensaje_id}", response_model=dict, tags=["Mensajes"])
async def delete_mensaje(mensaje_id: int, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        # Verificar que el usuario actual es administrador
        if current_user.role != "administrador":
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos para eliminar mensajes"
            )
            
        mensaje_db = db.query(MensajeContactoDB).filter(MensajeContactoDB.id == mensaje_id).first()
        if not mensaje_db:
            raise HTTPException(status_code=404, detail="Mensaje no encontrado")
        
        db.delete(mensaje_db)
        db.commit()
        
        return {"message": "Mensaje eliminado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)