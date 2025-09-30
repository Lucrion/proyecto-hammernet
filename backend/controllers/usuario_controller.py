#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Controlador de usuarios
Maneja todas las operaciones CRUD de usuarios
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from models.usuario import UsuarioDB, UsuarioCreate, UsuarioUpdate, Usuario
from auth import hash_contraseña


class UsuarioController:
    """Controlador para manejo de usuarios"""
    
    @staticmethod
    async def crear_usuario(usuario: UsuarioCreate, db: Session) -> Usuario:
        """
        Crea un nuevo usuario
        
        Args:
            usuario: Datos del usuario a crear
            db: Sesión de base de datos
            
        Returns:
            Usuario: Usuario creado
            
        Raises:
            HTTPException: Si hay error en la creación
        """
        try:
            # Hash de la contraseña
            hashed_password = hash_contraseña(usuario.password)
            
            # Crear usuario en BD
            db_usuario = UsuarioDB(
                nombre=usuario.nombre,
                username=usuario.username,
                password=hashed_password,
                role=usuario.role
            )
            
            db.add(db_usuario)
            db.commit()
            db.refresh(db_usuario)
            
            return Usuario(
                id_usuario=db_usuario.id_usuario,
                nombre=db_usuario.nombre,
                username=db_usuario.username,
                role=db_usuario.role,
                fecha_creacion=db_usuario.fecha_creacion.isoformat() if db_usuario.fecha_creacion else None
            )
            
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya existe"
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear usuario: {str(e)}"
            )
    
    @staticmethod
    async def obtener_usuarios(db: Session) -> List[Usuario]:
        """
        Obtiene todos los usuarios
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            List[Usuario]: Lista de usuarios
        """
        try:
            usuarios = db.query(UsuarioDB).all()
            return [
                Usuario(
                    id_usuario=u.id_usuario,
                    nombre=u.nombre,
                    username=u.username,
                    role=u.role,
                    fecha_creacion=u.fecha_creacion.isoformat() if u.fecha_creacion else None
                ) for u in usuarios
            ]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener usuarios: {str(e)}"
            )
    
    @staticmethod
    async def obtener_usuario(usuario_id: int, db: Session) -> Usuario:
        """
        Obtiene un usuario por ID
        
        Args:
            usuario_id: ID del usuario
            db: Sesión de base de datos
            
        Returns:
            Usuario: Usuario encontrado
            
        Raises:
            HTTPException: Si el usuario no existe
        """
        try:
            usuario = db.query(UsuarioDB).filter(UsuarioDB.id_usuario == usuario_id).first()
            if not usuario:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )
            
            return Usuario(
                id_usuario=usuario.id_usuario,
                nombre=usuario.nombre,
                username=usuario.username,
                role=usuario.role,
                fecha_creacion=usuario.fecha_creacion.isoformat() if usuario.fecha_creacion else None
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener usuario: {str(e)}"
            )
    
    @staticmethod
    async def actualizar_usuario(usuario_id: int, usuario_update: UsuarioUpdate, db: Session) -> Usuario:
        """
        Actualiza un usuario
        
        Args:
            usuario_id: ID del usuario
            usuario_update: Datos a actualizar
            db: Sesión de base de datos
            
        Returns:
            Usuario: Usuario actualizado
            
        Raises:
            HTTPException: Si el usuario no existe o hay error
        """
        try:
            usuario = db.query(UsuarioDB).filter(UsuarioDB.id_usuario == usuario_id).first()
            if not usuario:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )
            
            # Actualizar campos
            if usuario_update.nombre is not None:
                usuario.nombre = usuario_update.nombre
            if usuario_update.username is not None:
                usuario.username = usuario_update.username
            if usuario_update.password is not None:
                usuario.password = hash_contraseña(usuario_update.password)
            if usuario_update.role is not None:
                usuario.role = usuario_update.role
            
            db.commit()
            db.refresh(usuario)
            
            return Usuario(
                id_usuario=usuario.id_usuario,
                nombre=usuario.nombre,
                username=usuario.username,
                role=usuario.role,
                fecha_creacion=usuario.fecha_creacion.isoformat() if usuario.fecha_creacion else None
            )
            
        except HTTPException:
            raise
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya existe"
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al actualizar usuario: {str(e)}"
            )
    
    @staticmethod
    async def eliminar_usuario(usuario_id: int, db: Session) -> dict:
        """
        Elimina un usuario
        
        Args:
            usuario_id: ID del usuario
            db: Sesión de base de datos
            
        Returns:
            dict: Mensaje de confirmación
            
        Raises:
            HTTPException: Si el usuario no existe o hay error
        """
        try:
            usuario = db.query(UsuarioDB).filter(UsuarioDB.id_usuario == usuario_id).first()
            if not usuario:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )
            
            db.delete(usuario)
            db.commit()
            
            return {"message": "Usuario eliminado exitosamente"}
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al eliminar usuario: {str(e)}"
            )