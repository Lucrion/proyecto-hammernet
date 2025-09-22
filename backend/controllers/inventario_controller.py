#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Controlador de inventario
Maneja todas las operaciones CRUD de inventario y funcionalidades específicas
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from models.inventario import InventarioDB, InventarioCreate, InventarioUpdate, Inventario
from models.producto import ProductoDB


class InventarioController:
    """Controlador para manejo de inventario"""
    
    @staticmethod
    async def crear_inventario(inventario: InventarioCreate, db: Session) -> Inventario:
        """
        Crea un nuevo registro de inventario
        
        Args:
            inventario: Datos del inventario a crear
            db: Sesión de base de datos
            
        Returns:
            Inventario: Inventario creado
            
        Raises:
            HTTPException: Si hay error en la creación
        """
        try:
            # Verificar que exista el producto
            producto = db.query(ProductoDB).filter(ProductoDB.id_producto == inventario.id_producto).first()
            if not producto:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El producto especificado no existe"
                )
            
            db_inventario = InventarioDB(**inventario.dict())
            db.add(db_inventario)
            db.commit()
            db.refresh(db_inventario)
            
            # Cargar relaciones
            db_inventario = db.query(InventarioDB).options(
                joinedload(InventarioDB.producto)
            ).filter(InventarioDB.id_inventario == db_inventario.id_inventario).first()
            
            return Inventario(
                id_inventario=db_inventario.id_inventario,
                id_producto=db_inventario.id_producto,
                precio=db_inventario.precio,
                cantidad=db_inventario.cantidad,
                fecha_registro=db_inventario.fecha_registro.isoformat() if db_inventario.fecha_registro else None,
                producto={
                    "id_producto": db_inventario.producto.id_producto,
                    "nombre": db_inventario.producto.nombre,
                    "codigo_interno": db_inventario.producto.codigo_interno
                } if db_inventario.producto else None
            )
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear inventario: {str(e)}"
            )
    
    @staticmethod
    async def obtener_inventarios(db: Session, producto_id: Optional[int] = None) -> List[Inventario]:
        """
        Obtiene todos los registros de inventario o filtrados por producto
        
        Args:
            db: Sesión de base de datos
            producto_id: ID de producto para filtrar (opcional)
            
        Returns:
            List[Inventario]: Lista de inventarios
        """
        try:
            query = db.query(InventarioDB).options(
                joinedload(InventarioDB.producto)
            )
            
            if producto_id:
                query = query.filter(InventarioDB.id_producto == producto_id)
            
            inventarios = query.all()
            
            return [
                Inventario(
                    id_inventario=i.id_inventario,
                    id_producto=i.id_producto,
                    precio=i.precio,
                    cantidad=i.cantidad,
                    fecha_registro=i.fecha_registro.isoformat() if i.fecha_registro else None,
                    producto={
                        "id_producto": i.producto.id_producto,
                        "nombre": i.producto.nombre,
                        "codigo_interno": i.producto.codigo_interno,
                        "imagen_url": i.producto.imagen_url
                    } if i.producto else None
                ) for i in inventarios
            ]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener inventarios: {str(e)}"
            )
    
    @staticmethod
    async def obtener_inventario(inventario_id: int, db: Session) -> Inventario:
        """
        Obtiene un registro de inventario por ID
        
        Args:
            inventario_id: ID del inventario
            db: Sesión de base de datos
            
        Returns:
            Inventario: Inventario encontrado
            
        Raises:
            HTTPException: Si el inventario no existe
        """
        try:
            inventario = db.query(InventarioDB).options(
                joinedload(InventarioDB.producto)
            ).filter(InventarioDB.id_inventario == inventario_id).first()
            
            if not inventario:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Inventario no encontrado"
                )
            
            return Inventario(
                id_inventario=inventario.id_inventario,
                id_producto=inventario.id_producto,
                precio=inventario.precio,
                cantidad=inventario.cantidad,
                fecha_registro=inventario.fecha_registro.isoformat() if inventario.fecha_registro else None,
                producto={
                    "id_producto": inventario.producto.id_producto,
                    "nombre": inventario.producto.nombre,
                    "codigo_interno": inventario.producto.codigo_interno,
                    "imagen_url": inventario.producto.imagen_url
                } if inventario.producto else None
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener inventario: {str(e)}"
            )
    
    @staticmethod
    async def actualizar_inventario(inventario_id: int, inventario_update: InventarioUpdate, db: Session) -> Inventario:
        """
        Actualiza un registro de inventario
        
        Args:
            inventario_id: ID del inventario
            inventario_update: Datos a actualizar
            db: Sesión de base de datos
            
        Returns:
            Inventario: Inventario actualizado
            
        Raises:
            HTTPException: Si el inventario no existe o hay error
        """
        try:
            inventario = db.query(InventarioDB).filter(InventarioDB.id_inventario == inventario_id).first()
            if not inventario:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Inventario no encontrado"
                )
            
            # Actualizar campos
            for field, value in inventario_update.dict(exclude_unset=True).items():
                setattr(inventario, field, value)
            
            db.commit()
            db.refresh(inventario)
            
            # Cargar relaciones
            inventario = db.query(InventarioDB).options(
                joinedload(InventarioDB.producto)
            ).filter(InventarioDB.id_inventario == inventario_id).first()
            
            return Inventario(
                id_inventario=inventario.id_inventario,
                id_producto=inventario.id_producto,
                precio=inventario.precio,
                cantidad=inventario.cantidad,
                fecha_registro=inventario.fecha_registro.isoformat() if inventario.fecha_registro else None,
                producto={
                    "id_producto": inventario.producto.id_producto,
                    "nombre": inventario.producto.nombre,
                    "codigo_interno": inventario.producto.codigo_interno,
                    "imagen_url": inventario.producto.imagen_url
                } if inventario.producto else None
            )
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al actualizar inventario: {str(e)}"
            )
    
    @staticmethod
    async def eliminar_inventario(inventario_id: int, db: Session) -> dict:
        """
        Elimina un registro de inventario
        
        Args:
            inventario_id: ID del inventario
            db: Sesión de base de datos
            
        Returns:
            dict: Mensaje de confirmación
            
        Raises:
            HTTPException: Si el inventario no existe o hay error
        """
        try:
            inventario = db.query(InventarioDB).filter(InventarioDB.id_inventario == inventario_id).first()
            if not inventario:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Inventario no encontrado"
                )
            
            db.delete(inventario)
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
    async def obtener_resumen_inventario(db: Session) -> dict:
        """
        Obtiene un resumen del inventario
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            dict: Resumen del inventario
        """
        try:
            from sqlalchemy import func
            
            # Estadísticas básicas
            total_productos = db.query(func.count(InventarioDB.id_inventario.distinct())).scalar()
            total_cantidad = db.query(func.sum(InventarioDB.cantidad)).scalar() or 0
            valor_total = db.query(func.sum(InventarioDB.precio * InventarioDB.cantidad)).scalar() or 0
            
            # Productos con bajo stock (menos de 10 unidades)
            productos_bajo_stock = db.query(InventarioDB).options(
                joinedload(InventarioDB.producto)
            ).filter(InventarioDB.cantidad < 10).all()
            
            return {
                "total_productos": total_productos,
                "total_cantidad": total_cantidad,
                "valor_total": valor_total,
                "productos_bajo_stock": [
                    {
                        "id_inventario": p.id_inventario,
                        "producto": p.producto.nombre if p.producto else "N/A",
                        "cantidad": p.cantidad,
                        "precio": p.precio
                    } for p in productos_bajo_stock
                ]
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener resumen de inventario: {str(e)}"
            )