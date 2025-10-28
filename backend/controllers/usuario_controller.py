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
from core.auth import hash_contraseña


def _normalizar_rut(rut: str) -> str:
    """Normaliza un RUT: elimina puntos, espacios y deja el guion si existe"""
    if not rut:
        return rut
    rut = rut.strip().upper()
    rut = rut.replace('.', '').replace(' ', '')
    return rut


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
            # Validar confirmación de contraseña si se envía
            if usuario.confirm_password is not None and usuario.password != usuario.confirm_password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La confirmación de contraseña no coincide"
                )

            # Normalizar RUT y usarlo como username (login por RUT)
            rut_norm = _normalizar_rut(usuario.rut or usuario.username)
            if not rut_norm:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Debe proporcionar el RUT"
                )

            # Hash de la contraseña
            hashed_password = hash_contraseña(usuario.password)
            
            # Crear usuario en BD
            db_usuario = UsuarioDB(
                nombre=usuario.nombre,
                apellido=usuario.apellido,
                username=rut_norm,  # compatibilidad con OAuth2PasswordRequestForm
                rut=rut_norm,
                email=usuario.email,
                telefono=usuario.telefono,
                password=hashed_password,
                role=usuario.role
            )
            
            db.add(db_usuario)
            db.commit()
            db.refresh(db_usuario)
            
            return Usuario(
                id_usuario=db_usuario.id_usuario,
                nombre=db_usuario.nombre,
                apellido=db_usuario.apellido,
                username=db_usuario.username,
                rut=db_usuario.rut,
                email=db_usuario.email,
                telefono=db_usuario.telefono,
                role=db_usuario.role,
                activo=db_usuario.activo,
                fecha_creacion=db_usuario.fecha_creacion.isoformat() if db_usuario.fecha_creacion else None
            )
            
        except IntegrityError as ie:
            db.rollback()
            # Mensaje más específico según restricción
            msg = "El usuario ya existe"
            if 'username' in str(ie.orig).lower():
                msg = "El RUT/usuario ya está registrado"
            if 'rut' in str(ie.orig).lower():
                msg = "El RUT ya está registrado"
            if 'email' in str(ie.orig).lower():
                msg = "El correo ya está registrado"
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=msg
            )
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear usuario: {str(e)}"
            )
    
    @staticmethod
    async def crear_usuario_google(nombre: str, username: str, email: str, password: str, role: str, db: Session) -> Usuario:
        """
        Crea un nuevo usuario desde Google OAuth
        
        Args:
            nombre: Nombre del usuario
            username: Username único
            email: Email del usuario
            password: Contraseña temporal
            role: Rol del usuario
            db: Sesión de base de datos
            
        Returns:
            Usuario: Usuario creado
            
        Raises:
            HTTPException: Si hay error en la creación
        """
        try:
            # Hash de la contraseña
            hashed_password = hash_contraseña(password)
            
            # Crear usuario en BD
            db_usuario = UsuarioDB(
                nombre=nombre,
                username=username,
                email=email,
                password=hashed_password,
                role=role,
                activo=True
            )
            
            db.add(db_usuario)
            db.commit()
            db.refresh(db_usuario)
            
            return Usuario(
                id_usuario=db_usuario.id_usuario,
                nombre=db_usuario.nombre,
                apellido=db_usuario.apellido,
                username=db_usuario.username,
                rut=db_usuario.rut,
                email=db_usuario.email,
                telefono=db_usuario.telefono,
                role=db_usuario.role,
                activo=db_usuario.activo,
                fecha_creacion=db_usuario.fecha_creacion.isoformat() if db_usuario.fecha_creacion else None
            )
            
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El usuario ya existe"
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear usuario desde Google: {str(e)}"
            )
    
    @staticmethod
    async def obtener_usuarios(db: Session) -> List[Usuario]:
        """
        Obtiene todos los usuarios activos
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            List[Usuario]: Lista de usuarios activos
        """
        try:
            usuarios = db.query(UsuarioDB).filter(UsuarioDB.activo == True).all()
            return usuarios
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener usuarios: {str(e)}"
            )

    @staticmethod
    async def obtener_usuarios_desactivados(db: Session) -> List[Usuario]:
        """
        Obtiene todos los usuarios desactivados
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            List[Usuario]: Lista de usuarios desactivados
        """
        try:
            usuarios = db.query(UsuarioDB).filter(UsuarioDB.activo == False).all()
            return usuarios
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener usuarios desactivados: {str(e)}"
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
            
            return usuario
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
            if usuario_update.apellido is not None:
                usuario.apellido = usuario_update.apellido
            # Si se actualiza el RUT, normalizarlo y mantener username = rut
            if usuario_update.rut is not None:
                rut_norm = _normalizar_rut(usuario_update.rut)
                usuario.rut = rut_norm
                usuario.username = rut_norm
            # Si se actualiza explícitamente el username y NO se envía rut, respetar el username
            if usuario_update.username is not None and usuario_update.rut is None:
                usuario.username = _normalizar_rut(usuario_update.username)
            if usuario_update.email is not None:
                usuario.email = usuario_update.email
            if usuario_update.telefono is not None:
                usuario.telefono = usuario_update.telefono
            if usuario_update.password is not None:
                usuario.password = hash_contraseña(usuario_update.password)
            if usuario_update.role is not None:
                usuario.role = usuario_update.role
            
            db.commit()
            db.refresh(usuario)
            
            return Usuario(
                id_usuario=usuario.id_usuario,
                nombre=usuario.nombre,
                apellido=usuario.apellido,
                username=usuario.username,
                rut=usuario.rut,
                email=usuario.email,
                telefono=usuario.telefono,
                role=usuario.role,
                activo=usuario.activo,
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
        Desactiva un usuario (eliminación lógica)
        
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
            
            # Desactivar usuario en lugar de eliminarlo
            usuario.activo = False
            db.commit()
            
            return {"message": "Usuario desactivado exitosamente"}
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al desactivar usuario: {str(e)}"
            )

    @staticmethod
    async def eliminar_usuario_permanente(usuario_id: int, db: Session) -> dict:
        """
        Elimina permanentemente un usuario de la base de datos
        
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
            
            # Borrado en cascada manual de datos relacionados al usuario
            from models.venta import VentaDB, MovimientoInventarioDB
            from models.despacho import DespachoDB

            # 1) Eliminar movimientos de inventario asociados al usuario (sin venta)
            movimientos_usuario = db.query(MovimientoInventarioDB).filter(MovimientoInventarioDB.id_usuario == usuario_id).all()
            for m in movimientos_usuario:
                db.delete(m)

            # 2) Obtener ventas del usuario
            ventas_usuario = db.query(VentaDB).filter(VentaDB.id_usuario == usuario_id).all()

            # 2a) Eliminar movimientos de inventario asociados a cada venta (id_venta)
            for v in ventas_usuario:
                movimientos_por_venta = db.query(MovimientoInventarioDB).filter(MovimientoInventarioDB.id_venta == v.id_venta).all()
                for mv in movimientos_por_venta:
                    db.delete(mv)

            # 2b) Eliminar ventas (cascade elimina detalles_venta)
            for v in ventas_usuario:
                db.delete(v)

            # 3) Eliminar direcciones de despacho asociadas
            despachos = db.query(DespachoDB).filter(DespachoDB.id_usuario == usuario_id).all()
            for d in despachos:
                db.delete(d)

            # 4) Eliminar usuario
            db.delete(usuario)
            db.commit()

            return {"message": "Usuario eliminado permanentemente"}
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al eliminar usuario permanentemente: {str(e)}"
            )