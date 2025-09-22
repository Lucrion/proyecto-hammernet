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
from models import (Producto, ProductoCreate, ProductoUpdate, ProductoBase, Usuario, UsuarioCreate, 
    UsuarioLogin, Token, UsuarioDB, MensajeContacto, MensajeContactoCreate, 
    MensajeContactoDB,
    Categoria, CategoriaCreate, CategoriaUpdate, CategoriaDB,
    Proveedor, ProveedorCreate, ProveedorUpdate, ProveedorDB,
    ProductoNuevo, ProductoNuevoCreate, ProductoNuevoUpdate, ProductoDB,
    Inventario, InventarioCreate, InventarioUpdate, InventarioDB)
from auth import hash_contraseña, verificar_contraseña, crear_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user, verificar_permisos_admin, es_administrador
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

# Endpoints de productos implementados con nuevo esquema normalizado









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
        # Verificar permisos de administrador
        verificar_permisos_admin(current_user, "ver la lista de usuarios")
            
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
        # Verificar permisos de administrador
        verificar_permisos_admin(current_user, "ver los detalles de usuarios")
            
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
        # Verificar permisos de administrador
        verificar_permisos_admin(current_user, "crear usuarios")
            
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
        # Verificar permisos de administrador
        verificar_permisos_admin(current_user, "actualizar usuarios")
            
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
        # Verificar permisos de administrador
        verificar_permisos_admin(current_user, "eliminar usuarios")
            
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
    # Verificar permisos de administrador
    verificar_permisos_admin(current_user, "ver los mensajes")
        
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
        # Verificar permisos de administrador
        verificar_permisos_admin(current_user, "marcar mensajes como leídos")
            
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
        # Verificar permisos de administrador
        verificar_permisos_admin(current_user, "eliminar mensajes")
            
        mensaje_db = db.query(MensajeContactoDB).filter(MensajeContactoDB.id == mensaje_id).first()
        if not mensaje_db:
            raise HTTPException(status_code=404, detail="Mensaje no encontrado")
        
        db.delete(mensaje_db)
        db.commit()
        
        return {"message": "Mensaje eliminado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoints de productos, categorías e inventario implementados con nuevo esquema normalizado






# ==================== ENDPOINTS CRUD PARA CATEGORÍAS ====================

@app.get("/categorias", response_model=List[Categoria])
def obtener_categorias(db: Session = Depends(get_db)):
    """Obtener todas las categorías"""
    categorias = db.query(CategoriaDB).all()
    return categorias

@app.get("/categorias/{categoria_id}", response_model=Categoria)
def obtener_categoria(categoria_id: int, db: Session = Depends(get_db)):
    """Obtener una categoría por ID"""
    categoria = db.query(CategoriaDB).filter(CategoriaDB.id_categoria == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return categoria

@app.post("/categorias", response_model=Categoria)
def crear_categoria(
    categoria: CategoriaCreate,
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(get_current_user)
):
    """Crear una nueva categoría"""
    if current_user.role not in ["administrador"]:
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para crear categorías"
        )
    
    # Verificar si ya existe una categoría con el mismo nombre
    categoria_existente = db.query(CategoriaDB).filter(CategoriaDB.nombre == categoria.nombre).first()
    if categoria_existente:
        raise HTTPException(status_code=400, detail="Ya existe una categoría con ese nombre")
    
    nueva_categoria = CategoriaDB(**categoria.dict())
    db.add(nueva_categoria)
    db.commit()
    db.refresh(nueva_categoria)
    return nueva_categoria

@app.put("/categorias/{categoria_id}", response_model=Categoria)
def actualizar_categoria(
    categoria_id: int,
    categoria_update: CategoriaUpdate,
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(get_current_user)
):
    """Actualizar una categoría existente"""
    if current_user.role not in ["administrador"]:
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para actualizar categorías"
        )
    
    categoria = db.query(CategoriaDB).filter(CategoriaDB.id_categoria == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    # Verificar si el nuevo nombre ya existe (si se está cambiando)
    if categoria_update.nombre and categoria_update.nombre != categoria.nombre:
        categoria_existente = db.query(CategoriaDB).filter(CategoriaDB.nombre == categoria_update.nombre).first()
        if categoria_existente:
            raise HTTPException(status_code=400, detail="Ya existe una categoría con ese nombre")
    
    # Actualizar campos
    for field, value in categoria_update.dict(exclude_unset=True).items():
        setattr(categoria, field, value)
    
    db.commit()
    db.refresh(categoria)
    return categoria

@app.delete("/categorias/{categoria_id}")
def eliminar_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(get_current_user)
):
    """Eliminar una categoría"""
    if current_user.role not in ["administrador"]:
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para eliminar categorías"
        )
    
    categoria = db.query(CategoriaDB).filter(CategoriaDB.id_categoria == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    # Verificar si hay productos asociados a esta categoría
    productos_asociados = db.query(ProductoDB).filter(ProductoDB.id_categoria == categoria_id).count()
    if productos_asociados > 0:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede eliminar la categoría porque tiene {productos_asociados} productos asociados"
        )
    
    db.delete(categoria)
    db.commit()
    return {"message": "Categoría eliminada correctamente"}

# ==================== ENDPOINTS CRUD PARA PROVEEDORES ====================

@app.get("/proveedores", response_model=List[Proveedor])
def obtener_proveedores(db: Session = Depends(get_db)):
    """Obtener todos los proveedores"""
    proveedores = db.query(ProveedorDB).all()
    return proveedores

@app.get("/proveedores/{proveedor_id}", response_model=Proveedor)
def obtener_proveedor(proveedor_id: int, db: Session = Depends(get_db)):
    """Obtener un proveedor por ID"""
    proveedor = db.query(ProveedorDB).filter(ProveedorDB.id_proveedor == proveedor_id).first()
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return proveedor

@app.post("/proveedores", response_model=Proveedor)
def crear_proveedor(
    proveedor: ProveedorCreate,
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(get_current_user)
):
    """Crear un nuevo proveedor"""
    if current_user.role not in ["administrador", "bodeguero"]:
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para crear proveedores"
        )
    
    # Verificar si ya existe un proveedor con el mismo nombre
    proveedor_existente = db.query(ProveedorDB).filter(ProveedorDB.nombre == proveedor.nombre).first()
    if proveedor_existente:
        raise HTTPException(status_code=400, detail="Ya existe un proveedor con ese nombre")
    
    nuevo_proveedor = ProveedorDB(**proveedor.dict())
    db.add(nuevo_proveedor)
    db.commit()
    db.refresh(nuevo_proveedor)
    return nuevo_proveedor

@app.put("/proveedores/{proveedor_id}", response_model=Proveedor)
def actualizar_proveedor(
    proveedor_id: int,
    proveedor_update: ProveedorUpdate,
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(get_current_user)
):
    """Actualizar un proveedor existente"""
    if current_user.role not in ["administrador", "bodeguero"]:
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para actualizar proveedores"
        )
    
    proveedor = db.query(ProveedorDB).filter(ProveedorDB.id_proveedor == proveedor_id).first()
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    # Verificar si el nuevo nombre ya existe (si se está cambiando)
    if proveedor_update.nombre and proveedor_update.nombre != proveedor.nombre:
        proveedor_existente = db.query(ProveedorDB).filter(ProveedorDB.nombre == proveedor_update.nombre).first()
        if proveedor_existente:
            raise HTTPException(status_code=400, detail="Ya existe un proveedor con ese nombre")
    
    # Actualizar campos
    for field, value in proveedor_update.dict(exclude_unset=True).items():
        setattr(proveedor, field, value)
    
    db.commit()
    db.refresh(proveedor)
    return proveedor

@app.delete("/proveedores/{proveedor_id}")
def eliminar_proveedor(
    proveedor_id: int,
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(get_current_user)
):
    """Eliminar un proveedor"""
    if current_user.role not in ["administrador"]:
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para eliminar proveedores"
        )
    
    proveedor = db.query(ProveedorDB).filter(ProveedorDB.id_proveedor == proveedor_id).first()
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    # Verificar si hay productos asociados a este proveedor
    productos_asociados = db.query(ProductoDB).filter(ProductoDB.id_proveedor == proveedor_id).count()
    if productos_asociados > 0:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede eliminar el proveedor porque tiene {productos_asociados} productos asociados"
        )
    
    db.delete(proveedor)
    db.commit()
    return {"message": "Proveedor eliminado correctamente"}

# ==================== ENDPOINTS CRUD PARA PRODUCTOS (NUEVO ESQUEMA) ====================

@app.get("/productos", response_model=List[Producto])
def obtener_productos(
    skip: int = 0,
    limit: int = 100,
    categoria_id: Optional[int] = None,
    proveedor_id: Optional[int] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener todos los productos con filtros opcionales"""
    query = db.query(ProductoDB)
    
    if categoria_id:
        query = query.filter(ProductoDB.id_categoria == categoria_id)
    if proveedor_id:
        query = query.filter(ProductoDB.id_proveedor == proveedor_id)
    
    productos_db = query.offset(skip).limit(limit).all()
    
    # Convertir los productos de la base de datos al modelo Pydantic para la respuesta
    productos = []
    for producto in productos_db:
        # Obtener la categoría si existe
        categoria = None
        if producto.id_categoria:
            categoria_db = db.query(CategoriaDB).filter(CategoriaDB.id_categoria == producto.id_categoria).first()
            if categoria_db:
                categoria = {
                    "id_categoria": categoria_db.id_categoria,
                    "nombre": categoria_db.nombre,
                    "descripcion": categoria_db.descripcion
                }
        
        # Obtener el proveedor si existe
        proveedor = None
        if producto.id_proveedor:
            proveedor_db = db.query(ProveedorDB).filter(ProveedorDB.id_proveedor == producto.id_proveedor).first()
            if proveedor_db:
                proveedor = {
                    "id_proveedor": proveedor_db.id_proveedor,
                    "nombre": proveedor_db.nombre,
                    "rut": proveedor_db.rut,
                    "razon_social": proveedor_db.razon_social,
                    "sucursal": proveedor_db.sucursal,
                    "direccion": proveedor_db.direccion,
                    "ciudad": proveedor_db.ciudad,
                    "celular": proveedor_db.celular,
                    "correo": proveedor_db.correo,
                    "contacto": proveedor_db.contacto,
                    "telefono": proveedor_db.telefono
                }
        
        productos.append({
            "id_producto": producto.id_producto,
            "nombre": producto.nombre,
            "descripcion": producto.descripcion,
            "codigo_barras": producto.codigo_barras,
            "imagen_url": producto.imagen_url,
            "id_categoria": producto.id_categoria,
            "id_proveedor": producto.id_proveedor,
            "estado": producto.estado,
            "costo_bruto": producto.costo_bruto,
            "costo_neto": producto.costo_neto,
            "porcentaje_utilidad": producto.porcentaje_utilidad,
            "utilidad_pesos": producto.utilidad_pesos,
            "cantidad_actual": producto.cantidad_actual,
            "stock_minimo": producto.stock_minimo,
            "codigo_interno": producto.codigo_interno,
            "fecha_creacion": producto.fecha_creacion.isoformat() if producto.fecha_creacion else None,
            "categoria": categoria,
            "proveedor": proveedor
        })
    
    return productos

@app.get("/productos/{producto_id}", response_model=Producto)
def obtener_producto(
    producto_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener un producto por ID"""
    producto = db.query(ProductoDB).filter(ProductoDB.id_producto == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Obtener la categoría si existe
    categoria = None
    if producto.id_categoria:
        categoria_db = db.query(CategoriaDB).filter(CategoriaDB.id_categoria == producto.id_categoria).first()
        if categoria_db:
            categoria = categoria_db.nombre
    
    # Obtener el precio y stock del inventario si existe
    precio = 0.0
    stock = 0
    inventario = db.query(InventarioDB).filter(InventarioDB.id_producto == producto.id_producto).first()
    if inventario:
        precio = inventario.precio
        stock = inventario.cantidad
    
    return {
        "id": producto.id_producto,
        "id_producto": producto.id_producto,  # Agregar para consistencia con inventario
        "nombre": producto.nombre,
        "descripcion": producto.descripcion,
        "caracteristicas": None,  # Este campo no está en ProductoDB
        "precio": precio,
        "imagen": producto.imagen_url,
        "categoria": categoria,
        "stock": stock,
        "fecha_creacion": producto.fecha_creacion.isoformat() if producto.fecha_creacion else None
    }

@app.post("/productos", response_model=Producto)
def crear_producto(
    producto_data: dict,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear un nuevo producto"""
    if current_user.role not in ["administrador", "almacenista", "bodeguero"]:
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para crear productos"
        )
    
    # Extraer los campos para ProductoDB
    producto_dict = {
        "nombre": producto_data.get("nombre"),
        "descripcion": producto_data.get("descripcion"),
        "codigo_barras": producto_data.get("codigo_barras"),
        "imagen_url": producto_data.get("imagen"),  # Usar 'imagen' en lugar de 'imagen_url'
        "id_categoria": producto_data.get("id_categoria"),
        "id_proveedor": producto_data.get("id_proveedor"),
        "estado": producto_data.get("estado", "activo"),
        "costo_bruto": producto_data.get("costo_bruto", 0.0),
        "costo_neto": producto_data.get("costo_neto", 0.0),
        "porcentaje_utilidad": producto_data.get("porcentaje_utilidad", 0.0),
        "utilidad_pesos": producto_data.get("utilidad_pesos", 0.0),
        "cantidad_actual": producto_data.get("cantidad_actual", 0),
        "stock_minimo": producto_data.get("stock_minimo", 0)
    }
    
    # Verificar categoría
    categoria = None
    if producto_dict["id_categoria"]:
        categoria = db.query(CategoriaDB).filter(CategoriaDB.id_categoria == producto_dict["id_categoria"]).first()
        if not categoria:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    # Verificar proveedor
    if producto_dict["id_proveedor"]:
        proveedor = db.query(ProveedorDB).filter(ProveedorDB.id_proveedor == producto_dict["id_proveedor"]).first()
        if not proveedor:
            raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    # Verificar código de barras único
    if producto_dict["codigo_barras"]:
        existe_codigo = db.query(ProductoDB).filter(ProductoDB.codigo_barras == producto_dict["codigo_barras"]).first()
        if existe_codigo:
            raise HTTPException(status_code=400, detail="El código de barras ya existe")
    
    # Crear el producto
    db_producto = ProductoDB(**producto_dict)
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    
    # Si hay precio y stock, crear un registro de inventario
    precio = producto_data.get("precio", 0.0)
    stock = producto_data.get("stock", 0) or producto_data.get("cantidad", 0)
    
    # Asegurarse de que los valores sean numéricos
    try:
        precio = float(precio)
        stock = int(stock)
    except (ValueError, TypeError):
        precio = 0.0
        stock = 0
    
    if stock > 0:
        inventario = InventarioDB(
            id_producto=db_producto.id_producto,
            precio=precio,
            cantidad=stock
        )
        db.add(inventario)
        db.commit()
    
    # Convertir el producto de la base de datos al modelo Pydantic para la respuesta
    return {
        "id": db_producto.id_producto,
        "id_producto": db_producto.id_producto,  # Agregar para consistencia con inventario
        "nombre": db_producto.nombre,
        "descripcion": db_producto.descripcion,
        "caracteristicas": None,  # Este campo no está en ProductoDB
        "precio": precio,
        "imagen": db_producto.imagen_url,
        "categoria": {
            "id_categoria": categoria.id_categoria,
            "nombre": categoria.nombre
        } if categoria else None,
        "proveedor": None,  # Agregar campo proveedor
        "stock": stock,
        "fecha_creacion": db_producto.fecha_creacion.isoformat() if db_producto.fecha_creacion else None
    }

@app.put("/productos/{producto_id}", response_model=Producto)
def actualizar_producto(
    producto_id: int,
    producto: ProductoUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar un producto existente"""
    if current_user.role not in ["administrador", "almacenista", "bodeguero"]:
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para actualizar productos"
        )
    
    db_producto = db.query(ProductoDB).filter(ProductoDB.id_producto == producto_id).first()
    if not db_producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Verificar categoría si se proporciona
    if producto.id_categoria is not None:
        categoria = db.query(CategoriaDB).filter(CategoriaDB.id_categoria == producto.id_categoria).first()
        if not categoria:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    # Verificar proveedor si se proporciona
    if producto.id_proveedor is not None:
        proveedor = db.query(ProveedorDB).filter(ProveedorDB.id_proveedor == producto.id_proveedor).first()
        if not proveedor:
            raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    # Verificar código de barras único si se proporciona
    if producto.codigo_barras is not None:
        producto_existente = db.query(ProductoDB).filter(
            ProductoDB.codigo_barras == producto.codigo_barras,
            ProductoDB.id_producto != producto_id
        ).first()
        if producto_existente:
            raise HTTPException(status_code=400, detail="Ya existe un producto con este código de barras")
    
    # Actualizar campos
    for field, value in producto.dict(exclude_unset=True).items():
        setattr(db_producto, field, value)
    
    # Actualizar stock_minimo si se proporciona
    if hasattr(producto, 'stock_minimo') and producto.stock_minimo is not None:
        db_producto.stock_minimo = producto.stock_minimo
    
    db.commit()
    db.refresh(db_producto)
    return db_producto

@app.delete("/productos/{producto_id}")
def eliminar_producto(
    producto_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar un producto"""
    # Verificar permisos de administrador
    verificar_permisos_admin(current_user, "eliminar productos")
    
    producto = db.query(ProductoDB).filter(ProductoDB.id_producto == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Verificar si hay inventario asociado
    inventario_asociado = db.query(InventarioDB).filter(InventarioDB.id_producto == producto_id).count()
    if inventario_asociado > 0:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede eliminar el producto porque tiene {inventario_asociado} registros de inventario asociados"
        )
    
    db.delete(producto)
    db.commit()
    return {"message": "Producto eliminado correctamente"}

# ==================== ENDPOINTS CRUD PARA INVENTARIO ====================

@app.get("/catalogo-inventario")
def obtener_catalogo_inventario(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint unificado que devuelve productos separados en:
    - catalogados: productos con descripción e imagen (listos para catálogo)
    - inventario: productos sin descripción o imagen (solo inventario)
    Usa la misma estructura de datos que el endpoint /inventario
    """
    try:
        # Obtener todos los registros de inventario con sus productos relacionados
        inventario_query = db.query(InventarioDB).all()
        
        catalogados = []
        inventario_solo = []
        
        for item in inventario_query:
            # Crear estructura igual a la del endpoint /inventario
            producto = None
            if item.producto:
                producto_dict = {
                    "id_producto": item.producto.id_producto,
                    "nombre": item.producto.nombre,
                    "descripcion": item.producto.descripcion,
                    "codigo_barras": item.producto.codigo_barras,
                    "codigo_interno": item.producto.codigo_interno,
                    "imagen_url": item.producto.imagen_url,
                    "id_categoria": item.producto.id_categoria,
                    "id_proveedor": item.producto.id_proveedor,
                    "estado": item.producto.estado,
                    "fecha_creacion": item.producto.fecha_creacion.isoformat() if item.producto.fecha_creacion else None
                }
                producto = producto_dict
            
            # Estructura de inventario igual al endpoint /inventario
            inventario_data = {
                "id_inventario": item.id_inventario,
                "id_producto": item.id_producto,
                "precio": int(item.precio),
                "cantidad": item.cantidad,
                "fecha_registro": item.fecha_registro.isoformat() if item.fecha_registro else None,
                "producto": producto
            }
            
            # Separar entre catalogados e inventario según criterios
            if (item.producto and item.producto.descripcion and 
                item.producto.imagen_url and item.precio):
                catalogados.append(inventario_data)
            else:
                inventario_solo.append(inventario_data)
        
        return {
            "catalogados": catalogados,
            "inventario": inventario_solo,
            "total_catalogados": len(catalogados),
            "total_inventario": len(inventario_solo)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener datos del catálogo e inventario: {str(e)}"
        )

@app.post("/catalogar-producto/{producto_id}")
async def catalogar_producto(
    producto_id: int,
    precio: int = Form(None),
    descripcion: str = Form(None),
    caracteristicas: str = Form(None),
    imagen: UploadFile = File(None),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Catalogar un producto del inventario agregando los campos necesarios para el catálogo
    """
    try:
        # Verificar que el producto existe
        producto = db.query(ProductoDB).filter(ProductoDB.id_producto == producto_id).first()
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado"
            )
        
        # Procesar imagen si se proporciona
        imagen_url = None
        if imagen and imagen.filename:
            try:
                imagen_url = await upload_image(imagen)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Error al subir imagen: {str(e)}"
                )
        
        # Actualizar el producto con los datos del catálogo
        if descripcion:
            producto.descripcion = descripcion
        if imagen_url:
            producto.imagen_url = imagen_url
        
        # Actualizar o crear entrada en inventario con el precio (solo si se proporciona)
        inventario_item = db.query(InventarioDB).filter(InventarioDB.id_producto == producto_id).first()
        if inventario_item:
            if precio is not None:
                inventario_item.precio = precio
                # Actualizar campos adicionales del producto solo si hay precio
                producto.costo_bruto = inventario_item.precio * 0.8  # Ejemplo: 80% del precio de venta
                producto.costo_neto = producto.costo_bruto * 0.9  # Ejemplo: 90% del costo bruto
                producto.porcentaje_utilidad = ((precio - producto.costo_neto) / producto.costo_neto) * 100
                producto.utilidad_pesos = precio - producto.costo_neto
            producto.cantidad_actual = inventario_item.cantidad
            producto.stock_minimo = 5  # Valor por defecto
        else:
            # Solo crear nueva entrada de inventario si se proporciona precio
            if precio is not None:
                nuevo_inventario = InventarioDB(
                    id_producto=producto_id,
                    precio=precio,
                    cantidad=0
                )
                db.add(nuevo_inventario)
                inventario_item = nuevo_inventario
                # Actualizar campos adicionales del producto
                producto.costo_bruto = precio * 0.8  # Ejemplo: 80% del precio de venta
                producto.costo_neto = producto.costo_bruto * 0.9  # Ejemplo: 90% del costo bruto
                producto.porcentaje_utilidad = ((precio - producto.costo_neto) / producto.costo_neto) * 100
                producto.utilidad_pesos = precio - producto.costo_neto
                producto.cantidad_actual = 0
                producto.stock_minimo = 5  # Valor por defecto
            else:
                # Si no hay precio, solo actualizar los campos del producto sin crear inventario
                producto.stock_minimo = 5  # Valor por defecto
        
        db.commit()
        db.refresh(producto)
        
        return {
            "message": "Producto catalogado correctamente",
            "producto": {
                "id_producto": producto.id_producto,
                "nombre": producto.nombre,
                "precio": int(inventario_item.precio) if inventario_item and inventario_item.precio else 0,
                "descripcion": producto.descripcion,
                "imagen": producto.imagen_url
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al catalogar producto: {str(e)}"
        )

@app.put("/catalogar-producto/{producto_id}")
async def editar_producto_catalogado(
    producto_id: int,
    precio: int = Form(None),
    descripcion: str = Form(None),
    caracteristicas: str = Form(None),
    stock_minimo: int = Form(None),
    imagen: UploadFile = File(None),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Editar un producto catalogado
    """
    try:
        # Verificar que el producto existe
        producto = db.query(ProductoDB).filter(ProductoDB.id_producto == producto_id).first()
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado"
            )
        
        # Verificar que el producto está catalogado (tiene entrada en inventario)
        inventario_item = db.query(InventarioDB).filter(InventarioDB.id_producto == producto_id).first()
        if not inventario_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no está catalogado"
            )
        
        # Procesar imagen si se proporciona
        if imagen and imagen.filename:
            try:
                imagen_url = await upload_image(imagen)
                producto.imagen_url = imagen_url
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Error al subir imagen: {str(e)}"
                )
        
        # Actualizar campos del producto
        if descripcion is not None:
            producto.descripcion = descripcion
        
        # Actualizar stock mínimo si se proporciona
        if stock_minimo is not None:
            producto.stock_minimo = stock_minimo
        
        # Actualizar precio en inventario y campos adicionales del producto
        if precio is not None:
            inventario_item.precio = precio
            # Actualizar campos adicionales del producto
            producto.costo_bruto = precio * 0.8  # Ejemplo: 80% del precio de venta
            producto.costo_neto = producto.costo_bruto * 0.9  # Ejemplo: 90% del costo bruto
            producto.porcentaje_utilidad = ((precio - producto.costo_neto) / producto.costo_neto) * 100
            producto.utilidad_pesos = precio - producto.costo_neto
            producto.cantidad_actual = inventario_item.cantidad
            if producto.stock_minimo is None:
                producto.stock_minimo = 5  # Valor por defecto si no está establecido
        
        db.commit()
        db.refresh(producto)
        db.refresh(inventario_item)
        
        return {
            "message": "Producto editado correctamente",
            "producto": {
                "id_producto": producto.id_producto,
                "nombre": producto.nombre,
                "precio": int(inventario_item.precio),
                "descripcion": producto.descripcion,
                "imagen": producto.imagen_url
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al editar producto: {str(e)}"
        )

@app.delete("/catalogar-producto/{producto_id}")
def eliminar_producto_catalogado(
    producto_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Eliminar un producto del catálogo (eliminar entrada de inventario pero mantener el producto)
    """
    try:
        # Verificar que el producto existe
        producto = db.query(ProductoDB).filter(ProductoDB.id_producto == producto_id).first()
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado"
            )
        
        # Verificar que el producto está catalogado (tiene entrada en inventario)
        inventario_item = db.query(InventarioDB).filter(InventarioDB.id_producto == producto_id).first()
        if not inventario_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no está catalogado"
            )
        
        # Eliminar la entrada del inventario (descatalogar)
        db.delete(inventario_item)
        
        # Limpiar campos de catálogo del producto
        producto.descripcion = None
        producto.imagen_url = None
        
        db.commit()
        
        return {
            "message": "Producto eliminado del catálogo correctamente",
            "producto_id": producto_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar producto del catálogo: {str(e)}"
        )

@app.get("/inventario", response_model=List[Inventario])
def obtener_inventario(
    skip: int = 0,
    limit: int = 100,
    producto_id: Optional[int] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener registros de inventario con filtros opcionales"""
    query = db.query(InventarioDB)
    
    if producto_id:
        query = query.filter(InventarioDB.id_producto == producto_id)
    
    inventario_items = query.offset(skip).limit(limit).all()
    
    # Convertir fechas a formato string antes de devolver
    result = []
    for item in inventario_items:
        producto = None
        if item.producto:
            producto_dict = {
                "id_producto": item.producto.id_producto,
                "nombre": item.producto.nombre,
                "descripcion": item.producto.descripcion,
                "codigo_barras": item.producto.codigo_barras,
                "imagen_url": item.producto.imagen_url,
                "id_categoria": item.producto.id_categoria,
                "id_proveedor": item.producto.id_proveedor,
                "estado": item.producto.estado,
                "fecha_creacion": item.producto.fecha_creacion.isoformat() if item.producto.fecha_creacion else None
            }
            producto = producto_dict
            
        result.append({
            "id_inventario": item.id_inventario,
            "id_producto": item.id_producto,
            "precio": int(item.precio),
            "cantidad": item.cantidad,
            "fecha_registro": item.fecha_registro.isoformat() if item.fecha_registro else None,
            "producto": producto
        })
    
    return result

@app.get("/inventario/{inventario_id}", response_model=Inventario)
def obtener_inventario_item(
    inventario_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener un registro de inventario por ID"""
    item = db.query(InventarioDB).filter(InventarioDB.id_inventario == inventario_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Registro de inventario no encontrado")
    
    # Convertir fechas a formato string antes de devolver
    producto = None
    if item.producto:
        producto_dict = {
            "id_producto": item.producto.id_producto,
            "nombre": item.producto.nombre,
            "descripcion": item.producto.descripcion,
            "codigo_barras": item.producto.codigo_barras,
            "codigo_interno": item.producto.codigo_interno,
            "imagen_url": item.producto.imagen_url,
            "id_categoria": item.producto.id_categoria,
            "id_proveedor": item.producto.id_proveedor,
            "costo_bruto": item.producto.costo_bruto or 0,
            "costo_neto": item.producto.costo_neto or 0,
            "porcentaje_utilidad": item.producto.porcentaje_utilidad or 0,
            "utilidad_pesos": item.producto.utilidad_pesos or 0,
            "stock_minimo": item.producto.stock_minimo or 0,
            "estado": item.producto.estado,
            "fecha_creacion": item.producto.fecha_creacion.isoformat() if item.producto.fecha_creacion else None
        }
        producto = producto_dict
        
    result = {
        "id_inventario": item.id_inventario,
        "id_producto": item.id_producto,
        "precio": int(item.precio),
        "cantidad": item.cantidad,
        "fecha_registro": item.fecha_registro.isoformat() if item.fecha_registro else None,
        "producto": producto
    }
    
    return result

@app.post("/inventario", response_model=Inventario)
def crear_inventario(
    inventario: InventarioCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear un nuevo registro de inventario"""
    if current_user.role not in ["administrador", "almacenista", "bodeguero"]:
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para crear registros de inventario"
        )
    
    # Verificar que el producto existe
    producto = db.query(ProductoDB).filter(ProductoDB.id_producto == inventario.id_producto).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    db_inventario = InventarioDB(**inventario.dict())
    db.add(db_inventario)
    db.commit()
    db.refresh(db_inventario)
    return db_inventario

@app.put("/inventario/{inventario_id}", response_model=Inventario)
def actualizar_inventario(
    inventario_id: int,
    inventario: InventarioUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar un registro de inventario existente"""
    if current_user.role not in ["administrador", "almacenista", "bodeguero"]:
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para actualizar inventario"
        )
    
    db_inventario = db.query(InventarioDB).filter(InventarioDB.id_inventario == inventario_id).first()
    if not db_inventario:
        raise HTTPException(status_code=404, detail="Registro de inventario no encontrado")
    
    # Actualizar campos
    for field, value in inventario.dict(exclude_unset=True).items():
        setattr(db_inventario, field, value)
    
    db.commit()
    db.refresh(db_inventario)
    return db_inventario

@app.delete("/inventario/{inventario_id}")
def eliminar_inventario(
    inventario_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar un registro de inventario"""
    # Verificar permisos de administrador
    verificar_permisos_admin(current_user, "eliminar registros de inventario")
    
    inventario = db.query(InventarioDB).filter(InventarioDB.id_inventario == inventario_id).first()
    if not inventario:
        raise HTTPException(status_code=404, detail="Registro de inventario no encontrado")
    
    db.delete(inventario)
    db.commit()
    return {"message": "Registro de inventario eliminado correctamente"}

# ==================== ENDPOINTS CRUD PARA MOVIMIENTOS DE INVENTARIO ====================


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)