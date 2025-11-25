#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Rutas de categorías
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from config.database import get_db
from controllers.categoria_controller import CategoriaController
from models.categoria import Categoria, CategoriaCreate, CategoriaUpdate
from core.auth import get_current_user, require_admin
from config.constants import API_PREFIX

router = APIRouter(prefix=f"{API_PREFIX}/categorias", tags=["Categorías"])


@router.get("/", response_model=List[Categoria])
async def obtener_categorias(
    db: Session = Depends(get_db)
):
    """ Obtener todas las categorías """
    return await CategoriaController.obtener_categorias(db)


@router.get("/{categoria_id}", response_model=Categoria)
async def obtener_categoria(
    categoria_id: int,
    db: Session = Depends(get_db)
):
    """ Obtener una categoría por ID """
    return await CategoriaController.obtener_categoria(categoria_id, db)


@router.post("/", response_model=Categoria)
async def crear_categoria(
    categoria: CategoriaCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """ Crear una nueva categoría (solo administradores) """
    return await CategoriaController.crear_categoria(categoria, db)


@router.put("/{categoria_id}", response_model=Categoria)
async def actualizar_categoria(
    categoria_id: int,
    categoria: CategoriaUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """ Actualizar una categoría (solo administradores) """
    return await CategoriaController.actualizar_categoria(categoria_id, categoria, db)


@router.delete("/{categoria_id}")
async def eliminar_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """ Eliminar una categoría (solo administradores) """
    return await CategoriaController.eliminar_categoria(categoria_id, db)
