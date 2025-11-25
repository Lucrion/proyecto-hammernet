#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Controlador de categorías
Maneja todas las operaciones CRUD de categorías
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from models.categoria import CategoriaDB, CategoriaCreate, CategoriaUpdate, Categoria
from models.producto import ProductoDB


class CategoriaController:
    """Controlador para manejo de categorías"""
    
    @staticmethod
    async def crear_categoria(categoria: CategoriaCreate, db: Session) -> Categoria:
        """
        Crea una nueva categoría
        
        Args:
            categoria: Datos de la categoría a crear
            db: Sesión de base de datos
            
        Returns:
            Categoria: Categoría creada
            
        Raises:
            HTTPException: Si hay error en la creación
        """
        try:
            db_categoria = CategoriaDB(**categoria.dict())
            db.add(db_categoria)
            db.commit()
            db.refresh(db_categoria)
            
            return Categoria(
                id_categoria=db_categoria.id_categoria,
                nombre=db_categoria.nombre,
                descripcion=db_categoria.descripcion
            )
            
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una categoría con ese nombre"
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear categoría: {str(e)}"
            )
    
    @staticmethod
    async def obtener_categorias(db: Session) -> List[Categoria]:
        """
        Obtiene todas las categorías
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            List[Categoria]: Lista de categorías
        """
        try:
            categorias = db.query(CategoriaDB).all()
            return [
                Categoria(
                    id_categoria=c.id_categoria,
                    nombre=c.nombre,
                    descripcion=c.descripcion
                ) for c in categorias
            ]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener categorías: {str(e)}"
            )
    
    @staticmethod
    async def obtener_categoria(categoria_id: int, db: Session) -> Categoria:
        """
        Obtiene una categoría por ID
        
        Args:
            categoria_id: ID de la categoría
            db: Sesión de base de datos
            
        Returns:
            Categoria: Categoría encontrada
            
        Raises:
            HTTPException: Si la categoría no existe
        """
        try:
            categoria = db.query(CategoriaDB).filter(CategoriaDB.id_categoria == categoria_id).first()
            if not categoria:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Categoría no encontrada"
                )
            
            return Categoria(
                id_categoria=categoria.id_categoria,
                nombre=categoria.nombre,
                descripcion=categoria.descripcion
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener categoría: {str(e)}"
            )
    
    @staticmethod
    async def actualizar_categoria(categoria_id: int, categoria_update: CategoriaUpdate, db: Session) -> Categoria:
        """
        Actualiza una categoría
        
        Args:
            categoria_id: ID de la categoría
            categoria_update: Datos a actualizar
            db: Sesión de base de datos
            
        Returns:
            Categoria: Categoría actualizada
            
        Raises:
            HTTPException: Si la categoría no existe o hay error
        """
        try:
            categoria = db.query(CategoriaDB).filter(CategoriaDB.id_categoria == categoria_id).first()
            if not categoria:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Categoría no encontrada"
                )
            
            # Actualizar campos
            if categoria_update.nombre is not None:
                categoria.nombre = categoria_update.nombre
            if categoria_update.descripcion is not None:
                categoria.descripcion = categoria_update.descripcion
            
            db.commit()
            db.refresh(categoria)
            
            return Categoria(
                id_categoria=categoria.id_categoria,
                nombre=categoria.nombre,
                descripcion=categoria.descripcion
            )
            
        except HTTPException:
            raise
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una categoría con ese nombre"
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al actualizar categoría: {str(e)}"
            )
    
    @staticmethod
    async def eliminar_categoria(categoria_id: int, db: Session) -> dict:
        """
        Elimina una categoría
        
        Args:
            categoria_id: ID de la categoría
            db: Sesión de base de datos
            
        Returns:
            dict: Mensaje de confirmación
            
        Raises:
            HTTPException: Si la categoría no existe o hay error
        """
        try:
            categoria = db.query(CategoriaDB).filter(CategoriaDB.id_categoria == categoria_id).first()
            if not categoria:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Categoría no encontrada"
                )
            # Bloquear eliminación si hay productos asociados
            productos_asociados = db.query(ProductoDB).filter(ProductoDB.id_categoria == categoria_id).count()
            if productos_asociados > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No se puede eliminar la categoría porque tiene productos asociados"
                )
            
            db.delete(categoria)
            db.commit()
            
            return {"message": "Categoría eliminada exitosamente"}
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al eliminar categoría: {str(e)}"
            )
