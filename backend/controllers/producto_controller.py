#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Controlador de productos unificado
Maneja todas las operaciones CRUD de productos con inventario integrado
"""

from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from models.producto import ProductoDB, ProductoCreate, ProductoUpdate, Producto, ProductoInventario
from models.categoria import CategoriaDB
from models.proveedor import ProveedorDB
import cloudinary.uploader
import uuid


class ProductoController:
    """Controlador para manejo de productos unificado con inventario"""
    
    @staticmethod
    async def obtener_inventario_por_id(inventario_id: int, db: Session) -> ProductoInventario:
        """
        Obtiene un inventario específico por su ID
        
        Args:
            inventario_id: ID del inventario
            db: Sesión de base de datos
            
        Returns:
            ProductoInventario: Inventario específico
        """
        try:
            producto = db.query(ProductoDB).options(
                joinedload(ProductoDB.categoria),
                joinedload(ProductoDB.proveedor)
            ).filter(ProductoDB.id_producto == inventario_id).first()
            
            if not producto:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Inventario no encontrado"
                )
            
            # Crear el objeto ProductoInventario
            inventario_item = ProductoInventario(
                id_inventario=producto.id_producto,
                id_producto=producto.id_producto,
                precio=float(producto.precio_venta) if producto.precio_venta else 0,
                cantidad=producto.cantidad_actual if producto.cantidad_actual else 0,
                cantidad_disponible=producto.cantidad_disponible if producto.cantidad_disponible else 0,
                fecha_registro=producto.fecha_creacion.isoformat() if producto.fecha_creacion else None,
                producto={
                    "id_producto": producto.id_producto,
                    "nombre": producto.nombre,
                    "descripcion": producto.descripcion,
                    "id_categoria": producto.id_categoria,
                    "id_proveedor": producto.id_proveedor,
                    "marca": producto.marca,
                    "costo_bruto": float(producto.costo_bruto) if producto.costo_bruto else 0,
                    "costo_neto": float(producto.costo_neto) if producto.costo_neto else 0,
                    "precio_venta": float(producto.precio_venta) if producto.precio_venta else 0,
                    "porcentaje_utilidad": float(producto.porcentaje_utilidad) if producto.porcentaje_utilidad else 0,
                    "utilidad_pesos": float(producto.utilidad_pesos) if producto.utilidad_pesos else 0,
                    "cantidad_actual": producto.cantidad_actual if producto.cantidad_actual else 0,
                    "cantidad_disponible": producto.cantidad_disponible if producto.cantidad_disponible else 0,
                    "stock_minimo": producto.stock_minimo if producto.stock_minimo else 0,
                    "estado": producto.estado,
                    "categoria": producto.categoria.nombre if producto.categoria else None,
                    "proveedor": producto.proveedor.nombre if producto.proveedor else None
                }
            )
            
            return inventario_item
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener inventario: {str(e)}"
            )

    @staticmethod
    async def actualizar_inventario_por_id(inventario_id: int, inventario_data: dict, db: Session) -> ProductoInventario:
        """
        Actualiza un inventario específico por su ID
        
        Args:
            inventario_id: ID del inventario
            inventario_data: Datos de actualización
            db: Sesión de base de datos
            
        Returns:
            ProductoInventario: Inventario actualizado
        """
        try:
            producto = db.query(ProductoDB).filter(ProductoDB.id_producto == inventario_id).first()
            
            if not producto:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Inventario no encontrado"
                )
            
            # Actualizar campos del inventario
            if 'precio' in inventario_data:
                producto.precio_venta = inventario_data['precio']
            if 'cantidad' in inventario_data:
                producto.cantidad_actual = inventario_data['cantidad']
                producto.cantidad_disponible = inventario_data['cantidad']
            
            db.commit()
            db.refresh(producto)
            
            # Retornar el inventario actualizado
            return await ProductoController.obtener_inventario_por_id(inventario_id, db)
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al actualizar inventario: {str(e)}"
            )

    @staticmethod
    async def eliminar_inventario_por_id(inventario_id: int, db: Session) -> dict:
        """
        Elimina un inventario específico por su ID
        
        Args:
            inventario_id: ID del inventario
            db: Sesión de base de datos
            
        Returns:
            dict: Mensaje de confirmación
        """
        try:
            producto = db.query(ProductoDB).filter(ProductoDB.id_producto == inventario_id).first()
            
            if not producto:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Inventario no encontrado"
                )
            
            db.delete(producto)
            db.commit()
            
            return {"message": "Inventario eliminado exitosamente"}
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al eliminar inventario: {str(e)}"
            )

    @staticmethod
    async def crear_producto(producto: ProductoCreate, db: Session) -> Producto:
        """
        Crea un nuevo producto con información de inventario integrada
        
        Args:
            producto: Datos del producto a crear
            db: Sesión de base de datos
            
        Returns:
            Producto: Producto creado
            
        Raises:
            HTTPException: Si hay error en la creación
        """
        try:
            # Verificar que existan la categoría y proveedor si se especifican
            if producto.id_categoria:
                categoria = db.query(CategoriaDB).filter(CategoriaDB.id_categoria == producto.id_categoria).first()
                if not categoria:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="La categoría especificada no existe"
                    )
            
            if producto.id_proveedor:
                proveedor = db.query(ProveedorDB).filter(ProveedorDB.id_proveedor == producto.id_proveedor).first()
                if not proveedor:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="El proveedor especificado no existe"
                    )
            
            # Generar código interno único si no se proporciona
            if not producto.codigo_interno:
                codigo_interno = str(uuid.uuid4())[:8].upper()
            else:
                codigo_interno = producto.codigo_interno
            
            # Crear el producto con todos los campos del modelo unificado
            producto_data = producto.dict()
            producto_data['codigo_interno'] = codigo_interno
            
            db_producto = ProductoDB(**producto_data)
            
            db.add(db_producto)
            db.commit()
            db.refresh(db_producto)
            
            # Cargar relaciones
            db_producto = db.query(ProductoDB).options(
                joinedload(ProductoDB.categoria),
                joinedload(ProductoDB.proveedor)
            ).filter(ProductoDB.id_producto == db_producto.id_producto).first()
            
            return Producto.from_orm(db_producto)
            
        except HTTPException:
            raise
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un producto con ese código o nombre"
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
        Obtiene todos los productos con información de inventario integrada
        
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
            
            # Convertir manualmente para manejar fechas y relaciones
            productos_convertidos = []
            for p in productos:
                producto_dict = {
                    "id_producto": p.id_producto,
                    "nombre": p.nombre,
                    "descripcion": p.descripcion,
                    "codigo_interno": p.codigo_interno,
                    "imagen_url": p.imagen_url,
                    "id_categoria": p.id_categoria,
                    "id_proveedor": p.id_proveedor,
                    "marca": p.marca,
                    "costo_bruto": float(p.costo_bruto) if p.costo_bruto else 0,
                    "costo_neto": float(p.costo_neto) if p.costo_neto else 0,
                    "precio_venta": float(p.precio_venta) if p.precio_venta else 0,
                    "porcentaje_utilidad": float(p.porcentaje_utilidad) if p.porcentaje_utilidad else 0,
                    "utilidad_pesos": float(p.utilidad_pesos) if p.utilidad_pesos else 0,
                    "cantidad_actual": p.cantidad_actual,
                    "cantidad_disponible": p.cantidad_disponible,
                    "stock_minimo": p.stock_minimo,
                    "estado": p.estado,
                    "fecha_creacion": p.fecha_creacion,
                    "fecha_actualizacion": p.fecha_actualizacion,
                    "fecha_ultima_venta": p.fecha_ultima_venta,
                    "fecha_ultimo_ingreso": p.fecha_ultimo_ingreso,
                    "categoria": p.categoria.nombre if p.categoria else None,
                    "proveedor": p.proveedor.nombre if p.proveedor else None
                }
                productos_convertidos.append(Producto(**producto_dict))
            
            return productos_convertidos
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener productos: {str(e)}"
            )
    
    @staticmethod
    async def obtener_producto(producto_id: int, db: Session) -> Producto:
        """
        Obtiene un producto por ID con información de inventario
        
        Args:
            producto_id: ID del producto
            db: Sesión de base de datos
            
        Returns:
            Producto: Producto encontrado
            
        Raises:
            HTTPException: Si no se encuentra el producto
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
            
            # Crear el objeto Producto manualmente para evitar problemas de serialización
            categoria_nombre = None
            proveedor_nombre = None
            
            # Obtener nombre de categoría si existe
            if producto.categoria:
                categoria_nombre = producto.categoria.nombre
            elif producto.id_categoria:
                # Si no se cargó la relación, buscar manualmente
                categoria = db.query(CategoriaDB).filter(CategoriaDB.id_categoria == producto.id_categoria).first()
                if categoria:
                    categoria_nombre = categoria.nombre
            
            # Obtener nombre de proveedor si existe
            if producto.proveedor:
                proveedor_nombre = producto.proveedor.nombre
            elif producto.id_proveedor:
                # Si no se cargó la relación, buscar manualmente
                proveedor = db.query(ProveedorDB).filter(ProveedorDB.id_proveedor == producto.id_proveedor).first()
                if proveedor:
                    proveedor_nombre = proveedor.nombre
            
            producto_dict = {
                "id_producto": producto.id_producto,
                "nombre": producto.nombre,
                "descripcion": producto.descripcion,
                "codigo_interno": producto.codigo_interno,
                "imagen_url": producto.imagen_url,
                "id_categoria": producto.id_categoria,
                "id_proveedor": producto.id_proveedor,
                "marca": producto.marca,
                "costo_bruto": float(producto.costo_bruto) if producto.costo_bruto else 0,
                "costo_neto": float(producto.costo_neto) if producto.costo_neto else 0,
                "precio_venta": float(producto.precio_venta) if producto.precio_venta else 0,
                "porcentaje_utilidad": float(producto.porcentaje_utilidad) if producto.porcentaje_utilidad else 0,
                "utilidad_pesos": float(producto.utilidad_pesos) if producto.utilidad_pesos else 0,
                "cantidad_actual": producto.cantidad_actual,
                "cantidad_disponible": producto.cantidad_disponible,
                "stock_minimo": producto.stock_minimo,
                "estado": producto.estado,
                "fecha_creacion": producto.fecha_creacion,
                "fecha_actualizacion": producto.fecha_actualizacion,
                "fecha_ultima_venta": producto.fecha_ultima_venta,
                "fecha_ultimo_ingreso": producto.fecha_ultimo_ingreso,
                "categoria": categoria_nombre,
                "proveedor": proveedor_nombre
            }
            
            return Producto(**producto_dict)
            
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
            
            # Manejar categoria y proveedor manualmente para evitar errores de serialización
            categoria_nombre = None
            proveedor_nombre = None
            
            if hasattr(producto, 'categoria') and producto.categoria:
                categoria_nombre = producto.categoria.nombre
            elif producto.id_categoria:
                # Fallback: consultar la base de datos si la relación no está cargada
                categoria = db.query(CategoriaDB).filter(CategoriaDB.id_categoria == producto.id_categoria).first()
                if categoria:
                    categoria_nombre = categoria.nombre
            
            if hasattr(producto, 'proveedor') and producto.proveedor:
                proveedor_nombre = producto.proveedor.nombre
            elif producto.id_proveedor:
                # Fallback: consultar la base de datos si la relación no está cargada
                proveedor = db.query(ProveedorDB).filter(ProveedorDB.id_proveedor == producto.id_proveedor).first()
                if proveedor:
                    proveedor_nombre = proveedor.nombre
            
            # Construir el objeto Producto manualmente
            return Producto(
                id_producto=producto.id_producto,
                nombre=producto.nombre,
                descripcion=producto.descripcion,
                precio=producto.precio,
                cantidad_actual=producto.cantidad_actual,
                cantidad_minima=producto.cantidad_minima,
                id_categoria=producto.id_categoria,
                id_proveedor=producto.id_proveedor,
                categoria=categoria_nombre,
                proveedor=proveedor_nombre,
                fecha_creacion=producto.fecha_creacion,
                fecha_actualizacion=producto.fecha_actualizacion,
                activo=producto.activo,
                imagen_url=producto.imagen_url
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
            
            return [Producto.from_orm(p) for p in productos]
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al buscar productos: {str(e)}"
            )
    
    @staticmethod
    async def actualizar_inventario_producto(producto_id: int, inventario_data: dict, db: Session) -> Producto:
        """
        Actualiza la información de inventario de un producto
        
        Args:
            producto_id: ID del producto
            inventario_data: Datos de inventario a actualizar
            db: Sesión de base de datos
            
        Returns:
            Producto: Producto actualizado
        """
        try:
            producto = db.query(ProductoDB).filter(ProductoDB.id_producto == producto_id).first()
            
            if not producto:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Producto no encontrado"
                )
            
            # Actualizar campos de inventario disponibles
            campos_inventario = ['cantidad_actual', 'cantidad_disponible', 'stock_minimo']
            
            for campo in campos_inventario:
                if campo in inventario_data:
                    setattr(producto, campo, inventario_data[campo])
            
            db.commit()
            db.refresh(producto)
            
            return Producto.from_orm(producto)
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al actualizar inventario: {str(e)}"
            )

    @staticmethod
    async def obtener_inventario(db: Session) -> List[ProductoInventario]:
        """
        Obtiene todos los productos en formato de inventario
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            List[ProductoInventario]: Lista de productos en formato inventario
        """
        try:
            productos = db.query(ProductoDB).options(
                joinedload(ProductoDB.categoria),
                joinedload(ProductoDB.proveedor)
            ).all()
            
            inventario_list = []
            for p in productos:
                inventario_item = ProductoInventario(
                    id_inventario=p.id_producto,  # Usar id_producto como id_inventario
                    id_producto=p.id_producto,
                    precio=float(p.precio_venta) if p.precio_venta else 0.0,
                    cantidad=p.cantidad_actual if p.cantidad_actual else 0,
                    fecha_registro=p.fecha_creacion.isoformat() if p.fecha_creacion else None,
                    producto={
                        "id_producto": p.id_producto,
                        "nombre": p.nombre,
                        "descripcion": p.descripcion,
                        "codigo_interno": p.codigo_interno,
                        "imagen_url": p.imagen_url,
                        "id_categoria": p.id_categoria,
                        "id_proveedor": p.id_proveedor,
                        "marca": p.marca,
                        "costo_bruto": float(p.costo_bruto) if p.costo_bruto else 0,
                        "costo_neto": float(p.costo_neto) if p.costo_neto else 0,
                        "precio_venta": float(p.precio_venta) if p.precio_venta else 0,
                        "porcentaje_utilidad": float(p.porcentaje_utilidad) if p.porcentaje_utilidad else 0,
                        "utilidad_pesos": float(p.utilidad_pesos) if p.utilidad_pesos else 0,
                        "cantidad_actual": p.cantidad_actual if p.cantidad_actual else 0,
                        "cantidad_disponible": p.cantidad_disponible if p.cantidad_disponible else 0,
                        "stock_minimo": p.stock_minimo if p.stock_minimo else 0,
                        "estado": p.estado,
                        "categoria": p.categoria.nombre if p.categoria else None,
                        "proveedor": p.proveedor.nombre if p.proveedor else None
                    }
                )
                inventario_list.append(inventario_item)
            
            return inventario_list
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener inventario: {str(e)}"
            )

    @staticmethod
    async def obtener_resumen_inventario(db: Session) -> dict:
        """
        Obtiene un resumen del inventario total
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            dict: Resumen del inventario
        """
        try:
            productos = db.query(ProductoDB).all()
            
            total_productos = len(productos)
            productos_bajo_stock = len([p for p in productos if (p.cantidad_disponible or 0) <= (p.stock_minimo or 0)])
            productos_sin_stock = len([p for p in productos if (p.cantidad_disponible or 0) == 0])
            total_cantidad_actual = sum(p.cantidad_actual or 0 for p in productos)
            total_cantidad_disponible = sum(p.cantidad_disponible or 0 for p in productos)
            
            return {
                "total_productos": total_productos,
                "productos_bajo_stock": productos_bajo_stock,
                "productos_sin_stock": productos_sin_stock,
                "productos_con_stock": total_productos - productos_sin_stock,
                "total_cantidad_actual": total_cantidad_actual,
                "total_cantidad_disponible": total_cantidad_disponible
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener resumen de inventario: {str(e)}"
            )
    
    @staticmethod
    async def crear_producto_nuevo(producto: ProductoCreate, db: Session) -> Producto:
        """
        Crea un nuevo producto (método alternativo para compatibilidad)
        
        Args:
            producto: Datos del producto a crear
            db: Sesión de base de datos
            
        Returns:
            Producto: Producto creado
        """
        return await ProductoController.crear_producto(producto, db)