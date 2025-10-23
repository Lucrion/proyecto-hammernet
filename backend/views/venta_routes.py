"""
Rutas de ventas
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from config.database import get_db
from controllers.venta_controller import VentaController
from models.venta import (
    Venta, VentaCreate, VentaUpdate, 
    DetalleVenta, DetalleVentaCreate,
    MovimientoInventario
)
from core.auth import get_current_user, require_admin

router = APIRouter(prefix="/api/ventas", tags=["Ventas"])


@router.post("/", response_model=Venta)
async def crear_venta(
    venta: VentaCreate,
    db: Session = Depends(get_db),
    # current_user: dict = Depends(get_current_user)  # Comentado temporalmente
):
    """ Crear una nueva venta """
    return VentaController.crear_venta(db, venta, venta.id_usuario)


@router.get("/", response_model=List[Venta])
def obtener_ventas(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a devolver"),
    fecha_inicio: Optional[date] = Query(None, description="Fecha de inicio para filtrar ventas"),
    fecha_fin: Optional[date] = Query(None, description="Fecha de fin para filtrar ventas"),
    id_usuario: Optional[int] = Query(None, description="ID del usuario para filtrar ventas"),
    db: Session = Depends(get_db),
    # current_user: dict = Depends(get_current_user)  # Comentado temporalmente
):
    """ Obtener todas las ventas con filtros opcionales """
    return VentaController.obtener_ventas(db, skip, limit, fecha_inicio, fecha_fin, id_usuario)


@router.get("/{id_venta}", response_model=Venta)
async def obtener_venta_por_id(
    id_venta: int,
    db: Session = Depends(get_db),
    # current_user: dict = Depends(get_current_user)  # Comentado temporalmente
):
    """ Obtener una venta específica por ID """
    venta = VentaController.obtener_venta_por_id(db, id_venta)
    if not venta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venta no encontrada"
        )
    return venta


@router.put("/{id_venta}/cancelar")
async def cancelar_venta(
    id_venta: int,
    id_usuario: int = Query(..., description="ID del usuario que cancela"),
    db: Session = Depends(get_db),
    # current_user: dict = Depends(get_current_user)  # Comentado temporalmente
):
    """ Cancelar una venta y restaurar el inventario """
    resultado = VentaController.cancelar_venta(db, id_venta, id_usuario)
    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venta no encontrada o ya cancelada"
        )
    return {"message": "Venta cancelada exitosamente", "venta": resultado}


@router.get("/movimientos/inventario", response_model=List[MovimientoInventario])
async def obtener_movimientos_inventario(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a devolver"),
    id_producto: Optional[int] = Query(None, description="ID del producto para filtrar movimientos"),
    tipo_movimiento: Optional[str] = Query(None, description="Tipo de movimiento (venta, cancelacion)"),
    fecha_inicio: Optional[date] = Query(None, description="Fecha de inicio para filtrar movimientos"),
    fecha_fin: Optional[date] = Query(None, description="Fecha de fin para filtrar movimientos"),
    db: Session = Depends(get_db),
    # current_user: dict = Depends(get_current_user)  # Comentado temporalmente
):
    """ Obtener movimientos de inventario con filtros opcionales """
    return VentaController.obtener_movimientos_inventario(
        db, skip, limit, id_producto
    )


@router.get("/estadisticas/resumen")
async def obtener_estadisticas_ventas(
    fecha_inicio: Optional[date] = Query(None, description="Fecha de inicio para estadísticas"),
    fecha_fin: Optional[date] = Query(None, description="Fecha de fin para estadísticas"),
    id_usuario: Optional[int] = Query(None, description="ID del usuario para filtrar estadísticas"),
    db: Session = Depends(get_db),
    # current_user: dict = Depends(get_current_user)  # Comentado temporalmente
):
    """ Obtener estadísticas de ventas """
    return VentaController.obtener_estadisticas_ventas(db, fecha_inicio, fecha_fin)


@router.get("/usuario/{id_usuario}", response_model=List[Venta])
async def obtener_ventas_por_usuario(
    id_usuario: int,
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a devolver"),
    fecha_inicio: Optional[date] = Query(None, description="Fecha de inicio para filtrar ventas"),
    fecha_fin: Optional[date] = Query(None, description="Fecha de fin para filtrar ventas"),
    db: Session = Depends(get_db),
    # current_user: dict = Depends(get_current_user)  # Comentado temporalmente
):
    """ Obtener ventas de un usuario específico """
    return VentaController.obtener_ventas(db, skip, limit, fecha_inicio, fecha_fin, id_usuario)


@router.get("/producto/{id_producto}/movimientos", response_model=List[MovimientoInventario])
async def obtener_movimientos_por_producto(
    id_producto: int,
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a devolver"),
    fecha_inicio: Optional[date] = Query(None, description="Fecha de inicio para filtrar movimientos"),
    fecha_fin: Optional[date] = Query(None, description="Fecha de fin para filtrar movimientos"),
    db: Session = Depends(get_db),
    # current_user: dict = Depends(get_current_user)  # Comentado temporalmente
):
    """ Obtener movimientos de inventario de un producto específico """
    return VentaController.obtener_movimientos_inventario(
        db, skip, limit, id_producto
    )