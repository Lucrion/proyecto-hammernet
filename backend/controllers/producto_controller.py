#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Controlador de productos unificado
Maneja todas las operaciones CRUD de productos con inventario integrado
"""

from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from typing import List, Optional
import uuid
import base64
import io
from models.producto import ProductoDB, ProductoCreate, ProductoUpdate, Producto, ProductoInventario
from models.catalogo import ProductoCatalogo, AgregarACatalogo
from models.categoria import CategoriaDB
from models.subcategoria import SubCategoriaDB
from models.proveedor import ProveedorDB
from config.cloudinary_config import upload_image
import cloudinary.uploader
from datetime import datetime


class ProductoController:
    """Controlador para manejo de productos unificado con inventario"""
    
    @staticmethod
    async def obtener_total_catalogo(db: Session) -> int:
        """
        Obtiene el total de productos en el catálogo público
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            int: Total de productos en catálogo
        """
        try:
            total = db.query(ProductoDB).filter(
                ProductoDB.en_catalogo == True,
                ProductoDB.estado == "activo"
            ).count()
            
            return total
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener total de catálogo: {str(e)}"
            )

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
                    detail="Producto no encontrado"
                )
            
            return ProductoInventario.from_orm(producto)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener inventario: {str(e)}"
            )
    
    @staticmethod
    async def obtener_catalogo_publico(db: Session, skip: int = 0, limit: int = 10) -> List[ProductoCatalogo]:
        """
        Obtiene todos los productos que están en el catálogo público con paginación
        
        Args:
            db: Sesión de base de datos
            skip: Número de registros a omitir
            limit: Número máximo de registros a devolver
            
        Returns:
            List[ProductoCatalogo]: Lista de productos en catálogo público
        """
        try:
            productos = db.query(ProductoDB).options(
                joinedload(ProductoDB.categoria),
                joinedload(ProductoDB.subcategoria)
            ).filter(
                ProductoDB.en_catalogo == True,
                ProductoDB.estado == "activo"
            ).offset(skip).limit(limit).all()
            
            catalogo_productos = []
            for p in productos:
                # Crear producto de catálogo con valores por defecto si faltan datos
                # Calcular precio final con oferta si aplica
                precio_base = float(p.precio_venta) if p.precio_venta else 0
                precio_final = precio_base
                try:
                    aplica_oferta = bool(getattr(p, 'oferta_activa', False))
                    if aplica_oferta:
                        # Validar rango de fechas
                        inicio_ok = True
                        fin_ok = True
                        if getattr(p, 'fecha_inicio_oferta', None):
                            inicio_ok = datetime.utcnow() >= p.fecha_inicio_oferta
                        if getattr(p, 'fecha_fin_oferta', None):
                            fin_ok = datetime.utcnow() <= p.fecha_fin_oferta
                        if inicio_ok and fin_ok:
                            tipo = getattr(p, 'tipo_oferta', None)
                            valor = float(getattr(p, 'valor_oferta', 0) or 0)
                            if tipo == 'porcentaje' and valor > 0:
                                precio_final = max(0.0, round(precio_base * (1 - valor / 100), 2))
                            elif tipo == 'fijo' and valor > 0:
                                precio_final = max(0.0, round(precio_base - valor, 2))
                except Exception:
                    # En caso de cualquier error, usar precio base
                    precio_final = precio_base
                producto_catalogo = ProductoCatalogo(
                    id_producto=p.id_producto,
                    nombre=p.nombre,
                    descripcion=p.descripcion or "Sin descripción",
                    imagen_url=p.imagen_url or "/images/default-product.jpg",
                    marca=p.marca or "Sin marca",
                    caracteristicas=p.caracteristicas or "Sin características especificadas",
                    precio_venta=precio_base,
                    id_categoria=p.id_categoria,
                    id_subcategoria=p.id_subcategoria,
                    disponible=(p.cantidad_disponible or 0) > 0,
                    fecha_agregado_catalogo=p.fecha_actualizacion,
                    oferta_activa=getattr(p, 'oferta_activa', False),
                    tipo_oferta=getattr(p, 'tipo_oferta', None),
                    valor_oferta=float(getattr(p, 'valor_oferta', 0) or 0),
                    precio_final=precio_final
                )
                catalogo_productos.append(producto_catalogo)
            
            return catalogo_productos
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener catálogo público: {str(e)}"
            )
    
    @staticmethod
    async def agregar_producto_a_catalogo(producto_id: int, datos_catalogo: AgregarACatalogo, db: Session) -> ProductoCatalogo:
        """
        Agrega un producto del inventario al catálogo público
        
        Args:
            producto_id: ID del producto a agregar al catálogo
            datos_catalogo: Datos adicionales para el catálogo
            db: Sesión de base de datos
            
        Returns:
            ProductoCatalogo: Producto agregado al catálogo
        """
        try:
            # Buscar el producto en inventario
            producto = db.query(ProductoDB).options(
                joinedload(ProductoDB.categoria),
                joinedload(ProductoDB.subcategoria)
            ).filter(ProductoDB.id_producto == producto_id).first()
            
            if not producto:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Producto no encontrado en inventario"
                )
            
            # Manejar la imagen
            imagen_url = datos_catalogo.imagen_url
            
            # Si se proporciona imagen_base64, subirla a Cloudinary
            if datos_catalogo.imagen_base64:
                try:
                    # Extraer el contenido base64 (remover el prefijo data:image/...;base64,)
                    if ',' in datos_catalogo.imagen_base64:
                        base64_data = datos_catalogo.imagen_base64.split(',')[1]
                    else:
                        base64_data = datos_catalogo.imagen_base64
                    
                    # Decodificar base64
                    image_data = base64.b64decode(base64_data)
                    
                    # Subir a Cloudinary
                    imagen_url = await upload_image(
                        image_data, 
                        public_id=f"producto_{producto_id}_{uuid.uuid4().hex[:8]}"
                    )
                    
                    if not imagen_url:
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Error al subir imagen a Cloudinary"
                        )
                        
                except Exception as e:
                    print(f"Error al procesar imagen base64: {e}")
                    # Si falla la subida de imagen, continuar sin imagen
                    imagen_url = None
            
            # Actualizar el producto con los datos del catálogo
            producto.descripcion = datos_catalogo.descripcion
            producto.imagen_url = imagen_url
            producto.marca = datos_catalogo.marca
            producto.caracteristicas = datos_catalogo.caracteristicas
            # Campos de oferta al catalogar (opcionales)
            try:
                producto.oferta_activa = bool(getattr(datos_catalogo, 'oferta_activa', False))
                producto.tipo_oferta = getattr(datos_catalogo, 'tipo_oferta', None)
                # valor_oferta puede ser None
                vo = getattr(datos_catalogo, 'valor_oferta', None)
                producto.valor_oferta = float(vo) if vo is not None else None
                # Fechas (pydantic convierte ISO a datetime si viene como string)
                producto.fecha_inicio_oferta = getattr(datos_catalogo, 'fecha_inicio_oferta', None)
                producto.fecha_fin_oferta = getattr(datos_catalogo, 'fecha_fin_oferta', None)
            except Exception:
                # Si algo falla, mantener valores por defecto
                pass
            producto.en_catalogo = True
            
            db.commit()
            db.refresh(producto)
            
            # Crear y retornar el objeto ProductoCatalogo
            # Calcular precio final con oferta si aplica
            precio_base = float(producto.precio_venta) if producto.precio_venta else 0
            precio_final = precio_base
            try:
                aplica_oferta = bool(getattr(producto, 'oferta_activa', False))
                if aplica_oferta:
                    inicio_ok = True
                    fin_ok = True
                    if getattr(producto, 'fecha_inicio_oferta', None):
                        inicio_ok = datetime.utcnow() >= producto.fecha_inicio_oferta
                    if getattr(producto, 'fecha_fin_oferta', None):
                        fin_ok = datetime.utcnow() <= producto.fecha_fin_oferta
                    if inicio_ok and fin_ok:
                        tipo = getattr(producto, 'tipo_oferta', None)
                        valor = float(getattr(producto, 'valor_oferta', 0) or 0)
                        if tipo == 'porcentaje' and valor > 0:
                            precio_final = max(0.0, round(precio_base * (1 - valor / 100), 2))
                        elif tipo == 'fijo' and valor > 0:
                            precio_final = max(0.0, round(precio_base - valor, 2))
            except Exception:
                precio_final = precio_base
            producto_catalogo = ProductoCatalogo(
                id_producto=producto.id_producto,
                nombre=producto.nombre,
                descripcion=producto.descripcion,
                imagen_url=producto.imagen_url,
                marca=producto.marca,
                caracteristicas=producto.caracteristicas,
                precio_venta=precio_base,
                id_categoria=producto.id_categoria,
                id_subcategoria=producto.id_subcategoria,
                disponible=(producto.cantidad_disponible or 0) > 0,
                fecha_agregado_catalogo=producto.fecha_actualizacion,
                oferta_activa=getattr(producto, 'oferta_activa', False),
                tipo_oferta=getattr(producto, 'tipo_oferta', None),
                valor_oferta=float(getattr(producto, 'valor_oferta', 0) or 0),
                precio_final=precio_final
            )
            
            return producto_catalogo
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al agregar producto al catálogo: {str(e)}"
            )

    @staticmethod
    async def quitar_producto_de_catalogo(producto_id: int, db: Session) -> dict:
        """
        Quita un producto del catálogo público (cambia en_catalogo a False)
        
        Args:
            producto_id: ID del producto a quitar del catálogo
            db: Sesión de base de datos
            
        Returns:
            dict: Mensaje de confirmación
        """
        try:
            # Buscar el producto
            producto = db.query(ProductoDB).filter(ProductoDB.id_producto == producto_id).first()
            
            if not producto:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Producto no encontrado"
                )
            
            if not producto.en_catalogo:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El producto no está en el catálogo"
                )
            
            # Cambiar en_catalogo a False y limpiar campos opcionales
            producto.en_catalogo = False
            producto.descripcion = None
            producto.imagen_url = None
            producto.marca = None
            producto.caracteristicas = None
            
            db.commit()
            
            return {"message": "Producto quitado del catálogo exitosamente"}
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al quitar producto del catálogo: {str(e)}"
            )

    @staticmethod
    async def obtener_inventario_por_id_alt(inventario_id: int, db: Session) -> ProductoInventario:
        """
        Obtiene un inventario específico por su ID (método alternativo)
        
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
                cantidad=producto.cantidad_disponible if producto.cantidad_disponible else 0,
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
                producto.cantidad_disponible = inventario_data['cantidad']
            
            db.commit()
            db.refresh(producto)
            
            # Retornar el inventario actualizado
            return await ProductoController.obtener_inventario_por_id_alt(inventario_id, db)
            
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

            # Validar subcategoría si se especifica
            if getattr(producto, 'id_subcategoria', None):
                sub = db.query(SubCategoriaDB).filter(SubCategoriaDB.id_subcategoria == producto.id_subcategoria).first()
                if not sub:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="La subcategoría especificada no existe"
                    )
                # Validar que la subcategoría pertenezca a la categoría seleccionada (si ambas existen)
                if producto.id_categoria and sub.id_categoria != producto.id_categoria:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="La subcategoría no pertenece a la categoría seleccionada"
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
                joinedload(ProductoDB.subcategoria),
                joinedload(ProductoDB.proveedor)
            ).filter(ProductoDB.id_producto == db_producto.id_producto).first()
            
            # Construir manualmente el objeto Producto para manejar las relaciones
            producto_dict = {
                "id_producto": db_producto.id_producto,
                "nombre": db_producto.nombre,
                "descripcion": db_producto.descripcion,
                "codigo_interno": db_producto.codigo_interno,
                "imagen_url": db_producto.imagen_url,
                "id_categoria": db_producto.id_categoria,
                "id_proveedor": db_producto.id_proveedor,
                "id_subcategoria": db_producto.id_subcategoria,
                "marca": db_producto.marca,
                "costo_bruto": float(db_producto.costo_bruto) if db_producto.costo_bruto else 0,
                "costo_neto": float(db_producto.costo_neto) if db_producto.costo_neto else 0,
                "precio_venta": float(db_producto.precio_venta) if db_producto.precio_venta else 0,
                "porcentaje_utilidad": float(db_producto.porcentaje_utilidad) if db_producto.porcentaje_utilidad else 0,
                "utilidad_pesos": float(db_producto.utilidad_pesos) if db_producto.utilidad_pesos else 0,
                "cantidad_disponible": db_producto.cantidad_disponible,
                "stock_minimo": db_producto.stock_minimo,
                "estado": db_producto.estado,
                "en_catalogo": db_producto.en_catalogo,
                "caracteristicas": db_producto.caracteristicas,
                "fecha_creacion": db_producto.fecha_creacion,
                "fecha_actualizacion": db_producto.fecha_actualizacion,
                "fecha_ultima_venta": db_producto.fecha_ultima_venta,
                "fecha_ultimo_ingreso": db_producto.fecha_ultimo_ingreso,
                "categoria": db_producto.categoria.nombre if db_producto.categoria else None,
                "proveedor": db_producto.proveedor.nombre if db_producto.proveedor else None,
                "subcategoria": db_producto.subcategoria.nombre if db_producto.subcategoria else None
            }
            
            return Producto(**producto_dict)
            
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
                joinedload(ProductoDB.subcategoria),
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
                    "id_subcategoria": p.id_subcategoria,
                    "marca": p.marca,
                    "costo_bruto": float(p.costo_bruto) if p.costo_bruto else 0,
                    "costo_neto": float(p.costo_neto) if p.costo_neto else 0,
                    "precio_venta": float(p.precio_venta) if p.precio_venta else 0,
                    "porcentaje_utilidad": float(p.porcentaje_utilidad) if p.porcentaje_utilidad else 0,
                    "utilidad_pesos": float(p.utilidad_pesos) if p.utilidad_pesos else 0,
                    "cantidad_disponible": p.cantidad_disponible,
                    "stock_minimo": p.stock_minimo,
                    "estado": p.estado,
                    "fecha_creacion": p.fecha_creacion,
                    "fecha_actualizacion": p.fecha_actualizacion,
                    "fecha_ultima_venta": p.fecha_ultima_venta,
                    "fecha_ultimo_ingreso": p.fecha_ultimo_ingreso,
                    "categoria": p.categoria.nombre if p.categoria else None,
                    "proveedor": p.proveedor.nombre if p.proveedor else None,
                    "subcategoria": p.subcategoria.nombre if p.subcategoria else None
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
                joinedload(ProductoDB.subcategoria),
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
            subcategoria_nombre = None
            
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

            # Obtener nombre de subcategoría si existe
            if hasattr(producto, 'subcategoria') and producto.subcategoria:
                subcategoria_nombre = producto.subcategoria.nombre
            elif getattr(producto, 'id_subcategoria', None):
                sub = db.query(SubCategoriaDB).filter(SubCategoriaDB.id_subcategoria == producto.id_subcategoria).first()
                if sub:
                    subcategoria_nombre = sub.nombre
            
            producto_dict = {
                "id_producto": producto.id_producto,
                "nombre": producto.nombre,
                "descripcion": producto.descripcion,
                "codigo_interno": producto.codigo_interno,
                "imagen_url": producto.imagen_url,
                "id_categoria": producto.id_categoria,
                "id_proveedor": producto.id_proveedor,
                "id_subcategoria": getattr(producto, 'id_subcategoria', None),
                "marca": producto.marca,
                "costo_bruto": float(producto.costo_bruto) if producto.costo_bruto else 0,
                "costo_neto": float(producto.costo_neto) if producto.costo_neto else 0,
                "precio_venta": float(producto.precio_venta) if producto.precio_venta else 0,
                "porcentaje_utilidad": float(producto.porcentaje_utilidad) if producto.porcentaje_utilidad else 0,
                "utilidad_pesos": float(producto.utilidad_pesos) if producto.utilidad_pesos else 0,
                "cantidad_disponible": producto.cantidad_disponible,
                "stock_minimo": producto.stock_minimo,
                "estado": producto.estado,
                "fecha_creacion": producto.fecha_creacion,
                "fecha_actualizacion": producto.fecha_actualizacion,
                "fecha_ultima_venta": producto.fecha_ultima_venta,
                "fecha_ultimo_ingreso": producto.fecha_ultimo_ingreso,
                "categoria": categoria_nombre,
                "proveedor": proveedor_nombre,
                "subcategoria": subcategoria_nombre
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

            if getattr(producto_update, 'id_subcategoria', None) is not None:
                if producto_update.id_subcategoria is None:
                    pass  # permitir limpiar subcategoría
                else:
                    sub = db.query(SubCategoriaDB).filter(SubCategoriaDB.id_subcategoria == producto_update.id_subcategoria).first()
                    if not sub:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="La subcategoría especificada no existe"
                        )
                    # Si se actualiza categoría también, validar consistencia; si no, validar con categoría actual
                    categoria_id_ref = producto_update.id_categoria if producto_update.id_categoria is not None else producto.id_categoria
                    if categoria_id_ref and sub.id_categoria != categoria_id_ref:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="La subcategoría no pertenece a la categoría seleccionada"
                        )
            
            # Actualizar campos
            for field, value in producto_update.dict(exclude_unset=True).items():
                setattr(producto, field, value)
            
            db.commit()
            db.refresh(producto)
            
            # Cargar relaciones
            producto = db.query(ProductoDB).options(
                joinedload(ProductoDB.categoria),
                joinedload(ProductoDB.subcategoria),
                joinedload(ProductoDB.proveedor)
            ).filter(ProductoDB.id_producto == producto_id).first()
            
            # Manejar categoria y proveedor manualmente para evitar errores de serialización
            categoria_nombre = None
            proveedor_nombre = None
            subcategoria_nombre = None
            
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

            # Resolver nombre de subcategoría si existe
            if hasattr(producto, 'subcategoria') and producto.subcategoria:
                subcategoria_nombre = producto.subcategoria.nombre
            elif getattr(producto, 'id_subcategoria', None):
                sub = db.query(SubCategoriaDB).filter(SubCategoriaDB.id_subcategoria == producto.id_subcategoria).first()
                if sub:
                    subcategoria_nombre = sub.nombre
            
            # Construir el objeto Producto manualmente (usando el modelo unificado)
            return Producto(
                id_producto=producto.id_producto,
                nombre=producto.nombre,
                descripcion=producto.descripcion,
                codigo_interno=producto.codigo_interno,
                imagen_url=producto.imagen_url,
                id_categoria=producto.id_categoria,
                id_proveedor=producto.id_proveedor,
                id_subcategoria=getattr(producto, 'id_subcategoria', None),
                marca=producto.marca,
                costo_bruto=float(producto.costo_bruto) if producto.costo_bruto else 0,
                costo_neto=float(producto.costo_neto) if producto.costo_neto else 0,
                precio_venta=float(producto.precio_venta) if producto.precio_venta else 0,
                porcentaje_utilidad=float(producto.porcentaje_utilidad) if producto.porcentaje_utilidad else 0,
                utilidad_pesos=float(producto.utilidad_pesos) if producto.utilidad_pesos else 0,
                cantidad_disponible=producto.cantidad_disponible,
                stock_minimo=producto.stock_minimo,
                estado=producto.estado,
                en_catalogo=getattr(producto, 'en_catalogo', False),
                caracteristicas=getattr(producto, 'caracteristicas', None),
                fecha_creacion=producto.fecha_creacion,
                fecha_actualizacion=producto.fecha_actualizacion,
                fecha_ultima_venta=getattr(producto, 'fecha_ultima_venta', None),
                fecha_ultimo_ingreso=getattr(producto, 'fecha_ultimo_ingreso', None),
                categoria=categoria_nombre,
                proveedor=proveedor_nombre,
                subcategoria=subcategoria_nombre
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
            campos_inventario = ['cantidad_disponible', 'stock_minimo']
            
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
    async def obtener_inventario(db: Session, skip: int = 0, limit: int = 10) -> List[ProductoInventario]:
        """
        Obtiene productos en formato de inventario que NO están catalogados con paginación
        
        Args:
            db: Sesión de base de datos
            skip: Número de registros a omitir
            limit: Número máximo de registros a devolver
            
        Returns:
            List[ProductoInventario]: Lista de productos en formato inventario (solo no catalogados)
        """
        try:
            # Filtrar solo productos que NO están en catálogo (en_catalogo = False o NULL)
            productos = db.query(ProductoDB).options(
                joinedload(ProductoDB.categoria),
                joinedload(ProductoDB.proveedor)
            ).filter(
                or_(ProductoDB.en_catalogo == False, ProductoDB.en_catalogo.is_(None))
            ).offset(skip).limit(limit).all()
            
            inventario_list = []
            for p in productos:
                inventario_item = ProductoInventario(
                    id_inventario=p.id_producto,  # Usar id_producto como id_inventario
                    id_producto=p.id_producto,
                    precio=float(p.precio_venta) if p.precio_venta else 0.0,
                    cantidad=p.cantidad_disponible if p.cantidad_disponible else 0,
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
    async def obtener_total_inventario(db: Session) -> int:
        """
        Obtiene el total de productos en inventario que NO están catalogados
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            int: Total de productos en inventario
        """
        try:
            total = db.query(ProductoDB).filter(
                or_(ProductoDB.en_catalogo == False, ProductoDB.en_catalogo.is_(None))
            ).count()
            
            return total
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener total de inventario: {str(e)}"
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
            total_cantidad_disponible = sum(p.cantidad_disponible or 0 for p in productos)
            
            return {
                "total_productos": total_productos,
                "productos_bajo_stock": productos_bajo_stock,
                "productos_sin_stock": productos_sin_stock,
                "productos_con_stock": total_productos - productos_sin_stock,
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

    @staticmethod
    async def actualizar_producto_catalogado(producto_id: int, datos_actualizacion: dict, db: Session) -> dict:
        """
        Actualiza un producto que ya está en el catálogo
        
        Args:
            producto_id: ID del producto a actualizar
            datos_actualizacion: Datos a actualizar (nombre, descripcion, caracteristicas, marca, imagen_base64)
            db: Sesión de base de datos
            
        Returns:
            dict: Mensaje de confirmación
        """
        try:
            # Buscar el producto
            producto = db.query(ProductoDB).filter(ProductoDB.id_producto == producto_id).first()
            
            if not producto:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Producto no encontrado"
                )
            
            if not producto.en_catalogo:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El producto no está en el catálogo"
                )
            
            # Actualizar solo los campos permitidos para productos catalogados
            if 'nombre' in datos_actualizacion:
                producto.nombre = datos_actualizacion['nombre']
            if 'marca' in datos_actualizacion:
                producto.marca = datos_actualizacion['marca']
            if 'descripcion' in datos_actualizacion:
                producto.descripcion = datos_actualizacion['descripcion']
            if 'caracteristicas' in datos_actualizacion:
                producto.caracteristicas = datos_actualizacion['caracteristicas']
            # Campos de oferta
            if 'oferta_activa' in datos_actualizacion:
                producto.oferta_activa = bool(datos_actualizacion['oferta_activa'])
            if 'tipo_oferta' in datos_actualizacion:
                producto.tipo_oferta = datos_actualizacion['tipo_oferta']
            if 'valor_oferta' in datos_actualizacion:
                try:
                    producto.valor_oferta = float(datos_actualizacion['valor_oferta'])
                except Exception:
                    producto.valor_oferta = None
            if 'fecha_inicio_oferta' in datos_actualizacion:
                try:
                    # Aceptar ISO string
                    from datetime import datetime as _dt
                    producto.fecha_inicio_oferta = _dt.fromisoformat(datos_actualizacion['fecha_inicio_oferta']) if datos_actualizacion['fecha_inicio_oferta'] else None
                except Exception:
                    producto.fecha_inicio_oferta = None
            if 'fecha_fin_oferta' in datos_actualizacion:
                try:
                    from datetime import datetime as _dt
                    producto.fecha_fin_oferta = _dt.fromisoformat(datos_actualizacion['fecha_fin_oferta']) if datos_actualizacion['fecha_fin_oferta'] else None
                except Exception:
                    producto.fecha_fin_oferta = None
            
            # Manejar imagen si se proporciona
            if 'imagen_base64' in datos_actualizacion and datos_actualizacion['imagen_base64']:
                try:
                    # Subir imagen a Cloudinary
                    imagen_url = await upload_image(datos_actualizacion['imagen_base64'])
                    producto.imagen_url = imagen_url
                    print(f"Imagen actualizada para producto {producto_id}: {imagen_url}")
                except Exception as img_error:
                    print(f"Error al subir imagen: {str(img_error)}")
                    # No fallar la actualización si solo falla la imagen
                    pass
            
            db.commit()
            
            return {"message": "Producto catalogado actualizado exitosamente"}
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al actualizar producto catalogado: {str(e)}"
            )