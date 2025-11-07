from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from controllers.auditoria_controller import (
    obtener_auditoria_por_entidad,
    obtener_auditoria,
)
from config.database import get_db
from models.auditoria import Auditoria
from config.constants import API_PREFIX


router = APIRouter(prefix=f"{API_PREFIX}/auditoria", tags=["Auditoría"])


@router.get("/{entidad_tipo}/{entidad_id}", response_model=List[Auditoria])
def listar_auditoria_por_entidad(
    entidad_tipo: str,
    entidad_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """Lista eventos de auditoría por entidad (tipo/id)"""
    eventos = obtener_auditoria_por_entidad(
        db, entidad_tipo=entidad_tipo, entidad_id=entidad_id, skip=skip, limit=limit
    )
    return eventos


@router.get("/", response_model=dict)
def listar_auditoria_filtrada(
    usuario_id: Optional[int] = Query(None),
    accion: Optional[str] = Query(None),
    fecha_desde: Optional[str] = Query(None, description="ISO 8601"),
    fecha_hasta: Optional[str] = Query(None, description="ISO 8601"),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """Lista eventos de auditoría con filtros por usuario/fecha/acción y paginación"""
    return obtener_auditoria(
        db,
        usuario_id=usuario_id,
        accion=accion,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        skip=skip,
        limit=limit,
    )