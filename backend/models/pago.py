#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modelos relacionados con pagos (preparado para integración con Transbank/Webpay)
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Text, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .base import Base


class PagoDB(Base):
    """Modelo de base de datos para pagos asociados a una venta"""
    __tablename__ = "pagos"

    id_pago = Column(Integer, primary_key=True, index=True)
    id_venta = Column(Integer, ForeignKey("ventas.id_venta"), nullable=False, index=True)

    proveedor = Column(String(50), nullable=False, default="transbank")
    estado = Column(String(20), nullable=False, default="iniciado")  # iniciado, autorizado, fallido, anulado, reembolsado

    monto = Column(Numeric(10, 2), nullable=False)
    moneda = Column(String(3), nullable=False, default="CLP")

    # Campos típicos de Webpay
    buy_order = Column(String(50), nullable=True)
    session_id = Column(String(100), nullable=True)
    token = Column(String(100), nullable=True, index=True)
    authorization_code = Column(String(20), nullable=True)
    accounting_date = Column(String(20), nullable=True)
    payment_method = Column(String(50), nullable=True)
    installments_number = Column(Integer, nullable=True)

    # Datos crudos del PSP (JSON serializado)
    response_raw = Column(Text, nullable=True)

    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relaciones
    venta = relationship("VentaDB", back_populates="pagos")

    __table_args__ = (
        Index("ix_pagos_id_venta_estado", "id_venta", "estado"),
    )


# Modelos Pydantic

class PagoBase(BaseModel):
    id_venta: int
    proveedor: Optional[str] = "transbank"
    estado: Optional[str] = "iniciado"
    monto: float
    moneda: Optional[str] = "CLP"
    buy_order: Optional[str] = None
    session_id: Optional[str] = None
    token: Optional[str] = None
    authorization_code: Optional[str] = None
    accounting_date: Optional[str] = None
    payment_method: Optional[str] = None
    installments_number: Optional[int] = None
    response_raw: Optional[str] = None


class PagoCreate(PagoBase):
    pass


class Pago(PagoBase):
    id_pago: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True