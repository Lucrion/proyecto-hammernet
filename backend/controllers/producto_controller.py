#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Controlador de productos
Maneja todas las operaciones CRUD de productos y funcionalidades específicas
"""

from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from models.producto import ProductoDB, ProductoCreate, ProductoUpdate, Producto, ProductoNuevoBase
from models.categoria import CategoriaDB
from models.proveedor import ProveedorDB
import cloudinary.uploader
import uuid


class ProductoController:
    """Controlador para manejo de productos"""
    
    @staticmethod
    async def crear_producto(producto: ProductoCreate, db: Session) -> Producto:
        """
        Crea un nuevo producto
        
        Args:
            producto: Datos del producto a crear
            db: Sesión de base de datos
            
        Returns:
            Producto: Producto creado
            
        Raises:
            HTTPException: Si hay error en la creación
        """
        try:
            # Verificar que existan la categoría y proveedor
            categoria = db.query(CategoriaDB).filter(CategoriaDB.id_categoria == producto.id_categoria).first()
            if not categoria:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La categoría especificada no existe"
                )
            
            proveedor = db.query(ProveedorDB).filter(ProveedorDB.id_proveedor == producto.id_proveedor).first()
            if not proveedor:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El proveedor especificado no existe"
                )
            
            # Generar código interno único
            codigo_interno = str(uuid.uuid4())[:8].upper()
            
            db_producto = ProductoDB(
                **producto.dict(),
                codigo_interno=codigo_interno
            )
            
            db.add(db_producto)
            db.commit()
            db.refresh(db_producto)
            
            # Cargar relaciones
            db_producto = db.query(ProductoDB).options(
                joinedload(ProductoDB.categoria),
                joinedload(ProductoDB.proveedor)
            ).filter(ProductoDB.id_producto == db_producto.id_producto).first()
            
            return Producto(
                id_producto=db_producto.id_producto,
                nombre=db_producto.nombre,
                descripcion=db_producto.descripcion,
                codigo_interno=db_producto.codigo_interno,
                imagen_url=db_producto.imagen_url,
                id_categoria=db_producto.id_categoria,
                id_proveedor=db_producto.id_proveedor,
                categoria=db_producto.categoria.nombre if db_producto.categoria else None,
                proveedor=db_producto.proveedor.nombre if db_producto.proveedor else None
            )
            
        except HTTPException:
            raise
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un producto con ese nombre"
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear producto: {str(e)}"
            )
    
    @staticmethod
    async def obtener_productos(db: Session, categoria_id: Optional[int] = None) -> List[Producto]:
        """
        Obtiene todos los productos o filtrados por categoría
        
        Args:
            db: Sesión de base de datos
            categoria_id: ID de categoría para filtrar (opcional)
            
        Returns:
            List[Producto]: Lista de productos
        """
        try:
            query = db.query(ProductoDB).options(
                joinedload(ProductoDB.categoria),
                joinedload(ProductoDB.proveedor)
            )
            
            if categoria_id:
                query = query.filter(ProductoDB.id_categoria == categoria_id)
            
            productos = query.all()
            
            return [
                Producto(
                    id_producto=p.id_producto,
                    nombre=p.nombre,
                    descripcion=p.descripcion,
                    codigo_interno=p.codigo_interno,
                    imagen_url=p.imagen_url,
                    id_categoria=p.id_categoria,
                    id_proveedor=p.id_proveedor,
                    categoria=p.categoria.nombre if p.categoria else None,
                    proveedor=p.proveedor.nombre if p.proveedor else None
                ) for p in productos
            ]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener productos: {str(e)}"
            )
    
    @staticmethod
    async def obtener_producto(producto_id: int, db: Session) -> Producto:
        """
        Obtiene un producto por ID
        
        Args:
            producto_id: ID del producto
            db: Sesión de base de datos
            
        Returns:
            Producto: Producto encontrado
            
        Raises:
            HTTPException: Si el producto no existe
        """
        try:
            producto = db.query(ProductoDB).options(
                joinedload(ProductoDB.categoria),
                joinedload(ProductoDB.proveedor)
            ).filter(ProductoDB.id_producto == producto_id).first()
            
            if not producto:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Producto no encontrado"
                )
            
            return Producto(
                id_producto=producto.id_producto,
                nombre=producto.nombre,
                descripcion=producto.descripcion,
                codigo_interno=producto.codigo_interno,
                imagen_url=producto.imagen_url,
                id_categoria=producto.id_categoria,
                id_proveedor=producto.id_proveedor,
                categoria=producto.categoria.nombre if producto.categoria else None,
                proveedor=producto.proveedor.nombre if producto.proveedor else None
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener producto: {str(e)}"
            )
    
    @staticmethod
    async def actualizar_producto(producto_id: int, producto_update: ProductoUpdate, db: Session) -> Producto:
        """
        Actualiza un producto
        
        Args:
            producto_id: ID del producto
            producto_update: Datos a actualizar
            db: Sesión de base de datos
            
        Returns:
            Producto: Producto actualizado
            
        Raises:
            HTTPException: Si el producto no existe o hay error
        """
        try:
            producto = db.query(ProductoDB).filter(ProductoDB.id_producto == producto_id).first()
            if not producto:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Producto no encontrado"
                )
            
            # Verificar relaciones si se actualizan
            if producto_update.id_categoria is not None:
                categoria = db.query(CategoriaDB).filter(CategoriaDB.id_categoria == producto_update.id_categoria).first()
                if not categoria:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="La categoría especificada no existe"
                    )
            
            if producto_update.id_proveedor is not None:
                proveedor = db.query(ProveedorDB).filter(ProveedorDB.id_proveedor == producto_update.id_proveedor).first()
                if not proveedor:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="El proveedor especificado no existe"
                    )
            
            # Actualizar campos
            for field, value in producto_update.dict(exclude_unset=True).items():
                setattr(producto, field, value)
            
            db.commit()
            db.refresh(producto)
            
            # Cargar relaciones
            producto = db.query(ProductoDB).options(
                joinedload(ProductoDB.categoria),
                joinedload(ProductoDB.proveedor)
            ).filter(ProductoDB.id_producto == producto_id).first()
            
            return Producto(
                id_producto=producto.id_producto,
                nombre=producto.nombre,
                descripcion=producto.descripcion,
                codigo_interno=producto.codigo_interno,
                imagen_url=producto.imagen_url,
                id_categoria=producto.id_categoria,
                id_proveedor=producto.id_proveedor,
                categoria=producto.categoria.nombre if producto.categoria else None,
                proveedor=producto.proveedor.nombre if producto.proveedor else None
            )
            
        except HTTPException:
            raise
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un producto con ese nombre"
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al actualizar producto: {str(e)}"
            )
    
    @staticmethod
    async def eliminar_producto(producto_id: int, db: Session) -> dict:
        """
        Elimina un producto
        
        Args:
            producto_id: ID del producto
            db: Sesión de base de datos
            
        Returns:
            dict: Mensaje de confirmación
            
        Raises:
            HTTPException: Si el producto no existe o hay error
        """
        try:
            producto = db.query(ProductoDB).filter(ProductoDB.id_producto == producto_id).first()
            if not producto:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Producto no encontrado"
                )
            
            db.delete(producto)
            db.commit()
            
            return {"message": "Producto eliminado exitosamente"}
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al eliminar producto: {str(e)}"
            )
    
    @staticmethod
    async def subir_imagen_producto(producto_id: int, file: UploadFile, db: Session) -> dict:
        """
        Sube una imagen para un producto
        
        Args:
            producto_id: ID del producto
            file: Archivo de imagen
            db: Sesión de base de datos
            
        Returns:
            dict: URL de la imagen subida
            
        Raises:
            HTTPException: Si hay error en la subida
        """
        try:
            producto = db.query(ProductoDB).filter(ProductoDB.id_producto == producto_id).first()
            if not producto:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Producto no encontrado"
                )
            
            # Subir imagen a Cloudinary
            result = cloudinary.uploader.upload(
                file.file,
                folder="productos",
                public_id=f"producto_{producto_id}_{uuid.uuid4().hex[:8]}"
            )
            
            # Actualizar URL en la base de datos
            producto.imagen_url = result['secure_url']
            db.commit()
            
            return {"imagen_url": result['secure_url']}
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al subir imagen: {str(e)}"
            )
    
    @staticmethod
    async def buscar_productos(query: str, db: Session) -> List[Producto]:
        """
        Busca productos por nombre o descripción
        
        Args:
            query: Término de búsqueda
            db: Sesión de base de datos
            
        Returns:
            List[Producto]: Lista de productos encontrados
        """
        try:
            productos = db.query(ProductoDB).options(
                joinedload(ProductoDB.categoria),
                joinedload(ProductoDB.proveedor)
            ).filter(
                ProductoDB.nombre.ilike(f"%{query}%") |
                ProductoDB.descripcion.ilike(f"%{query}%")
            ).all()
            
            return [
                Producto(
                    id_producto=p.id_producto,
                    nombre=p.nombre,
                    descripcion=p.descripcion,
                    codigo_interno=p.codigo_interno,
                    imagen_url=p.imagen_url,
                    id_categoria=p.id_categoria,
                    id_proveedor=p.id_proveedor,
                    categoria=p.categoria.nombre if p.categoria else None,
                    proveedor=p.proveedor.nombre if p.proveedor else None
                ) for p in productos
            ]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al buscar productos: {str(e)}"
            )