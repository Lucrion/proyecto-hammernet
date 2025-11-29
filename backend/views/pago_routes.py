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

class PagoSimulacionRequest(BaseModel):
    id_venta: int
    status: str
    payment_type_code: str | None = None
    amount: Decimal | None = None
    installments_amount: Decimal | None = None
    installments_number: int | None = None
    card_last4: str | None = None
    reason: str | None = None
    message: str | None = None


@router.post("/iniciar")
async def iniciar_pago(payload: PagoInitRequest, db: Session = Depends(get_db)):
    pago = PagoController.iniciar_pago(db, payload.id_venta, payload.monto, payload.moneda)
    token = f"tok_{pago.id_pago}"
    frontend_base = os.environ.get("FRONTEND_URL", "https://ferreteria-patricio.onrender.com")
    return_url = f"{frontend_base}/?paid=1&venta_id={payload.id_venta}&token={token}"
    notify_url = os.environ.get("PAYMENT_NOTIFY_URL", f"/api/pagos/notify")
    psp = PagoController.preparar_transaccion_psp(pago, return_url, notify_url)
    return {"status": "iniciado", "pago": pago, "token": token, "psp": psp, "redirect_url": f"/api/pagos/return?venta_id={payload.id_venta}&token={token}", "notify_url": notify_url}


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
        venta = VentaController.completar_venta(db, venta_id, usuario_admin_rut=None, metodo=None)
        return {"status": "aprobado", "venta": venta}
    return {"status": status_str}


@router.post("/simular/notificar")
async def pago_simular_notify(payload: PagoSimulacionRequest, db: Session = Depends(get_db)):
    from sqlalchemy.orm import joinedload
    from models.venta import VentaDB
    from models.pago import PagoDB
    v = db.query(VentaDB).options(joinedload(VentaDB.pagos)).filter(VentaDB.id_venta == payload.id_venta).first()
    if not v:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    ultimo = (
        db.query(PagoDB)
        .filter(PagoDB.id_venta == payload.id_venta)
        .order_by(PagoDB.id_pago.desc())
        .first()
    )
    if not ultimo:
        raise HTTPException(status_code=400, detail="No hay pago iniciado para simular")
    import uuid
    from datetime import datetime
    status = payload.status.upper()
    ultimo.response_raw = None
    ultimo.authorization_code = None
    ultimo.payment_method = None
    ultimo.installments_number = payload.installments_number
    ultimo.monto = payload.amount or ultimo.monto
    ultimo.accounting_date = datetime.utcnow().strftime("%Y-%m-%d")
    transaction_id = str(uuid.uuid4())
    buy_order = ultimo.buy_order or f"ORD-{payload.id_venta}"
    payment_type_code = payload.payment_type_code or "VD"
    card_last4 = (payload.card_last4 or "0000")[:4]
    transaction_date = datetime.utcnow().isoformat()

    if status == "AUTHORIZED":
        ultimo.estado = "aprobado"
        ultimo.authorization_code = f"A{str(uuid.uuid4())[:8].upper()}"
        ultimo.payment_method = payment_type_code
        ultimo.token = ultimo.token or f"tok_{ultimo.id_pago}"
        db.commit()
        from controllers.venta_controller import VentaController
        venta = VentaController.completar_venta(db, payload.id_venta, usuario_admin_rut=None, metodo=None)
        return {
            "status": "AUTHORIZED",
            "transaction_id": transaction_id,
            "buy_order": buy_order,
            "authorization_code": ultimo.authorization_code,
            "payment_type_code": payment_type_code,
            "amount": float(ultimo.monto),
            "installments_amount": float(payload.installments_amount or 0),
            "installments_number": payload.installments_number or 0,
            "card_number": f"**** **** **** {card_last4}",
            "transaction_date": transaction_date,
            "authorization_date": transaction_date,
            "venta": venta,
        }
    elif status in {"REJECTED", "FAILED"}:
        ultimo.estado = "rechazado"
        db.commit()
        return {"status": status, "reason": payload.reason or "Fondos insuficientes"}
    elif status == "ABORTED":
        ultimo.estado = "anulado"
        db.commit()
        return {"status": "ABORTED"}
    elif status == "TIMEOUT":
        ultimo.estado = "fallido"
        db.commit()
        return {"status": "TIMEOUT"}
    elif status == "ERROR":
        return {"status": "ERROR", "message": payload.message or "API key inválida"}
    else:
        raise HTTPException(status_code=400, detail="Status no soportado")
