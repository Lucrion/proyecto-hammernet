""" Rutas de usuarios """

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from config.database import get_db
from controllers.usuario_controller import UsuarioController
from models.usuario import Usuario, UsuarioCreate, UsuarioUpdate
# TODO: Reactivar después - from auth import get_current_user, require_admin

router = APIRouter(prefix="/api/usuarios", tags=["Usuarios"])


@router.get("/", response_model=List[Usuario])
async def obtener_usuarios(
    db: Session = Depends(get_db),
    # TODO: Reactivar después - current_user: dict = Depends(require_admin)
):
    """Obtener todos los usuarios activos (solo administradores)"""
    usuarios = await UsuarioController.obtener_usuarios(db)
    return [
        {
            "id_usuario": usuario.id_usuario,
            "nombre": usuario.nombre,
            "apellido": usuario.apellido,
            "username": usuario.username,
            "rut": usuario.rut,
            "email": usuario.email,
            "telefono": usuario.telefono,
            "role": usuario.role,
            "activo": usuario.activo,
            "fecha_creacion": usuario.fecha_creacion.isoformat() if usuario.fecha_creacion else None
        }
        for usuario in usuarios
    ]


@router.get("/desactivados", response_model=List[Usuario])
async def obtener_usuarios_desactivados(
    db: Session = Depends(get_db),
    # TODO: Reactivar después - current_user: dict = Depends(require_admin)
):
    """Obtener todos los usuarios desactivados (solo administradores)"""
    usuarios = await UsuarioController.obtener_usuarios_desactivados(db)
    return [
        {
            "id_usuario": usuario.id_usuario,
            "nombre": usuario.nombre,
            "username": usuario.username,
            "role": usuario.role,
            "activo": usuario.activo,
            "fecha_creacion": usuario.fecha_creacion.isoformat() if usuario.fecha_creacion else None
        }
        for usuario in usuarios
    ]


@router.get("/{usuario_id}", response_model=Usuario)
async def obtener_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    # TODO: Reactivar después - current_user: dict = Depends(get_current_user)
):
    """ Obtener un usuario por ID """
    # TODO: Reactivar después - Solo admin puede ver otros usuarios, usuarios normales solo pueden verse a sí mismos
    # if current_user.role != "administrador" and current_user.id_usuario != usuario_id:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="No tienes permisos para ver este usuario"
    #     )
    
    usuario = await UsuarioController.obtener_usuario(usuario_id, db)
    return {
        "id_usuario": usuario.id_usuario,
        "nombre": usuario.nombre,
        "apellido": usuario.apellido,
        "username": usuario.username,
        "rut": usuario.rut,
        "email": usuario.email,
        "telefono": usuario.telefono,
        "role": usuario.role,
        "activo": usuario.activo,
        "fecha_creacion": usuario.fecha_creacion.isoformat() if usuario.fecha_creacion else None
    }


@router.post("/", response_model=Usuario)
async def crear_usuario(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db),
    # TODO: Reactivar después - current_user: dict = Depends(require_admin)
):
    """ Crear un nuevo usuario (solo administradores) """
    return await UsuarioController.crear_usuario(usuario, db)


@router.put("/{usuario_id}", response_model=Usuario)
async def actualizar_usuario(
    usuario_id: int,
    usuario: UsuarioUpdate,
    db: Session = Depends(get_db),
    # TODO: Reactivar después - current_user: dict = Depends(get_current_user)
):
    """ Actualizar un usuario """
    # TODO: Reactivar después - Solo admin puede actualizar otros usuarios, usuarios normales solo pueden actualizarse a sí mismos
    # if current_user.role != "administrador" and current_user.id_usuario != usuario_id:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="No tienes permisos para actualizar este usuario"
    #     )
    
    return await UsuarioController.actualizar_usuario(usuario_id, usuario, db)


@router.put("/{usuario_id}/desactivar")
async def desactivar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    # TODO: Reactivar después - current_user: dict = Depends(require_admin)
):
    """ Desactivar un usuario (eliminación lógica) """
    return await UsuarioController.eliminar_usuario(usuario_id, db)


@router.delete("/{usuario_id}/eliminar-permanente")
async def eliminar_usuario_permanente(
    usuario_id: int,
    db: Session = Depends(get_db),
    # TODO: Reactivar después - current_user: dict = Depends(require_admin)
):
    """ Eliminar permanentemente un usuario desactivado (solo administradores) """
    return await UsuarioController.eliminar_usuario_permanente(usuario_id, db)