"""
Rutas de pagos (preparadas para Transbank)
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from decimal import Decimal
import os, hmac, hashlib

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
    """Registra un pago 'iniciado' y entrega token y URLs para flujo PSP."""
    pago = PagoController.iniciar_pago(db, payload.id_venta, payload.monto, payload.moneda)
    token = f"tok_{pago.id_pago}"
    redirect_url = f"/api/pagos/return?venta_id={payload.id_venta}&token={token}"
    notify_url = f"/api/pagos/notify"
    return {"message": "Pago iniciado", "pago": pago, "token": token, "redirect_url": redirect_url, "notify_url": notify_url}


@router.get("/estado/{id_venta}")
async def estado_pago(id_venta: int, db: Session = Depends(get_db)):
    """Consulta el estado del pago asociado a una venta."""
    estado = PagoController.estado_pago_por_venta(db, id_venta)
    return estado


@router.get("/return")
async def pago_return(venta_id: int, token: str, db: Session = Depends(get_db)):
    """Retorno informal del portal de pagos: redirige al frontend raíz con flag de compra."""
    frontend_base = os.environ.get("FRONTEND_URL", "https://ferreteria-patricio.onrender.com")
    url = f"{frontend_base}/?paid=1&venta_id={venta_id}&token={token}"
    return RedirectResponse(url=url, status_code=302)

def _verify_signature(venta_id: int, token: str, status_str: str, signature: str) -> bool:
    secret = os.environ.get("PAYMENT_NOTIFY_SECRET", "dev_secret")
    msg = f"{venta_id}|{token}|{status_str}".encode()
    mac = hmac.new(secret.encode(), msg, hashlib.sha256).hexdigest()
    try:
        return hmac.compare_digest(mac, signature or "")
    except Exception:
        return False

@router.post("/notify")
async def pago_notify(payload: dict, db: Session = Depends(get_db)):
    """Notificación real del PSP: verifica firma y marca venta como pagada."""
    venta_id = int(payload.get("venta_id") or 0)
    token = str(payload.get("token") or "")
    status_str = str(payload.get("status") or "").lower()
    signature = str(payload.get("signature") or "")
    if not venta_id or not token:
        raise HTTPException(status_code=400, detail="Payload inválido")
    if not _verify_signature(venta_id, token, status_str, signature):
        raise HTTPException(status_code=400, detail="Firma inválida")
    if status_str == "aprobado":
        from controllers.venta_controller import VentaController
        venta = VentaController.completar_venta(db, venta_id, usuario_admin_id=None, metodo=None)
        return {"status": "aprobado", "venta": venta}
    return {"status": status_str}
