""" Rutas de usuarios """

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from controllers.usuario_controller import UsuarioController
from models.usuario import Usuario, UsuarioCreate, UsuarioUpdate
from auth import get_current_user, require_admin

router = APIRouter(prefix="/api/usuarios", tags=["Usuarios"])


@router.get("/", response_model=List[Usuario])
async def obtener_usuarios(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Obtener todos los usuarios (solo administradores)"""
    return await UsuarioController.obtener_usuarios(db)


@router.get("/{usuario_id}", response_model=Usuario)
async def obtener_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """ Obtener un usuario por ID """
    # Solo admin puede ver otros usuarios, usuarios normales solo pueden verse a sí mismos
    if current_user["rol"] != "admin" and current_user["id"] != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver este usuario"
        )
    
    return await UsuarioController.obtener_usuario(usuario_id, db)


@router.post("/", response_model=Usuario)
async def crear_usuario(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """ Crear un nuevo usuario (solo administradores) """
    return await UsuarioController.crear_usuario(usuario, db)


@router.put("/{usuario_id}", response_model=Usuario)
async def actualizar_usuario(
    usuario_id: int,
    usuario: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """ Actualizar un usuario """
    # Solo admin puede actualizar otros usuarios, usuarios normales solo pueden actualizarse a sí mismos
    if current_user["rol"] != "admin" and current_user["id"] != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar este usuario"
        )
    
    return await UsuarioController.actualizar_usuario(usuario_id, usuario, db)


@router.delete("/{usuario_id}")
async def eliminar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """ Eliminar un usuario (solo administradores) """
    return await UsuarioController.eliminar_usuario(usuario_id, db)