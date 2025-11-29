from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text

from config.database import get_db
from config.constants import API_PREFIX
from controllers.producto_controller import ProductoController
from controllers.venta_controller import VentaController
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
    try:
        total_productos = db.execute(text("SELECT COUNT(1) FROM productos WHERE estado = 'activo'")).scalar() or 0
        productos_sin_stock = db.execute(text("SELECT COUNT(1) FROM productos WHERE COALESCE(cantidad_disponible,0) = 0")).scalar() or 0
        productos_bajo_stock = db.execute(text("SELECT COUNT(1) FROM productos WHERE COALESCE(cantidad_disponible,0) <= COALESCE(stock_minimo,0)")).scalar() or 0
        total_cantidad_disponible = db.execute(text("SELECT COALESCE(SUM(cantidad_disponible),0) FROM productos")).scalar() or 0
        resumen_inventario = {
            "total_productos": int(total_productos),
            "productos_bajo_stock": int(productos_bajo_stock),
            "productos_sin_stock": int(productos_sin_stock),
            "productos_con_stock": int(total_productos) - int(productos_sin_stock),
            "total_cantidad_disponible": int(total_cantidad_disponible),
        }
    except Exception:
        resumen_inventario = {
            "total_productos": 0,
            "productos_bajo_stock": 0,
            "productos_sin_stock": 0,
            "productos_con_stock": 0,
            "total_cantidad_disponible": 0,
        }
    from models.producto import ProductoDB
    try:
        total_valor = db.execute(text("SELECT COALESCE(SUM(COALESCE(precio_venta,0) * COALESCE(cantidad_disponible,0)),0) FROM productos")).scalar() or 0
        total_items = db.execute(text("SELECT COUNT(1) FROM productos")).scalar() or 0
        en_oferta = db.execute(text("SELECT COUNT(1) FROM productos WHERE oferta_activa = 1")).scalar() or 0
        pct = (en_oferta / total_items * 100) if total_items else 0
        resumen_inventario["valor_inventario_total"] = float(total_valor)
        resumen_inventario["porcentaje_en_oferta"] = pct
    except Exception:
        resumen_inventario["valor_inventario_total"] = 0
        resumen_inventario["porcentaje_en_oferta"] = 0

    # Ventas: estadísticas (opcionalmente filtradas por fecha)
    try:
        estadisticas_ventas = VentaController.obtener_estadisticas_ventas(db, fecha_inicio, fecha_fin)
    except Exception:
        estadisticas_ventas = {"ingresos": 0, "cantidad_ventas": 0, "promedio": 0, "canceladas": 0}

    # Ventas por períodos: día, semana, mes
    from datetime import datetime, timedelta
    try:
        hoy = datetime.utcnow().date()
        inicio_semana = hoy - timedelta(days=6)
        inicio_mes = (hoy.replace(day=1))

        ventas_hoy = VentaController.obtener_estadisticas_ventas(db, fecha_inicio=hoy, fecha_fin=hoy)
        ventas_semana = VentaController.obtener_estadisticas_ventas(db, fecha_inicio=inicio_semana, fecha_fin=hoy)
        ventas_mes = VentaController.obtener_estadisticas_ventas(db, fecha_inicio=inicio_mes, fecha_fin=hoy)
        resumen_periodos = {
            "dia": {"ingresos": ventas_hoy.get("total_ventas", 0), "cantidad": ventas_hoy.get("cantidad_ventas", 0)},
            "semana": {"ingresos": ventas_semana.get("total_ventas", 0), "cantidad": ventas_semana.get("cantidad_ventas", 0)},
            "mes": {"ingresos": ventas_mes.get("total_ventas", 0), "cantidad": ventas_mes.get("cantidad_ventas", 0)},
        }
    except Exception:
        resumen_periodos = {"dia": {"ingresos": 0, "cantidad": 0}, "semana": {"ingresos": 0, "cantidad": 0}, "mes": {"ingresos": 0, "cantidad": 0}}

    # Usuarios: conteos básicos
    try:
        usuarios_activos = db.execute(text("SELECT COUNT(1) FROM usuarios WHERE activo = 1")).scalar() or 0
        usuarios_inactivos = db.execute(text("SELECT COUNT(1) FROM usuarios WHERE activo = 0")).scalar() or 0
    except Exception:
        usuarios_activos = 0
        usuarios_inactivos = 0
    usuarios_total = usuarios_activos + usuarios_inactivos

    # Actividad reciente (auditoría)
    try:
        actividad = obtener_auditoria(db, skip=0, limit=limite_actividad)
        actividad_reciente = [
            {
                "id_evento": evt.id_evento,
                "accion": evt.accion,
                "entidad_tipo": evt.entidad_tipo,
                "entidad_id": evt.entidad_id,
                "detalle": evt.detalle,
                "fecha_evento": evt.fecha_evento,
                "usuario_rut": evt.usuario_rut,
            }
            for evt in actividad.get("data", [])
        ]
    except Exception:
        actividad_reciente = []

    return {
        "productos": resumen_inventario,
        "ventas": estadisticas_ventas,
        "ventas_periodos": resumen_periodos,
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

@router.get("/charts/ventas_por_categoria", response_model=list)
async def chart_ventas_por_categoria(
    fecha_inicio: Optional[date] = Query(None, description="Fecha de inicio"),
    fecha_fin: Optional[date] = Query(None, description="Fecha de fin"),
    db: Session = Depends(get_db),
):
    return VentaController.obtener_ventas_por_categoria(db, fecha_inicio, fecha_fin)

@router.get("/charts/inventario_por_categoria", response_model=list)
async def chart_inventario_por_categoria(
    db: Session = Depends(get_db),
):
    return await ProductoController.obtener_inventario_por_categoria(db)
