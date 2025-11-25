""" Rutas de usuarios """

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from config.database import get_db
from controllers.usuario_controller import UsuarioController, _rut_a_int
from models.usuario import Usuario, UsuarioCreate, UsuarioUpdate
from core.auth import get_current_user, require_admin
from config.constants import API_PREFIX
from controllers.auditoria_controller import registrar_evento

router = APIRouter(prefix=f"{API_PREFIX}/usuarios", tags=["Usuarios"])


@router.get("/", response_model=List[Usuario])
async def obtener_usuarios(
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Obtener todos los usuarios activos

    VALIDACIÓN TEMPORALMENTE DESACTIVADA: acceso sin token ni rol
    """
    usuarios = await UsuarioController.obtener_usuarios(db)
    return [
        {
            "id_usuario": usuario.id_usuario,
            "nombre": usuario.nombre,
            "apellido": usuario.apellido,
            "rut": _rut_a_int(usuario.rut),
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
    current_user = Depends(require_admin)
):
    """Obtener todos los usuarios desactivados

    VALIDACIÓN TEMPORALMENTE DESACTIVADA: acceso sin token ni rol
    """
    usuarios = await UsuarioController.obtener_usuarios_desactivados(db)
    return [
        {
            "id_usuario": usuario.id_usuario,
            "nombre": usuario.nombre,
            "rut": _rut_a_int(usuario.rut),
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
    current_user = Depends(require_admin)
):
    """ Obtener un usuario por ID

    VALIDACIÓN TEMPORALMENTE DESACTIVADA: acceso sin token ni rol
    """
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
    current_user = Depends(require_admin)
):
    """ Crear un nuevo usuario

    VALIDACIÓN TEMPORALMENTE DESACTIVADA: acceso sin token ni rol
    """
    nuevo = await UsuarioController.crear_usuario(usuario, db)
    try:
        registrar_evento(
            db,
            entidad_tipo="usuario",
            entidad_id=nuevo.id_usuario,
            accion="crear",
            usuario_actor_id=None,
            detalle=f"Usuario creado: RUT {nuevo.rut} ({nuevo.role})"
        )
    except Exception:
        # No bloquear flujo por fallo de auditoría
        pass
    return nuevo


@router.put("/{usuario_id}", response_model=Usuario)
async def actualizar_usuario(
    usuario_id: int,
    usuario: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """ Actualizar un usuario

    VALIDACIÓN TEMPORALMENTE DESACTIVADA: acceso sin token ni rol
    """
    # TODO: Reactivar después - Solo admin puede actualizar otros usuarios, usuarios normales solo pueden actualizarse a sí mismos
    # if current_user.role != "administrador" and current_user.id_usuario != usuario_id:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="No tienes permisos para actualizar este usuario"
    #     )
    
    actualizado = await UsuarioController.actualizar_usuario(usuario_id, usuario, db)
    try:
        registrar_evento(
            db,
            entidad_tipo="usuario",
            entidad_id=usuario_id,
            accion="actualizar",
            usuario_actor_id=None,
            detalle="Datos de usuario actualizados"
        )
    except Exception:
        pass
    return actualizado


@router.put("/{usuario_id}/desactivar")
async def desactivar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """ Desactivar un usuario (eliminación lógica)

    VALIDACIÓN TEMPORALMENTE DESACTIVADA: acceso sin token ni rol
    """
    resp = await UsuarioController.eliminar_usuario(usuario_id, db)
    try:
        registrar_evento(
            db,
            entidad_tipo="usuario",
            entidad_id=usuario_id,
            accion="desactivar",
            usuario_actor_id=None,
            detalle="Usuario desactivado (baja lógica)"
        )
    except Exception:
        pass
    return resp


@router.put("/{usuario_id}/activar")
async def activar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """ Activar un usuario (alta lógica)

    VALIDACIÓN TEMPORALMENTE DESACTIVADA: acceso sin token ni rol
    """
    resp = await UsuarioController.activar_usuario(usuario_id, db)
    try:
        registrar_evento(
            db,
            entidad_tipo="usuario",
            entidad_id=usuario_id,
            accion="activar",
            usuario_actor_id=None,
            detalle="Usuario activado (alta lógica)"
        )
    except Exception:
        pass
    return resp


@router.delete("/{usuario_id}/eliminar-permanente")
async def eliminar_usuario_permanente(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """ Eliminar permanentemente un usuario desactivado

    VALIDACIÓN TEMPORALMENTE DESACTIVADA: acceso sin token ni rol
    """
    result = await UsuarioController.eliminar_usuario_permanente(usuario_id, db)
    try:
        registrar_evento(
            db,
            entidad_tipo="usuario",
            entidad_id=usuario_id,
            accion="eliminar",
            usuario_actor_id=None,
            detalle="Usuario eliminado permanentemente"
        )
    except Exception:
        pass
    return result

from seed_data import prune_active_clients_to_n

@router.post("/prune-clientes")
async def prune_clientes(
    target: int = 30,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Deja solo N clientes activos; el resto se desactiva."""
    resumen = prune_active_clients_to_n(db, target=target)
    return {"status": "ok", "resumen": resumen}

@router.post("/eliminar-desactivados")
async def eliminar_desactivados(
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Elimina permanentemente todos los usuarios desactivados (clientes y trabajadores)."""
    from controllers.usuario_controller import UsuarioController
    resumen = await UsuarioController.eliminar_usuarios_desactivados(db)
    return {"status": "ok", "resumen": resumen}

@router.post("/purge-clientes")
async def purge_clientes_y_compras(
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Elimina todos los usuarios con role 'cliente' y borra sus compras relacionadas."""
    from controllers.usuario_controller import UsuarioController
    resumen = await UsuarioController.eliminar_clientes_y_compras(db)
    return {"status": "ok", "resumen": resumen}
