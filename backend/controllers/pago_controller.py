#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Controlador para gestión de pagos (preparado para Transbank)

Este controlador establece el flujo mínimo: iniciar pago (registrar) y consultar estado.
En el futuro se conectará al PSP (Transbank) para crear la transacción real y procesar webhooks.
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional
from decimal import Decimal
from datetime import datetime

from models import PagoDB, Pago, PagoCreate, VentaDB


class PagoController:
    """Controlador para pagos asociados a ventas"""

    @staticmethod
    def iniciar_pago(db: Session, id_venta: int, monto: Decimal, moneda: str = "CLP") -> Pago:
        """
        Registra un pago 'iniciado' para una venta. No integra PSP aún.

        - Verifica que la venta exista.
        - Crea registro en pagos con estado 'iniciado'.
        """
        venta = db.query(VentaDB).filter(VentaDB.id_venta == id_venta).first()
        if not venta:
            raise HTTPException(status_code=404, detail="Venta no encontrada para iniciar pago")

        from datetime import datetime
        import uuid
        buy_order = f"ORD-{id_venta}-{int(datetime.utcnow().timestamp())}"
        session_id = None
        try:
            session_id = str(venta.rut_usuario or "GUEST")
        except Exception:
            session_id = str(uuid.uuid4())

        db_pago = PagoDB(
            id_venta=id_venta,
            proveedor="transbank",
            estado="iniciado",
            monto=monto,
            moneda=moneda,
            buy_order=buy_order,
            session_id=session_id,
        )
        db.add(db_pago)
        db.commit()
        db.refresh(db_pago)

        return Pago(
            id_pago=db_pago.id_pago,
            id_venta=db_pago.id_venta,
            proveedor=db_pago.proveedor,
            estado=db_pago.estado,
            monto=float(db_pago.monto),
            moneda=db_pago.moneda,
            buy_order=db_pago.buy_order,
            session_id=db_pago.session_id,
            token=db_pago.token,
            authorization_code=db_pago.authorization_code,
            accounting_date=db_pago.accounting_date,
            payment_method=db_pago.payment_method,
            installments_number=db_pago.installments_number,
            response_raw=db_pago.response_raw,
            fecha_creacion=db_pago.fecha_creacion,
            fecha_actualizacion=db_pago.fecha_actualizacion,
        )

    @staticmethod
    def preparar_transaccion_psp(pago: Pago, return_url: str, notify_url: str) -> dict:
        import os, hmac, hashlib
        commerce_code = os.environ.get("PAYMENT_COMMERCE_CODE", "dev_commerce")
        merchant_id = os.environ.get("PAYMENT_MERCHANT_ID", commerce_code)
        api_key = os.environ.get("PAYMENT_API_KEY", "dev_api_key")
        msg = "|".join([
            str(pago.buy_order or ""),
            str(pago.session_id or ""),
            str(int(float(pago.monto))),
            str(pago.moneda or "CLP"),
        ]).encode()
        signature = hmac.new(api_key.encode(), msg, hashlib.sha256).hexdigest()
        return {
            "merchant_id": merchant_id,
            "commerce_code": commerce_code,
            "buy_order": pago.buy_order,
            "session_id": pago.session_id,
            "amount": int(float(pago.monto)),
            "currency": pago.moneda or "CLP",
            "return_url": return_url,
            "notify_url": notify_url,
            "signature": signature,
        }

    @staticmethod
    def estado_pago_por_venta(db: Session, id_venta: int) -> dict:
        """
        Devuelve el estado del pago más reciente para una venta.
        Si no hay pago, responde estado 'sin_pago'.
        """
        ultimo_pago = (
            db.query(PagoDB)
            .filter(PagoDB.id_venta == id_venta)
            .order_by(PagoDB.id_pago.desc())
            .first()
        )

        if not ultimo_pago:
            return {"id_venta": id_venta, "estado": "sin_pago"}

        return {
            "id_venta": ultimo_pago.id_venta,
            "id_pago": ultimo_pago.id_pago,
            "estado": ultimo_pago.estado,
            "monto": float(ultimo_pago.monto),
            "moneda": ultimo_pago.moneda,
            "proveedor": ultimo_pago.proveedor,
            "token": ultimo_pago.token,
        }
