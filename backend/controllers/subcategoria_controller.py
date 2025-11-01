#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Controlador de subcategorías
CRUD y consultas filtradas por categoría
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from models.subcategoria import SubCategoriaDB, SubCategoriaCreate, SubCategoriaUpdate, SubCategoria
from models.categoria import CategoriaDB


class SubCategoriaController:
    @staticmethod
    async def crear_subcategoria(subcategoria: SubCategoriaCreate, db: Session) -> SubCategoria:
        try:
            # Validar categoría existente
            categoria = db.query(CategoriaDB).filter(CategoriaDB.id_categoria == subcategoria.id_categoria).first()
            if not categoria:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada")

            db_sub = SubCategoriaDB(**subcategoria.dict())
            db.add(db_sub)
            db.commit()
            db.refresh(db_sub)

            return SubCategoria(
                id_subcategoria=db_sub.id_subcategoria,
                id_categoria=db_sub.id_categoria,
                nombre=db_sub.nombre,
                descripcion=db_sub.descripcion,
            )
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe una subcategoría con ese nombre")
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al crear subcategoría: {str(e)}")

    @staticmethod
    async def obtener_subcategorias(db: Session, categoria_id: Optional[int] = None) -> List[SubCategoria]:
        try:
            query = db.query(SubCategoriaDB)
            if categoria_id is not None:
                query = query.filter(SubCategoriaDB.id_categoria == categoria_id)
            subs = query.all()
            return [
                SubCategoria(
                    id_subcategoria=s.id_subcategoria,
                    id_categoria=s.id_categoria,
                    nombre=s.nombre,
                    descripcion=s.descripcion,
                ) for s in subs
            ]
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener subcategorías: {str(e)}")

    @staticmethod
    async def obtener_subcategoria(subcategoria_id: int, db: Session) -> SubCategoria:
        try:
            sub = db.query(SubCategoriaDB).filter(SubCategoriaDB.id_subcategoria == subcategoria_id).first()
            if not sub:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subcategoría no encontrada")
            return SubCategoria(
                id_subcategoria=sub.id_subcategoria,
                id_categoria=sub.id_categoria,
                nombre=sub.nombre,
                descripcion=sub.descripcion,
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener subcategoría: {str(e)}")

    @staticmethod
    async def actualizar_subcategoria(subcategoria_id: int, sub_update: SubCategoriaUpdate, db: Session) -> SubCategoria:
        try:
            sub = db.query(SubCategoriaDB).filter(SubCategoriaDB.id_subcategoria == subcategoria_id).first()
            if not sub:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subcategoría no encontrada")

            if sub_update.nombre is not None:
                sub.nombre = sub_update.nombre
            if sub_update.descripcion is not None:
                sub.descripcion = sub_update.descripcion
            if sub_update.id_categoria is not None:
                # Validar categoría
                categoria = db.query(CategoriaDB).filter(CategoriaDB.id_categoria == sub_update.id_categoria).first()
                if not categoria:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada")
                sub.id_categoria = sub_update.id_categoria

            db.commit()
            db.refresh(sub)

            return SubCategoria(
                id_subcategoria=sub.id_subcategoria,
                id_categoria=sub.id_categoria,
                nombre=sub.nombre,
                descripcion=sub.descripcion,
            )
        except HTTPException:
            raise
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe una subcategoría con ese nombre")
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al actualizar subcategoría: {str(e)}")

    @staticmethod
    async def eliminar_subcategoria(subcategoria_id: int, db: Session) -> dict:
        try:
            sub = db.query(SubCategoriaDB).filter(SubCategoriaDB.id_subcategoria == subcategoria_id).first()
            if not sub:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subcategoría no encontrada")
            db.delete(sub)
            db.commit()
            return {"message": "Subcategoría eliminada exitosamente"}
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar subcategoría: {str(e)}")