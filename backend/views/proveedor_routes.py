""" Rutas de proveedores """

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from config.database import get_db
from controllers.proveedor_controller import ProveedorController
from models.proveedor import Proveedor, ProveedorCreate, ProveedorUpdate
from core.auth import get_current_user, require_admin
from config.constants import API_PREFIX

router = APIRouter(prefix=f"{API_PREFIX}/proveedores", tags=["Proveedores"])


@router.get("/", response_model=List[Proveedor])
async def obtener_proveedores(
    db: Session = Depends(get_db),
    # current_user: dict = Depends(get_current_user)  # Comentado temporalmente
):
    """ Obtener todos los proveedores """
    return await ProveedorController.obtener_proveedores(db)


@router.get("/{proveedor_id}", response_model=Proveedor)
async def obtener_proveedor(
    proveedor_id: int,
    db: Session = Depends(get_db),
    # current_user: dict = Depends(get_current_user)  # Comentado temporalmente
):
    """ Obtener un proveedor por ID """
    return await ProveedorController.obtener_proveedor(proveedor_id, db)


@router.post("/", response_model=Proveedor)
async def crear_proveedor(
    proveedor: ProveedorCreate,
    db: Session = Depends(get_db),
    # current_user: dict = Depends(require_admin)  # Comentado temporalmente
):
    """ Crear un nuevo proveedor (solo administradores) """
    return await ProveedorController.crear_proveedor(proveedor, db)


@router.put("/{proveedor_id}", response_model=Proveedor)
async def actualizar_proveedor(
    proveedor_id: int,
    proveedor: ProveedorUpdate,
    db: Session = Depends(get_db),
    # current_user: dict = Depends(require_admin)  # Comentado temporalmente
):
    """ Actualizar un proveedor (solo administradores) """
    return await ProveedorController.actualizar_proveedor(proveedor_id, proveedor, db)


@router.delete("/{proveedor_id}")
async def eliminar_proveedor(
    proveedor_id: int,
    db: Session = Depends(get_db),
    # current_user: dict = Depends(require_admin)  # Comentado temporalmente
):
    """ Eliminar un proveedor (solo administradores) """
    return await ProveedorController.eliminar_proveedor(proveedor_id, db)