"""
Rutas de pagos (preparadas para Transbank)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from decimal import Decimal

from config.database import get_db
from config.constants import API_PREFIX
from controllers.pago_controller import PagoController


router = APIRouter(prefix=f"{API_PREFIX}/pagos", tags=["Pagos"])


class PagoInitRequest(BaseModel):
    id_venta: int
    monto: Decimal
    moneda: str = "CLP"


@router.post("/iniciar")
async def iniciar_pago(payload: PagoInitRequest, db: Session = Depends(get_db)):
    """Registra un pago 'iniciado' para una venta (sin PSP aún)."""
    pago = PagoController.iniciar_pago(db, payload.id_venta, payload.monto, payload.moneda)
    return {"message": "Pago iniciado", "pago": pago}


@router.get("/estado/{id_venta}")
async def estado_pago(id_venta: int, db: Session = Depends(get_db)):
    """Consulta el estado del pago asociado a una venta."""
    estado = PagoController.estado_pago_por_venta(db, id_venta)
    return estado