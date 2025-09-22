#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, DECIMAL
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Nuevos modelos basados en el esquema actualizado

class CategoriaDB(Base):
    __tablename__ = "categorias"
    
    id_categoria = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(500), nullable=True)
    
    # Relación con productos
    productos = relationship("ProductoDB", back_populates="categoria")

class ProveedorDB(Base):
    __tablename__ = "proveedores"
    
    id_proveedor = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    rut = Column(String(20), nullable=True)
    razon_social = Column(String(200), nullable=True)
    sucursal = Column(String(100), nullable=True)
    direccion = Column(String(200), nullable=True)
    ciudad = Column(String(100), nullable=True)
    celular = Column(String(50), nullable=True)
    correo = Column(String(100), nullable=True)
    contacto = Column(String(100), nullable=True)
    telefono = Column(String(50), nullable=True)
    
    # Relación con productos
    productos = relationship("ProductoDB", back_populates="proveedor")

class ProductoDB(Base):
    __tablename__ = "productos"
    
    id_producto = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(String(1000), nullable=True)
    codigo_interno = Column(String(50), unique=True, nullable=True)
    codigo_barras = Column(String(50), unique=True, nullable=True)
    imagen_url = Column(String(500), nullable=True)
    id_categoria = Column(Integer, ForeignKey("categorias.id_categoria"), nullable=True)
    id_proveedor = Column(Integer, ForeignKey("proveedores.id_proveedor"), nullable=True)
    estado = Column(String(20), default="activo", nullable=False)
    fecha_creacion = Column(DateTime, default=func.now())
    
    # Nuevos campos agregados
    costo_bruto = Column(Integer, nullable=True)
    costo_neto = Column(Integer, nullable=True)
    porcentaje_utilidad = Column(Integer, nullable=True)  # %utilidad
    utilidad_pesos = Column(Integer, nullable=True)  # Utilidad en $
    cantidad_actual = Column(Integer, default=0, nullable=False)
    stock_minimo = Column(Integer, default=0, nullable=False)
    
    # Relaciones
    categoria = relationship("CategoriaDB", back_populates="productos")
    proveedor = relationship("ProveedorDB", back_populates="productos")
    inventarios = relationship("InventarioDB", back_populates="producto")

class InventarioDB(Base):
    __tablename__ = "inventario"
    id_inventario = Column(Integer, primary_key=True, index=True)
    id_producto = Column(Integer, ForeignKey("productos.id_producto"), nullable=False)
    precio = Column(Integer, nullable=False)
    cantidad = Column(Integer, nullable=False)
    fecha_registro = Column(DateTime, default=func.now())
    
    # Relación
    producto = relationship("ProductoDB", back_populates="inventarios")



class UsuarioDB(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    fecha_creacion = Column(DateTime, default=func.now())

# Definir primero las clases base de Categoria y Proveedor
class CategoriaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None

class Categoria(CategoriaBase):
    id_categoria: int
    
    class Config:
        orm_mode = True

class ProveedorBase(BaseModel):
    nombre: str
    rut: Optional[str] = None
    razon_social: Optional[str] = None
    sucursal: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    celular: Optional[str] = None
    correo: Optional[str] = None
    contacto: Optional[str] = None
    telefono: Optional[str] = None

class ProveedorCreate(ProveedorBase):
    pass

class ProveedorUpdate(BaseModel):
    nombre: Optional[str] = None
    rut: Optional[str] = None
    razon_social: Optional[str] = None
    sucursal: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    celular: Optional[str] = None
    correo: Optional[str] = None
    contacto: Optional[str] = None
    telefono: Optional[str] = None

class Proveedor(ProveedorBase):
    id_proveedor: int
    
    class Config:
        orm_mode = True

# Ahora definir las clases de Producto
class ProductoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    codigo_barras: Optional[str] = None
    imagen_url: Optional[str] = None
    id_categoria: Optional[int] = None
    id_proveedor: Optional[int] = None
    estado: Optional[str] = "activo"
    costo_bruto: Optional[int] = None
    costo_neto: Optional[int] = None
    porcentaje_utilidad: Optional[int] = None
    utilidad_pesos: Optional[int] = None
    cantidad_actual: Optional[int] = 0
    stock_minimo: Optional[int] = 0

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    codigo_interno: Optional[str] = None
    codigo_barras: Optional[str] = None
    imagen_url: Optional[str] = None
    id_categoria: Optional[int] = None
    id_proveedor: Optional[int] = None
    estado: Optional[str] = None
    costo_bruto: Optional[int] = None
    costo_neto: Optional[int] = None
    porcentaje_utilidad: Optional[int] = None
    utilidad_pesos: Optional[int] = None
    cantidad_actual: Optional[int] = None
    stock_minimo: Optional[int] = None

class Producto(ProductoBase):
    id_producto: int
    codigo_interno: Optional[str] = None
    fecha_creacion: Optional[str] = None
    categoria: Optional[dict] = None
    proveedor: Optional[dict] = None
    
    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class UsuarioBase(BaseModel):
    nombre: str
    username: str
    role: str

class UsuarioCreate(UsuarioBase):
    password: str

class Usuario(UsuarioBase):
    id: int
    fecha_creacion: Optional[str] = None
    
    class Config:
        orm_mode = True

class UsuarioLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    id: int
    nombre: str
    username: str
    role: str



# InventarioDB eliminado - usar ProductoUnificadoDB

class MensajeContactoDB(Base):
    __tablename__ = "mensajes_contacto"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    asunto = Column(String(200), nullable=False)
    mensaje = Column(String(1000), nullable=False)
    fecha_envio = Column(DateTime, default=func.now())
    leido = Column(Boolean, default=False)

from pydantic import BaseModel, Field, EmailStr

# Modelos Pydantic de Inventario eliminados - usar ProductoUnificado



class MensajeContactoBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre del remitente")
    apellido: str = Field(..., min_length=2, max_length=50, description="Apellido del remitente")
    email: EmailStr = Field(..., description="Correo electrónico del remitente")
    asunto: str = Field(..., min_length=5, max_length=200, description="Asunto del mensaje")
    mensaje: str = Field(..., min_length=10, max_length=1000, description="Contenido del mensaje")

    class Config:
        schema_extra = {
            'example': {
                'nombre': 'Juan',
                'apellido': 'Pérez',
                'email': 'juan.perez@example.com',
                'asunto': 'Consulta sobre productos',
                'mensaje': 'Me gustaría obtener más información sobre sus productos.'
            }
        }

class MensajeContactoCreate(MensajeContactoBase):
    pass

class MensajeContacto(MensajeContactoBase):
    id: int
    fecha_envio: str
    leido: bool
    
    class Config:
        orm_mode = True

# Las clases de Categoria y Proveedor ya están definidas arriba

# Modelos Pydantic para Productos (nuevo esquema)
class ProductoNuevoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    codigo_barras: Optional[str] = None
    imagen_url: Optional[str] = None
    id_categoria: Optional[int] = None
    id_proveedor: Optional[int] = None
    estado: Optional[str] = "activo"
    
    # Nuevos campos agregados
    costo_bruto: Optional[int] = None
    costo_neto: Optional[int] = None
    porcentaje_utilidad: Optional[int] = None
    utilidad_pesos: Optional[int] = None
    cantidad_actual: Optional[int] = 0
    stock_minimo: Optional[int] = 0

class ProductoNuevoCreate(ProductoNuevoBase):
    pass

class ProductoNuevoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    codigo_barras: Optional[str] = None
    imagen_url: Optional[str] = None
    id_categoria: Optional[int] = None
    id_proveedor: Optional[int] = None
    estado: Optional[str] = None
    
    # Nuevos campos agregados
    costo_bruto: Optional[int] = None
    costo_neto: Optional[int] = None
    porcentaje_utilidad: Optional[int] = None
    utilidad_pesos: Optional[int] = None
    cantidad_actual: Optional[int] = None
    stock_minimo: Optional[int] = None

class ProductoNuevo(ProductoNuevoBase):
    id_producto: int
    fecha_creacion: Optional[str] = None
    categoria: Optional[Categoria] = None
    proveedor: Optional[Proveedor] = None
    
    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

# Modelos Pydantic para Inventario
class InventarioBase(BaseModel):
    id_producto: int
    precio: int
    cantidad: int

class InventarioCreate(InventarioBase):
    pass

class InventarioUpdate(BaseModel):
    precio: Optional[int] = None
    cantidad: Optional[int] = None

class Inventario(InventarioBase):
    id_inventario: int
    fecha_registro: Optional[str] = None
    producto: Optional[ProductoNuevo] = None
    
    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }