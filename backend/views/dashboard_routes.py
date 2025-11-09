from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from config.database import get_db
from config.constants import API_PREFIX
from controllers.producto_controller import ProductoController
from controllers.venta_controller import VentaController
from models.usuario import UsuarioDB
from controllers.auditoria_controller import obtener_auditoria


router = APIRouter(prefix=f"{API_PREFIX}/dashboard", tags=["Dashboard"])


@router.get("/metrics", response_model=dict)
async def obtener_metricas_dashboard(
    fecha_inicio: Optional[date] = Query(None, description="Fecha de inicio para estadísticas de ventas"),
    fecha_fin: Optional[date] = Query(None, description="Fecha de fin para estadísticas de ventas"),
    limite_actividad: int = Query(5, ge=1, le=50, description="Cantidad de eventos recientes a mostrar"),
    db: Session = Depends(get_db),
):
    """Devuelve métricas clave del dashboard para la empresa.

    Incluye:
    - Resumen de inventario (total, bajo stock, sin stock)
    - Estadísticas de ventas (ingresos, cantidad, promedio, canceladas)
    - Usuarios (activos, inactivos, total)
    - Actividad reciente (últimos eventos de auditoría)
    """

    # Productos: resumen de inventario
    resumen_inventario = await ProductoController.obtener_resumen_inventario(db)

    # Ventas: estadísticas (opcionalmente filtradas por fecha)
    estadisticas_ventas = VentaController.obtener_estadisticas_ventas(db, fecha_inicio, fecha_fin)

    # Usuarios: conteos básicos
    usuarios_activos = db.query(UsuarioDB).filter(UsuarioDB.activo == True).count()
    usuarios_inactivos = db.query(UsuarioDB).filter(UsuarioDB.activo == False).count()
    usuarios_total = usuarios_activos + usuarios_inactivos

    # Actividad reciente (auditoría)
    actividad = obtener_auditoria(db, skip=0, limit=limite_actividad)
    actividad_reciente = [
        {
            "id": evt.id,
            "accion": evt.accion,
            "entidad_tipo": evt.entidad_tipo,
            "entidad_id": evt.entidad_id,
            "detalle": evt.detalle,
            "fecha_evento": evt.fecha_evento,
            "usuario_id": evt.usuario_id,
        }
        for evt in actividad.get("data", [])
    ]

    return {
        "productos": resumen_inventario,
        "ventas": estadisticas_ventas,
        "usuarios": {
            "activos": usuarios_activos,
            "inactivos": usuarios_inactivos,
            "total": usuarios_total,
        },
        "actividad_reciente": actividad_reciente,
    }


@router.get("/charts/ventas_por_dia", response_model=list)
async def chart_ventas_por_dia(
    fecha_inicio: Optional[date] = Query(None, description="Fecha de inicio"),
    fecha_fin: Optional[date] = Query(None, description="Fecha de fin"),
    db: Session = Depends(get_db),
):
    """Devuelve ventas agrupadas por día: ingresos y cantidad."""
    return VentaController.obtener_ventas_por_dia(db, fecha_inicio, fecha_fin)


@router.get("/charts/top_productos", response_model=list)
async def chart_top_productos(
    fecha_inicio: Optional[date] = Query(None, description="Fecha de inicio"),
    fecha_fin: Optional[date] = Query(None, description="Fecha de fin"),
    limite: int = Query(5, ge=1, le=50, description="Cantidad de productos"),
    db: Session = Depends(get_db),
):
    """Devuelve top productos por unidades vendidas."""
    return VentaController.obtener_top_productos(db, fecha_inicio, fecha_fin, limit=limite)