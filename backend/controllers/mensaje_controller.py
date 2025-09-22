#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Controlador de mensajes de contacto
Maneja todas las operaciones CRUD de mensajes de contacto
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from models.mensaje import MensajeContactoDB, MensajeContactoCreate, MensajeContacto


class MensajeController:
    """Controlador para manejo de mensajes de contacto"""
    
    @staticmethod
    async def crear_mensaje(mensaje: MensajeContactoCreate, db: Session) -> MensajeContacto:
        """
        Crea un nuevo mensaje de contacto
        
        Args:
            mensaje: Datos del mensaje a crear
            db: Sesión de base de datos
            
        Returns:
            MensajeContacto: Mensaje creado
            
        Raises:
            HTTPException: Si hay error en la creación
        """
        try:
            db_mensaje = MensajeContactoDB(**mensaje.dict())
            db.add(db_mensaje)
            db.commit()
            db.refresh(db_mensaje)
            
            return MensajeContacto(
                id=db_mensaje.id,
                nombre=db_mensaje.nombre,
                apellido=db_mensaje.apellido,
                email=db_mensaje.email,
                asunto=db_mensaje.asunto,
                mensaje=db_mensaje.mensaje,
                fecha_envio=db_mensaje.fecha_envio.isoformat() if db_mensaje.fecha_envio else "",
                leido=db_mensaje.leido
            )
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear mensaje: {str(e)}"
            )
    
    @staticmethod
    async def obtener_mensajes(db: Session, solo_no_leidos: bool = False) -> List[MensajeContacto]:
        """
        Obtiene todos los mensajes de contacto
        
        Args:
            db: Sesión de base de datos
            solo_no_leidos: Si True, solo devuelve mensajes no leídos
            
        Returns:
            List[MensajeContacto]: Lista de mensajes
        """
        try:
            query = db.query(MensajeContactoDB)
            
            if solo_no_leidos:
                query = query.filter(MensajeContactoDB.leido == False)
            
            mensajes = query.order_by(MensajeContactoDB.fecha_envio.desc()).all()
            
            return [
                MensajeContacto(
                    id=m.id,
                    nombre=m.nombre,
                    apellido=m.apellido,
                    email=m.email,
                    asunto=m.asunto,
                    mensaje=m.mensaje,
                    fecha_envio=m.fecha_envio.isoformat() if m.fecha_envio else "",
                    leido=m.leido
                ) for m in mensajes
            ]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener mensajes: {str(e)}"
            )
    
    @staticmethod
    async def obtener_mensaje(mensaje_id: int, db: Session) -> MensajeContacto:
        """
        Obtiene un mensaje de contacto por ID
        
        Args:
            mensaje_id: ID del mensaje
            db: Sesión de base de datos
            
        Returns:
            MensajeContacto: Mensaje encontrado
            
        Raises:
            HTTPException: Si el mensaje no existe
        """
        try:
            mensaje = db.query(MensajeContactoDB).filter(MensajeContactoDB.id == mensaje_id).first()
            if not mensaje:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Mensaje no encontrado"
                )
            
            return MensajeContacto(
                id=mensaje.id,
                nombre=mensaje.nombre,
                apellido=mensaje.apellido,
                email=mensaje.email,
                asunto=mensaje.asunto,
                mensaje=mensaje.mensaje,
                fecha_envio=mensaje.fecha_envio.isoformat() if mensaje.fecha_envio else "",
                leido=mensaje.leido
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener mensaje: {str(e)}"
            )
    
    @staticmethod
    async def marcar_como_leido(mensaje_id: int, db: Session) -> MensajeContacto:
        """
        Marca un mensaje como leído
        
        Args:
            mensaje_id: ID del mensaje
            db: Sesión de base de datos
            
        Returns:
            MensajeContacto: Mensaje actualizado
            
        Raises:
            HTTPException: Si el mensaje no existe o hay error
        """
        try:
            mensaje = db.query(MensajeContactoDB).filter(MensajeContactoDB.id == mensaje_id).first()
            if not mensaje:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Mensaje no encontrado"
                )
            
            mensaje.leido = True
            db.commit()
            db.refresh(mensaje)
            
            return MensajeContacto(
                id=mensaje.id,
                nombre=mensaje.nombre,
                apellido=mensaje.apellido,
                email=mensaje.email,
                asunto=mensaje.asunto,
                mensaje=mensaje.mensaje,
                fecha_envio=mensaje.fecha_envio.isoformat() if mensaje.fecha_envio else "",
                leido=mensaje.leido
            )
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al marcar mensaje como leído: {str(e)}"
            )
    
    @staticmethod
    async def eliminar_mensaje(mensaje_id: int, db: Session) -> dict:
        """
        Elimina un mensaje de contacto
        
        Args:
            mensaje_id: ID del mensaje
            db: Sesión de base de datos
            
        Returns:
            dict: Mensaje de confirmación
            
        Raises:
            HTTPException: Si el mensaje no existe o hay error
        """
        try:
            mensaje = db.query(MensajeContactoDB).filter(MensajeContactoDB.id == mensaje_id).first()
            if not mensaje:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Mensaje no encontrado"
                )
            
            db.delete(mensaje)
            db.commit()
            
            return {"message": "Mensaje eliminado exitosamente"}
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al eliminar mensaje: {str(e)}"
            )
    
    @staticmethod
    async def obtener_estadisticas_mensajes(db: Session) -> dict:
        """
        Obtiene estadísticas de los mensajes
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            dict: Estadísticas de mensajes
        """
        try:
            from sqlalchemy import func
            
            total_mensajes = db.query(func.count(MensajeContactoDB.id)).scalar()
            mensajes_no_leidos = db.query(func.count(MensajeContactoDB.id)).filter(
                MensajeContactoDB.leido == False
            ).scalar()
            mensajes_leidos = total_mensajes - mensajes_no_leidos
            
            return {
                "total_mensajes": total_mensajes,
                "mensajes_leidos": mensajes_leidos,
                "mensajes_no_leidos": mensajes_no_leidos,
                "porcentaje_leidos": round((mensajes_leidos / total_mensajes * 100), 2) if total_mensajes > 0 else 0
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener estadísticas: {str(e)}"
            )