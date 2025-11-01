#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Rutas de subcategorías
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from config.database import get_db
from controllers.subcategoria_controller import SubCategoriaController
from models.subcategoria import SubCategoria, SubCategoriaCreate, SubCategoriaUpdate
from core.auth import require_admin
from config.constants import API_PREFIX

router = APIRouter(prefix=f"{API_PREFIX}/subcategorias", tags=["Subcategorías"])


@router.get("/", response_model=List[SubCategoria])
async def obtener_subcategorias(
    categoria_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Obtener todas las subcategorías, opcionalmente filtradas por categoría"""
    return await SubCategoriaController.obtener_subcategorias(db, categoria_id)


@router.get("/{subcategoria_id}", response_model=SubCategoria)
async def obtener_subcategoria(
    subcategoria_id: int,
    db: Session = Depends(get_db)
):
    """Obtener una subcategoría por ID"""
    return await SubCategoriaController.obtener_subcategoria(subcategoria_id, db)


@router.post("/", response_model=SubCategoria)
async def crear_subcategoria(
    subcategoria: SubCategoriaCreate,
    db: Session = Depends(get_db),
    # current_user: dict = Depends(require_admin)
):
    """Crear una nueva subcategoría (solo administradores)"""
    return await SubCategoriaController.crear_subcategoria(subcategoria, db)


@router.put("/{subcategoria_id}", response_model=SubCategoria)
async def actualizar_subcategoria(
    subcategoria_id: int,
    subcategoria: SubCategoriaUpdate,
    db: Session = Depends(get_db),
    # current_user: dict = Depends(require_admin)
):
    """Actualizar una subcategoría (solo administradores)"""
    return await SubCategoriaController.actualizar_subcategoria(subcategoria_id, subcategoria, db)


@router.delete("/{subcategoria_id}")
async def eliminar_subcategoria(
    subcategoria_id: int,
    db: Session = Depends(get_db),
    # current_user: dict = Depends(require_admin)
):
    """Eliminar una subcategoría (solo administradores)"""
    return await SubCategoriaController.eliminar_subcategoria(subcategoria_id, db)