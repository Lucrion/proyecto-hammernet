#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Controlador para direcciones de despacho de usuarios
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from models.despacho import DespachoDB, DespachoCreate, DespachoUpdate, Despacho
from models.usuario import UsuarioDB


class DespachoController:
    """Operaciones CRUD para direcciones de despacho"""

    @staticmethod
    async def crear(usuario_id: int, data: DespachoCreate, db: Session) -> Despacho:
        # Verificar usuario
        usuario = db.query(UsuarioDB).filter(UsuarioDB.id_usuario == usuario_id, UsuarioDB.activo == True).first()
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

        if not data.calle or not data.numero:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Calle y número son obligatorios")

        try:
            registro = DespachoDB(
                id_usuario=usuario_id,
                buscar=data.buscar,
                calle=data.calle,
                numero=data.numero,
                depto=data.depto,
                adicional=data.adicional,
            )
            db.add(registro)
            db.commit()
            db.refresh(registro)
            return Despacho.from_orm(registro)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al crear despacho: {str(e)}")

    @staticmethod
    async def listar_por_usuario(usuario_id: int, db: Session) -> List[Despacho]:
        try:
            registros = db.query(DespachoDB).filter(DespachoDB.id_usuario == usuario_id).order_by(DespachoDB.fecha_actualizacion.desc()).all()
            return [Despacho.from_orm(r) for r in registros]
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener despachos: {str(e)}")

    @staticmethod
    async def obtener(despacho_id: int, db: Session) -> Despacho:
        registro = db.query(DespachoDB).filter(DespachoDB.id_despacho == despacho_id).first()
        if not registro:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Despacho no encontrado")
        return Despacho.from_orm(registro)

    @staticmethod
    async def actualizar(despacho_id: int, data: DespachoUpdate, db: Session) -> Despacho:
        registro = db.query(DespachoDB).filter(DespachoDB.id_despacho == despacho_id).first()
        if not registro:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Despacho no encontrado")

        try:
            for field in ["buscar", "calle", "numero", "depto", "adicional"]:
                value = getattr(data, field, None)
                if value is not None:
                    setattr(registro, field, value)
            db.add(registro)
            db.commit()
            db.refresh(registro)
            return Despacho.from_orm(registro)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al actualizar despacho: {str(e)}")

    @staticmethod
    async def eliminar(despacho_id: int, db: Session) -> dict:
        registro = db.query(DespachoDB).filter(DespachoDB.id_despacho == despacho_id).first()
        if not registro:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Despacho no encontrado")
        try:
            db.delete(registro)
            db.commit()
            return {"message": "Despacho eliminado"}
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar despacho: {str(e)}")