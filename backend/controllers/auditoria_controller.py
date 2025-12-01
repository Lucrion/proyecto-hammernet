#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Controlador de auditoría
Registra eventos y permite consultas filtradas
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from fastapi import HTTPException, status
from models.auditoria import AuditoriaDB, Auditoria, AuditoriaCreate


async def registrar_evento(
    db: Session,
    accion: str,
    usuario_rut: Optional[str] = None,
    entidad_tipo: Optional[str] = None,
    entidad_id: Optional[int] = None,
    detalle: Optional[str] = None,
) -> Auditoria:
    """Registra un evento de auditoría"""
    try:
        # Permitir pasar un objeto AuditoriaCreate como primer argumento
        try:
            from models.auditoria import AuditoriaCreate
            if isinstance(accion, AuditoriaCreate):
                payload = accion
                accion = payload.accion
                usuario_rut = getattr(payload, 'usuario_rut', usuario_rut)
                entidad_tipo = payload.entidad_tipo
                entidad_id = payload.entidad_id
                detalle = payload.detalle
        except Exception:
            pass

        if accion and accion.strip().lower().startswith("login"):
            from datetime import datetime
            return Auditoria(
                id_evento=0,
                usuario_rut=usuario_rut,
                accion=accion,
                entidad_tipo=entidad_tipo,
                entidad_id=entidad_id,
                detalle=detalle,
                fecha_evento=datetime.utcnow(),
            )
        evento = AuditoriaDB(
            usuario_rut=usuario_rut,
            accion=accion,
            entidad_tipo=entidad_tipo,
            entidad_id=entidad_id,
            detalle=detalle,
        )
        db.add(evento)
        db.commit()
        db.refresh(evento)
        return Auditoria.from_orm(evento)
    except Exception as e:
        db.rollback()
        # No bloquear la operación original por fallos de auditoría
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar auditoría: {str(e)}",
        )


def obtener_auditoria_por_entidad(
    db: Session,
    entidad_tipo: str,
    entidad_id: int,
    skip: int = 0,
    limit: int = 50,
) -> List[Auditoria]:
    """Obtiene eventos de auditoría por entidad"""
    q = (
        db.query(AuditoriaDB)
        .filter(
            and_(
                AuditoriaDB.entidad_tipo == entidad_tipo,
                AuditoriaDB.entidad_id == entidad_id,
            )
        )
        .order_by(desc(AuditoriaDB.fecha_evento))
        .offset(skip)
        .limit(limit)
    )
    eventos = q.all()
    return [Auditoria.from_orm(e) for e in eventos]


def obtener_auditoria(
    db: Session,
    usuario_rut: Optional[str] = None,
    accion: Optional[str] = None,
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> dict:
    """Lista eventos de auditoría con filtros dinámicos y paginación"""
    from sqlalchemy import func, text
    qry = db.query(AuditoriaDB)
    if usuario_rut is not None:
        qry = qry.filter(AuditoriaDB.usuario_rut == usuario_rut)
    if accion:
        qry = qry.filter(AuditoriaDB.accion == accion)
    # Filtros de fecha si se proveen como ISO
    if fecha_desde:
        qry = qry.filter(AuditoriaDB.fecha_evento >= fecha_desde)
    if fecha_hasta:
        qry = qry.filter(AuditoriaDB.fecha_evento <= fecha_hasta)

    total = qry.count()
    items = (
        qry.order_by(desc(AuditoriaDB.fecha_evento))
        .offset(skip)
        .limit(limit)
        .all()
    )
    return {
        "total": total,
        "data": [Auditoria.from_orm(e) for e in items],
    }
