#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Controlador de proveedores
Maneja todas las operaciones CRUD de proveedores
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from models.proveedor import ProveedorDB, ProveedorCreate, ProveedorUpdate, Proveedor


class ProveedorController:
    """Controlador para manejo de proveedores"""
    
    @staticmethod
    async def crear_proveedor(proveedor: ProveedorCreate, db: Session) -> Proveedor:
        """
        Crea un nuevo proveedor
        
        Args:
            proveedor: Datos del proveedor a crear
            db: Sesión de base de datos
            
        Returns:
            Proveedor: Proveedor creado
            
        Raises:
            HTTPException: Si hay error en la creación
        """
        try:
            db_proveedor = ProveedorDB(**proveedor.dict())
            db.add(db_proveedor)
            db.commit()
            db.refresh(db_proveedor)
            
            return Proveedor(
                id_proveedor=db_proveedor.id_proveedor,
                nombre=db_proveedor.nombre,
                contacto=db_proveedor.contacto,
                telefono=db_proveedor.telefono,
                email=db_proveedor.email,
                direccion=db_proveedor.direccion
            )
            
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un proveedor con ese nombre o email"
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear proveedor: {str(e)}"
            )
    
    @staticmethod
    async def obtener_proveedores(db: Session) -> List[Proveedor]:
        """
        Obtiene todos los proveedores
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            List[Proveedor]: Lista de proveedores
        """
        try:
            proveedores = db.query(ProveedorDB).all()
            return [
                Proveedor(
                    id_proveedor=p.id_proveedor,
                    nombre=p.nombre,
                    contacto=p.contacto,
                    telefono=p.telefono,
                    email=p.email,
                    direccion=p.direccion
                ) for p in proveedores
            ]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener proveedores: {str(e)}"
            )
    
    @staticmethod
    async def obtener_proveedor(proveedor_id: int, db: Session) -> Proveedor:
        """
        Obtiene un proveedor por ID
        
        Args:
            proveedor_id: ID del proveedor
            db: Sesión de base de datos
            
        Returns:
            Proveedor: Proveedor encontrado
            
        Raises:
            HTTPException: Si el proveedor no existe
        """
        try:
            proveedor = db.query(ProveedorDB).filter(ProveedorDB.id_proveedor == proveedor_id).first()
            if not proveedor:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Proveedor no encontrado"
                )
            
            return Proveedor(
                id_proveedor=proveedor.id_proveedor,
                nombre=proveedor.nombre,
                contacto=proveedor.contacto,
                telefono=proveedor.telefono,
                email=proveedor.email,
                direccion=proveedor.direccion
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener proveedor: {str(e)}"
            )
    
    @staticmethod
    async def actualizar_proveedor(proveedor_id: int, proveedor_update: ProveedorUpdate, db: Session) -> Proveedor:
        """
        Actualiza un proveedor
        
        Args:
            proveedor_id: ID del proveedor
            proveedor_update: Datos a actualizar
            db: Sesión de base de datos
            
        Returns:
            Proveedor: Proveedor actualizado
            
        Raises:
            HTTPException: Si el proveedor no existe o hay error
        """
        try:
            proveedor = db.query(ProveedorDB).filter(ProveedorDB.id_proveedor == proveedor_id).first()
            if not proveedor:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Proveedor no encontrado"
                )
            
            # Actualizar campos
            if proveedor_update.nombre is not None:
                proveedor.nombre = proveedor_update.nombre
            if proveedor_update.contacto is not None:
                proveedor.contacto = proveedor_update.contacto
            if proveedor_update.telefono is not None:
                proveedor.telefono = proveedor_update.telefono
            if proveedor_update.email is not None:
                proveedor.email = proveedor_update.email
            if proveedor_update.direccion is not None:
                proveedor.direccion = proveedor_update.direccion
            
            db.commit()
            db.refresh(proveedor)
            
            return Proveedor(
                id_proveedor=proveedor.id_proveedor,
                nombre=proveedor.nombre,
                contacto=proveedor.contacto,
                telefono=proveedor.telefono,
                email=proveedor.email,
                direccion=proveedor.direccion
            )
            
        except HTTPException:
            raise
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un proveedor con ese nombre o email"
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al actualizar proveedor: {str(e)}"
            )
    
    @staticmethod
    async def eliminar_proveedor(proveedor_id: int, db: Session) -> dict:
        """
        Elimina un proveedor
        
        Args:
            proveedor_id: ID del proveedor
            db: Sesión de base de datos
            
        Returns:
            dict: Mensaje de confirmación
            
        Raises:
            HTTPException: Si el proveedor no existe o hay error
        """
        try:
            proveedor = db.query(ProveedorDB).filter(ProveedorDB.id_proveedor == proveedor_id).first()
            if not proveedor:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Proveedor no encontrado"
                )
            
            db.delete(proveedor)
            db.commit()
            
            return {"message": "Proveedor eliminado exitosamente"}
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al eliminar proveedor: {str(e)}"
            )