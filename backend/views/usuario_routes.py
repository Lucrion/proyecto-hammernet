""" Rutas de usuarios """

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from config.database import get_db
from controllers.usuario_controller import UsuarioController
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
            "nombre": usuario.nombre,
            "apellido": usuario.apellido,
            "rut": str(usuario.rut) if usuario.rut is not None else None,
            "email": usuario.email,
            "telefono": usuario.telefono,
            "role": getattr(getattr(usuario, "rol_ref", None), "nombre", None),
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
            "nombre": usuario.nombre,
            "rut": str(usuario.rut) if usuario.rut is not None else None,
            "role": getattr(getattr(usuario, "rol_ref", None), "nombre", None),
            "activo": usuario.activo,
            "fecha_creacion": usuario.fecha_creacion.isoformat() if usuario.fecha_creacion else None
        }
        for usuario in usuarios
    ]


@router.get("/me", response_model=Usuario)
async def obtener_usuario_actual(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return {
        "nombre": current_user.nombre,
        "apellido": current_user.apellido,
        "rut": str(current_user.rut) if current_user.rut is not None else None,
        "email": current_user.email,
        "telefono": current_user.telefono,
        "role": getattr(getattr(current_user, "rol_ref", None), "nombre", None),
        "activo": current_user.activo,
        "fecha_creacion": getattr(current_user, "fecha_creacion", None).isoformat() if getattr(current_user, "fecha_creacion", None) else None
    }


@router.get("/{rut}", response_model=Usuario)
async def obtener_usuario(
    rut: str,
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
    
    usuario = await UsuarioController.obtener_usuario(rut, db)
    return {
        "nombre": usuario.nombre,
        "apellido": usuario.apellido,
        "rut": usuario.rut,
        "email": usuario.email,
        "telefono": usuario.telefono,
        "role": getattr(getattr(usuario, "rol_ref", None), "nombre", None),
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
            entidad_id=None,
            accion="crear",
            usuario_rut=nuevo.rut,
            detalle=f"Usuario creado: RUT {nuevo.rut} ({nuevo.role})"
        )
    except Exception:
        # No bloquear flujo por fallo de auditoría
        pass
    return nuevo


@router.put("/me", response_model=Usuario)
async def actualizar_usuario_actual(
    usuario: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    actualizado = await UsuarioController.actualizar_usuario(current_user.rut, usuario, db)
    return actualizado


@router.put("/{rut}", response_model=Usuario)
async def actualizar_usuario(
    rut: str,
    usuario: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """ Actualizar un usuario

    VALIDACIÓN TEMPORALMENTE DESACTIVADA: acceso sin token ni rol
    """
    actualizado = await UsuarioController.actualizar_usuario(rut, usuario, db)
    try:
        registrar_evento(
            db,
            entidad_tipo="usuario",
            entidad_id=None,
            accion="actualizar",
            usuario_rut=rut,
            detalle="Datos de usuario actualizados"
        )
    except Exception:
        pass
    return actualizado


@router.put("/{rut}/desactivar")
async def desactivar_usuario(
    rut: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """ Desactivar un usuario (eliminación lógica)

    VALIDACIÓN TEMPORALMENTE DESACTIVADA: acceso sin token ni rol
    """
    resp = await UsuarioController.eliminar_usuario(rut, db)
    try:
        registrar_evento(
            db,
            entidad_tipo="usuario",
            entidad_id=None,
            accion="desactivar",
            usuario_rut=rut,
            detalle="Usuario desactivado (baja lógica)"
        )
    except Exception:
        pass
    return resp


@router.put("/{rut}/activar")
async def activar_usuario(
    rut: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """ Activar un usuario (alta lógica)

    VALIDACIÓN TEMPORALMENTE DESACTIVADA: acceso sin token ni rol
    """
    resp = await UsuarioController.activar_usuario(rut, db)
    try:
        registrar_evento(
            db,
            entidad_tipo="usuario",
            entidad_id=None,
            accion="activar",
            usuario_rut=rut,
            detalle="Usuario activado (alta lógica)"
        )
    except Exception:
        pass
    return resp


@router.delete("/{rut}/eliminar-permanente")
async def eliminar_usuario_permanente(
    rut: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """ Eliminar permanentemente un usuario desactivado

    VALIDACIÓN TEMPORALMENTE DESACTIVADA: acceso sin token ni rol
    """
    result = await UsuarioController.eliminar_usuario_permanente(rut, db)
    try:
        registrar_evento(
            db,
            entidad_tipo="usuario",
            entidad_id=None,
            accion="eliminar",
            usuario_rut=rut,
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
