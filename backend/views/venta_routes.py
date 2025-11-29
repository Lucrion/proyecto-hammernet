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
    MovimientoInventario, VentaGuestCreate
)
# Asegurar resolución de forward refs para modelos Pydantic
try:
    VentaGuestCreate.update_forward_refs()
    VentaCreate.update_forward_refs()
    Venta.update_forward_refs()
except Exception:
    pass
from seed_data import seed_extra_ventas
from seed_data import seed_client_purchases
from core.auth import get_current_user, require_admin
from config.constants import API_PREFIX
from models.pago import PagoDB

router = APIRouter(prefix=f"{API_PREFIX}/ventas", tags=["Ventas"])


@router.post("/", response_model=Venta)
async def crear_venta(
    venta: VentaCreate,
    db: Session = Depends(get_db),
    # current_user: dict = Depends(get_current_user)  # Comentado temporalmente
):
    """ Crear una nueva venta """
    return VentaController.crear_venta(db, venta, venta.rut_usuario)


@router.post("/guest", response_model=Venta)
async def crear_venta_invitado(
    venta: VentaGuestCreate,
    db: Session = Depends(get_db),
):
    """Crear una nueva venta como invitado (sin autenticación)"""
    return VentaController.crear_venta_invitado(db, venta)


@router.get("/", response_model=List[Venta])
def obtener_ventas(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a devolver"),
    fecha_inicio: Optional[date] = Query(None, description="Fecha de inicio para filtrar ventas"),
    fecha_fin: Optional[date] = Query(None, description="Fecha de fin para filtrar ventas"),
    rut_usuario: Optional[str] = Query(None, description="RUT del usuario para filtrar ventas"),
    db: Session = Depends(get_db),
    # current_user: dict = Depends(get_current_user)  # Comentado temporalmente
):
    """ Obtener todas las ventas con filtros opcionales """
    return VentaController.obtener_ventas(db, skip, limit, fecha_inicio, fecha_fin, rut_usuario)


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
    rut_usuario: str = Query(..., description="RUT del usuario que cancela"),
    db: Session = Depends(get_db),
    # current_user: dict = Depends(get_current_user)  # Comentado temporalmente
):
    """ Cancelar una venta y restaurar el inventario """
    resultado = VentaController.cancelar_venta(db, id_venta, rut_usuario)
    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venta no encontrada o ya cancelada"
        )
    return {"message": "Venta cancelada exitosamente", "venta": resultado}


@router.put("/{id_venta}/completar")
async def completar_venta(
    id_venta: int,
    metodo: Optional[str] = Query(None, description="Metodo de entrega: retiro|despacho"),
    usuario_admin_rut: Optional[str] = Query(None, description="RUT del usuario administrador que confirma"),
    db: Session = Depends(get_db),
):
    """Marcar una venta como completada (entregada)."""
    resultado = VentaController.completar_venta(db, id_venta, usuario_admin_rut, metodo)
    return {"message": "Venta marcada como completada", "venta": resultado}


@router.put("/{id_venta}/envio-estado")
async def actualizar_estado_envio(
    id_venta: int,
    estado: str = Query(..., description="Estado de envío: pendiente|preparando|en camino|entregado"),
    db: Session = Depends(get_db),
):
    resultado = VentaController.set_envio_estado(db, id_venta, estado)
    return {"message": "Estado de envío actualizado", "venta": resultado}

@router.post("/seed")
async def seed_ventas_extra(
    cantidad: int = Query(50, ge=1, le=1000, description="Cantidad de ventas adicionales a generar"),
    db: Session = Depends(get_db),
):
    resumen = seed_extra_ventas(db, cantidad=cantidad)
    return {"status": "ok", "resumen": resumen}


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
    db: Session = Depends(get_db),
    # current_user: dict = Depends(get_current_user)  # Comentado temporalmente
):
    """ Obtener estadísticas de ventas """
    return VentaController.obtener_estadisticas_ventas(db, fecha_inicio, fecha_fin)


@router.get("/usuario/{rut}", response_model=List[Venta])
async def obtener_ventas_por_usuario(
    rut: str,
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a devolver"),
    fecha_inicio: Optional[date] = Query(None, description="Fecha de inicio para filtrar ventas"),
    fecha_fin: Optional[date] = Query(None, description="Fecha de fin para filtrar ventas"),
    db: Session = Depends(get_db),
    # current_user: dict = Depends(get_current_user)  # Comentado temporalmente
):
    """ Obtener ventas de un usuario específico """
    return VentaController.obtener_ventas(db, skip, limit, fecha_inicio, fecha_fin, rut)


@router.get("/orden/{buy_order}", response_model=Venta)
async def obtener_venta_por_orden(
    buy_order: str,
    db: Session = Depends(get_db),
):
    pago = db.query(PagoDB).filter(PagoDB.buy_order == buy_order).first()
    if not pago:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Orden no encontrada")
    return VentaController.obtener_venta_por_id(db, pago.id_venta)


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


@router.post("/seed/clientes")
async def seed_ventas_clientes(
    cantidad: int = Query(30, ge=1, le=1000, description="Cantidad de compras de clientes a generar"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Genera compras reales con distintos clientes y asigna una dirección real única por cliente."""
    resumen = seed_client_purchases(db, cantidad=cantidad)
    return {"status": "ok", "resumen": resumen}


@router.delete("/cleanup/clientes")
async def eliminar_compras_clientes(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Elimina todas las ventas de usuarios con role 'cliente' (admin requerido)."""
    resumen = VentaController.eliminar_compras_de_clientes(db)
    return {"status": "ok", **resumen}
