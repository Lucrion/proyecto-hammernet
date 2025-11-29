#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Controlador de usuarios
Maneja todas las operaciones CRUD de usuarios
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from models.usuario import UsuarioDB, UsuarioCreate, UsuarioUpdate, Usuario
from core.auth import hash_contraseña


def _rut_normalizado(rut: str) -> str:
    if rut is None:
        return None
    s = str(rut).strip().upper()
    cuerpo = ''.join(ch for ch in s if ch.isdigit())[:8]
    dv = ''
    dv_prov = None
    if s and not s[-1].isdigit():
        dv = 'K' if s[-1] == 'K' else s[-1]
        dv_prov = dv
    def _dv_calc(b: str) -> str:
        if not b:
            return ''
        acc = 0
        f = 2
        for ch in reversed(b):
            acc += int(ch) * f
            f = 2 if f == 7 else f + 1
        rest = 11 - (acc % 11)
        if rest == 11:
            return '0'
        if rest == 10:
            return 'K'
        return str(rest)
    if cuerpo:
        expected = _dv_calc(cuerpo)
        if dv_prov is not None and dv_prov != expected:
            return None
        if not dv:
            dv = expected
    return f"{cuerpo}{dv}" if cuerpo else None


class UsuarioController:
    """Controlador para manejo de usuarios"""
    
    @staticmethod
    async def crear_usuario(usuario: UsuarioCreate, db: Session) -> Usuario:
        """
        Crea un nuevo usuario
        
        Args:
            usuario: Datos del usuario a crear
            db: Sesión de base de datos
            
        Returns:
            Usuario: Usuario creado
            
        Raises:
            HTTPException: Si hay error en la creación
        """
        try:
            # Validar confirmación de contraseña si se envía
            if usuario.confirm_password is not None and usuario.password != usuario.confirm_password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La confirmación de contraseña no coincide"
                )

            rut_str = _rut_normalizado(usuario.rut)
            if not rut_str:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="RUT inválido"
                )

            # Hash de la contraseña
            hashed_password = hash_contraseña(usuario.password)
            
            rol_nombre = usuario.role
            if not rol_nombre:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Debe proporcionar el rol"
                )
            from models.rol import RolDB
            rol = db.query(RolDB).filter(RolDB.nombre == rol_nombre).first()
            if not rol:
                rol = RolDB(nombre=rol_nombre)
                db.add(rol)
                db.flush()
            db_usuario = UsuarioDB(
                nombre=usuario.nombre,
                apellido=usuario.apellido,
                rut=rut_str,
                email=usuario.email,
                telefono=usuario.telefono,
                password=hashed_password,
                id_rol=rol.id_rol
            )
            
            db.add(db_usuario)
            db.commit()
            db.refresh(db_usuario)
            
            return Usuario(
                rut=db_usuario.rut,
                nombre=db_usuario.nombre,
                apellido=db_usuario.apellido,
                email=db_usuario.email,
                telefono=db_usuario.telefono,
                role=getattr(getattr(db_usuario, "rol_ref", None), "nombre", None),
                activo=db_usuario.activo,
                fecha_creacion=db_usuario.fecha_creacion.isoformat() if db_usuario.fecha_creacion else None
            )
            
        except IntegrityError as ie:
            db.rollback()
            # Mensaje más específico según restricción
            msg = "El usuario ya existe"
            if 'rut' in str(ie.orig).lower():
                msg = "El RUT ya está registrado"
            if 'email' in str(ie.orig).lower():
                msg = "El correo ya está registrado"
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=msg
            )
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear usuario: {str(e)}"
            )
    
    
    @staticmethod
    async def obtener_usuarios(db: Session) -> List[Usuario]:
        """
        Obtiene todos los usuarios activos
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            List[Usuario]: Lista de usuarios activos
        """
        try:
            usuarios = db.query(UsuarioDB).filter(UsuarioDB.activo == True).all()
            return usuarios
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener usuarios: {str(e)}"
            )

    @staticmethod
    async def obtener_usuarios_desactivados(db: Session) -> List[Usuario]:
        """
        Obtiene todos los usuarios desactivados
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            List[Usuario]: Lista de usuarios desactivados
        """
        try:
            usuarios = db.query(UsuarioDB).filter(UsuarioDB.activo == False).all()
            return usuarios
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener usuarios desactivados: {str(e)}"
            )
    
    @staticmethod
    async def obtener_usuario(rut: str, db: Session) -> Usuario:
        """
        Obtiene un usuario por ID
        
        Args:
            usuario_id: ID del usuario
            db: Sesión de base de datos
            
        Returns:
            Usuario: Usuario encontrado
            
        Raises:
            HTTPException: Si el usuario no existe
        """
        try:
            usuario = db.query(UsuarioDB).filter(UsuarioDB.rut == rut).first()
            if not usuario:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )
            
            return usuario
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener usuario: {str(e)}"
            )
    
    @staticmethod
    async def actualizar_usuario(rut: str, usuario_update: UsuarioUpdate, db: Session) -> Usuario:
        """
        Actualiza un usuario
        
        Args:
            usuario_id: ID del usuario
            usuario_update: Datos a actualizar
            db: Sesión de base de datos
            
        Returns:
            Usuario: Usuario actualizado
            
        Raises:
            HTTPException: Si el usuario no existe o hay error
        """
        try:
            usuario = db.query(UsuarioDB).filter(UsuarioDB.rut == rut).first()
            if not usuario:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )
            
            # Actualizar campos
            if usuario_update.nombre is not None:
                usuario.nombre = usuario_update.nombre
            if usuario_update.apellido is not None:
                usuario.apellido = usuario_update.apellido
            if usuario_update.email is not None:
                usuario.email = usuario_update.email
            if usuario_update.telefono is not None:
                usuario.telefono = usuario_update.telefono
            if usuario_update.password is not None:
                usuario.password = hash_contraseña(usuario_update.password)
            if usuario_update.role is not None:
                from models.rol import RolDB
                rol = db.query(RolDB).filter(RolDB.nombre == usuario_update.role).first()
                if not rol:
                    rol = RolDB(nombre=usuario_update.role)
                    db.add(rol)
                    db.flush()
                usuario.id_rol = rol.id_rol
            
            db.commit()
            db.refresh(usuario)
            
            return Usuario(
                rut=usuario.rut,
                nombre=usuario.nombre,
                apellido=usuario.apellido,
                email=usuario.email,
                telefono=usuario.telefono,
                role=getattr(getattr(usuario, "rol_ref", None), "nombre", None),
                activo=usuario.activo,
                fecha_creacion=usuario.fecha_creacion.isoformat() if usuario.fecha_creacion else None
            )
            
        except HTTPException:
            raise
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El RUT ya existe"
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al actualizar usuario: {str(e)}"
            )
    
    @staticmethod
    async def eliminar_usuario(rut: str, db: Session) -> dict:
        """
        Desactiva un usuario (eliminación lógica)
        
        Args:
            usuario_id: ID del usuario
            db: Sesión de base de datos
            
        Returns:
            dict: Mensaje de confirmación
            
        Raises:
            HTTPException: Si el usuario no existe o hay error
        """
        try:
            usuario = db.query(UsuarioDB).filter(UsuarioDB.rut == rut).first()
            if not usuario:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )
            
            # Desactivar usuario en lugar de eliminarlo
            usuario.activo = False
            db.commit()
            
            return {"message": "Usuario desactivado exitosamente"}
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al desactivar usuario: {str(e)}"
            )

    @staticmethod
    async def activar_usuario(rut: str, db: Session) -> dict:
        """
        Activa un usuario previamente desactivado (alta lógica)
        
        Args:
            usuario_id: ID del usuario
            db: Sesión de base de datos
            
        Returns:
            dict: Mensaje de confirmación
            
        Raises:
            HTTPException: Si el usuario no existe o hay error
        """
        try:
            usuario = db.query(UsuarioDB).filter(UsuarioDB.rut == rut).first()
            if not usuario:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )

            # Activar usuario
            usuario.activo = True
            db.commit()

            return {"message": "Usuario activado exitosamente"}
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al activar usuario: {str(e)}"
            )

    @staticmethod
    async def eliminar_usuario_permanente(rut: str, db: Session) -> dict:
        """
        Elimina permanentemente un usuario de la base de datos
        
        Args:
            usuario_id: ID del usuario
            db: Sesión de base de datos
            
        Returns:
            dict: Mensaje de confirmación
            
        Raises:
            HTTPException: Si el usuario no existe o hay error
        """
        try:
            usuario = db.query(UsuarioDB).filter(UsuarioDB.rut == rut).first()
            if not usuario:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )
            # Solo permitir si está desactivado
            if usuario.activo:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario debe estar desactivado antes de eliminar permanentemente")
            # Borrado en cascada manual de datos relacionados al usuario
            from models.venta import VentaDB, MovimientoInventarioDB, DetalleVentaDB
            from models.despacho import DespachoDB
            from models.pago import PagoDB
            from models.auditoria import AuditoriaDB

            # 1) Eliminar movimientos de inventario asociados al usuario (sin venta)
            movimientos_usuario = db.query(MovimientoInventarioDB).filter(MovimientoInventarioDB.rut_usuario == rut).all()
            for m in movimientos_usuario:
                db.delete(m)

            # 2) Obtener ventas del usuario (como vendedor) y como cliente
            ventas_usuario = db.query(VentaDB).filter(VentaDB.rut_usuario == rut).all()
            ventas_cliente = db.query(VentaDB).filter(VentaDB.cliente_rut == rut).all()
            ventas_todas = ventas_usuario + ventas_cliente

            # 2a) Eliminar movimientos de inventario asociados a cada venta (id_venta)
            for v in ventas_todas:
                movimientos_por_venta = db.query(MovimientoInventarioDB).filter(MovimientoInventarioDB.id_venta == v.id_venta).all()
                for mv in movimientos_por_venta:
                    db.delete(mv)
                # Eliminar pagos asociados a la venta
                pagos = db.query(PagoDB).filter(PagoDB.id_venta == v.id_venta).all()
                for p in pagos:
                    db.delete(p)
                # Eliminar detalles de venta
                detalles = db.query(DetalleVentaDB).filter(DetalleVentaDB.id_venta == v.id_venta).all()
                for d in detalles:
                    db.delete(d)

            # 2b) Eliminar ventas (cascade elimina detalles_venta)
            for v in ventas_todas:
                db.delete(v)

            # 3) Eliminar direcciones de despacho asociadas
            despachos = db.query(DespachoDB).filter(DespachoDB.rut_usuario == rut).all()
            for d in despachos:
                db.delete(d)

            # 4) Eliminar usuario
            db.delete(usuario)
            db.commit()

            return {"message": "Usuario eliminado permanentemente"}
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al eliminar usuario permanentemente: {str(e)}"
            )

    @staticmethod
    async def eliminar_usuarios_desactivados(db: Session) -> dict:
        """
        Elimina permanentemente todos los usuarios desactivados (clientes y trabajadores)
        realizando borrado en cascada seguro de datos relacionados.
        """
        try:
            usuarios = db.query(UsuarioDB).filter(UsuarioDB.activo == False).all()
            eliminados = 0
            for usuario in usuarios:
                uid = usuario.rut
                from models.venta import VentaDB, MovimientoInventarioDB, DetalleVentaDB
                from models.despacho import DespachoDB
                from models.pago import PagoDB
                from models.auditoria import AuditoriaDB

                mov_sin_venta = db.query(MovimientoInventarioDB).filter(MovimientoInventarioDB.rut_usuario == uid, MovimientoInventarioDB.id_venta == None).all()
                for m in mov_sin_venta:
                    db.delete(m)

                ventas_usuario = db.query(VentaDB).filter((VentaDB.rut_usuario == uid) | (VentaDB.cliente_rut == uid)).all()
                for v in ventas_usuario:
                    movs = db.query(MovimientoInventarioDB).filter(MovimientoInventarioDB.id_venta == v.id_venta).all()
                    for mv in movs:
                        db.delete(mv)
                    pays = db.query(PagoDB).filter(PagoDB.id_venta == v.id_venta).all()
                    for p in pays:
                        db.delete(p)
                    dets = db.query(DetalleVentaDB).filter(DetalleVentaDB.id_venta == v.id_venta).all()
                    for d in dets:
                        db.delete(d)
                    db.delete(v)

                despachos = db.query(DespachoDB).filter(DespachoDB.rut_usuario == uid).all()
                for d in despachos:
                    db.delete(d)

                auds = db.query(AuditoriaDB).filter(AuditoriaDB.usuario_rut == uid).all()
                for a in auds:
                    db.delete(a)

                db.delete(usuario)
                eliminados += 1

            db.commit()
            return {"eliminados": eliminados}
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar usuarios desactivados: {str(e)}")
            # 3b) Eliminar auditoría asociada al usuario
            auds = db.query(AuditoriaDB).filter(AuditoriaDB.usuario_rut == uid).all()
            for a in auds:
                db.delete(a)

    @staticmethod
    async def eliminar_clientes_y_compras(db: Session) -> dict:
        """
        Elimina de la base de datos todos los usuarios con role "cliente" y
        borra en cascada sus compras (ventas), pagos, detalles, movimientos de inventario,
        direcciones de despacho y auditoría.
        """
        try:
            from models.venta import VentaDB, MovimientoInventarioDB, DetalleVentaDB
            from models.despacho import DespachoDB
            from models.pago import PagoDB
            from models.auditoria import AuditoriaDB

            from sqlalchemy import func
            from models.rol import RolDB
            clientes = (
                db.query(UsuarioDB)
                .join(RolDB, UsuarioDB.id_rol == RolDB.id_rol)
                .filter(func.lower(RolDB.nombre) == 'cliente')
                .all()
            )
            eliminados = 0

            for cliente in clientes:
                uid = cliente.rut

                # Ventas donde el usuario es cliente
                ventas_cliente = db.query(VentaDB).filter(VentaDB.cliente_rut == uid).all()
                # Ventas donde el usuario aparece como vendedor (por si acaso en datos de prueba)
                ventas_usuario = db.query(VentaDB).filter(VentaDB.rut_usuario == uid).all()
                ventas_todas = ventas_cliente + ventas_usuario
                for v in ventas_todas:
                    # Eliminar movimientos generados por la venta
                    movs = db.query(MovimientoInventarioDB).filter(MovimientoInventarioDB.id_venta == v.id_venta).all()
                    for mv in movs:
                        db.delete(mv)
                    # Eliminar pagos de la venta
                    pays = db.query(PagoDB).filter(PagoDB.id_venta == v.id_venta).all()
                    for p in pays:
                        db.delete(p)
                    # Eliminar detalles de la venta
                    dets = db.query(DetalleVentaDB).filter(DetalleVentaDB.id_venta == v.id_venta).all()
                    for d in dets:
                        db.delete(d)
                    # Eliminar la venta
                    db.delete(v)

                # También eliminar movimientos de inventario sueltos del cliente (si existieran)
                mov_sin_venta = db.query(MovimientoInventarioDB).filter(MovimientoInventarioDB.rut_usuario == uid, MovimientoInventarioDB.id_venta == None).all()
                for m in mov_sin_venta:
                    db.delete(m)

                # Eliminar direcciones de despacho
                despachos = db.query(DespachoDB).filter(DespachoDB.rut_usuario == uid).all()
                for d in despachos:
                    db.delete(d)

                # Eliminar auditoría asociada al usuario
                auds = db.query(AuditoriaDB).filter(AuditoriaDB.usuario_rut == uid).all()
                for a in auds:
                    db.delete(a)

                # Finalmente eliminar el usuario cliente
                db.delete(cliente)
                eliminados += 1

            db.commit()
            return {"clientes_eliminados": eliminados}
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar clientes y compras: {str(e)}")
