""" Rutas de direcciones de despacho """

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from config.database import get_db
from controllers.despacho_controller import DespachoController
from models.despacho import Despacho, DespachoCreate, DespachoUpdate
from config.constants import API_PREFIX

router = APIRouter(prefix=f"{API_PREFIX}/despachos", tags=["Despachos"])


@router.get("/usuario/{rut}", response_model=List[Despacho])
async def listar_por_usuario(rut: str, db: Session = Depends(get_db)):
    return await DespachoController.listar_por_usuario(rut, db)


@router.post("/usuario/{rut}", response_model=Despacho)
async def crear_despacho(rut: str, data: DespachoCreate, db: Session = Depends(get_db)):
    return await DespachoController.crear(rut, data, db)


@router.get("/{despacho_id}", response_model=Despacho)
async def obtener_despacho(despacho_id: int, db: Session = Depends(get_db)):
    return await DespachoController.obtener(despacho_id, db)


@router.put("/{despacho_id}", response_model=Despacho)
async def actualizar_despacho(despacho_id: int, data: DespachoUpdate, db: Session = Depends(get_db)):
    return await DespachoController.actualizar(despacho_id, data, db)


@router.delete("/{despacho_id}")
async def eliminar_despacho(despacho_id: int, db: Session = Depends(get_db)):
    return await DespachoController.eliminar(despacho_id, db)
