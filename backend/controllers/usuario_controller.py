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


def _rut_a_int(rut) -> int:
    """Convierte un RUT con formato (con puntos/guion) a entero (solo dígitos).
    Acepta int y str; si es str, se extraen solo dígitos, descartando DV.
    """
    if rut is None:
        return None
    if isinstance(rut, int):
        return rut
    s = str(rut).strip()
    # Extraer únicamente dígitos
    digits = ''.join(ch for ch in s if ch.isdigit())
    return int(digits) if digits else None


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

            # Normalizar RUT a entero (login por RUT)
            rut_int = _rut_a_int(usuario.rut)
            if not rut_int:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Debe proporcionar el RUT"
                )

            # Hash de la contraseña
            hashed_password = hash_contraseña(usuario.password)
            
            # Crear usuario en BD
            db_usuario = UsuarioDB(
                nombre=usuario.nombre,
                apellido=usuario.apellido,
                rut=rut_int,
                email=usuario.email,
                telefono=usuario.telefono,
                password=hashed_password,
                role=usuario.role
            )
            
            db.add(db_usuario)
            db.commit()
            db.refresh(db_usuario)
            
            return Usuario(
                id_usuario=db_usuario.id_usuario,
                nombre=db_usuario.nombre,
                apellido=db_usuario.apellido,
                rut=_rut_a_int(db_usuario.rut),
                email=db_usuario.email,
                telefono=db_usuario.telefono,
                role=db_usuario.role,
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
    async def crear_usuario_google(nombre: str, rut: str, email: str, password: str, role: str, db: Session) -> Usuario:
        """
        Crea un nuevo usuario desde Google OAuth
        
        Args:
            nombre: Nombre del usuario
            rut: RUT del usuario (normalizado)
            email: Email del usuario
            password: Contraseña temporal
            role: Rol del usuario
            db: Sesión de base de datos
            
        Returns:
            Usuario: Usuario creado
            
        Raises:
            HTTPException: Si hay error en la creación
        """
        try:
            # Hash de la contraseña
            hashed_password = hash_contraseña(password)
            
            # Crear usuario en BD
            db_usuario = UsuarioDB(
                nombre=nombre,
                rut=_rut_a_int(rut) if rut else None,
                email=email,
                password=hashed_password,
                role=role,
                activo=True
            )
            
            db.add(db_usuario)
            db.commit()
            db.refresh(db_usuario)
            
            return Usuario(
                id_usuario=db_usuario.id_usuario,
                nombre=db_usuario.nombre,
                apellido=db_usuario.apellido,
                rut=_rut_a_int(db_usuario.rut),
                email=db_usuario.email,
                telefono=db_usuario.telefono,
                role=db_usuario.role,
                activo=db_usuario.activo,
                fecha_creacion=db_usuario.fecha_creacion.isoformat() if db_usuario.fecha_creacion else None
            )
            
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El usuario ya existe"
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear usuario desde Google: {str(e)}"
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
    async def obtener_usuario(usuario_id: int, db: Session) -> Usuario:
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
            usuario = db.query(UsuarioDB).filter(UsuarioDB.id_usuario == usuario_id).first()
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
    async def actualizar_usuario(usuario_id: int, usuario_update: UsuarioUpdate, db: Session) -> Usuario:
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
            usuario = db.query(UsuarioDB).filter(UsuarioDB.id_usuario == usuario_id).first()
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
            # Si se actualiza el RUT, normalizarlo a entero
            if usuario_update.rut is not None:
                usuario.rut = _rut_a_int(usuario_update.rut)
            if usuario_update.email is not None:
                usuario.email = usuario_update.email
            if usuario_update.telefono is not None:
                usuario.telefono = usuario_update.telefono
            if usuario_update.password is not None:
                usuario.password = hash_contraseña(usuario_update.password)
            if usuario_update.role is not None:
                usuario.role = usuario_update.role
            
            db.commit()
            db.refresh(usuario)
            
            return Usuario(
                id_usuario=usuario.id_usuario,
                nombre=usuario.nombre,
                apellido=usuario.apellido,
                rut=_rut_a_int(usuario.rut),
                email=usuario.email,
                telefono=usuario.telefono,
                role=usuario.role,
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
    async def eliminar_usuario(usuario_id: int, db: Session) -> dict:
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
            usuario = db.query(UsuarioDB).filter(UsuarioDB.id_usuario == usuario_id).first()
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
    async def activar_usuario(usuario_id: int, db: Session) -> dict:
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
            usuario = db.query(UsuarioDB).filter(UsuarioDB.id_usuario == usuario_id).first()
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
    async def eliminar_usuario_permanente(usuario_id: int, db: Session) -> dict:
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
            usuario = db.query(UsuarioDB).filter(UsuarioDB.id_usuario == usuario_id).first()
            if not usuario:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )
            # Solo permitir si está desactivado
            if usuario.activo:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario debe estar desactivado antes de eliminar permanentemente")
            # No permitir eliminar clientes vía permanente (solo trabajadores)
            if (usuario.role or '').lower() == 'cliente':
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se permite eliminar clientes permanentemente")
            
            # Borrado en cascada manual de datos relacionados al usuario
            from models.venta import VentaDB, MovimientoInventarioDB, DetalleVentaDB
            from models.despacho import DespachoDB
            from models.pago import PagoDB
            from models.auditoria import AuditoriaDB

            # 1) Eliminar movimientos de inventario asociados al usuario (sin venta)
            movimientos_usuario = db.query(MovimientoInventarioDB).filter(MovimientoInventarioDB.id_usuario == usuario_id).all()
            for m in movimientos_usuario:
                db.delete(m)

            # 2) Obtener ventas del usuario (como vendedor) y como cliente
            ventas_usuario = db.query(VentaDB).filter(VentaDB.id_usuario == usuario_id).all()
            ventas_cliente = db.query(VentaDB).filter(VentaDB.cliente_id == usuario_id).all()
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
            despachos = db.query(DespachoDB).filter(DespachoDB.id_usuario == usuario_id).all()
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
                uid = usuario.id_usuario
                from models.venta import VentaDB, MovimientoInventarioDB, DetalleVentaDB
                from models.despacho import DespachoDB
                from models.pago import PagoDB
                from models.auditoria import AuditoriaDB

                mov_sin_venta = db.query(MovimientoInventarioDB).filter(MovimientoInventarioDB.id_usuario == uid, MovimientoInventarioDB.id_venta == None).all()
                for m in mov_sin_venta:
                    db.delete(m)

                ventas_usuario = db.query(VentaDB).filter((VentaDB.id_usuario == uid) | (VentaDB.cliente_id == uid)).all()
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

                despachos = db.query(DespachoDB).filter(DespachoDB.id_usuario == uid).all()
                for d in despachos:
                    db.delete(d)

                auds = db.query(AuditoriaDB).filter(AuditoriaDB.usuario_id == uid).all()
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
            auds = db.query(AuditoriaDB).filter(AuditoriaDB.usuario_id == usuario_id).all()
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
            clientes = db.query(UsuarioDB).filter(func.lower(UsuarioDB.role) == 'cliente').all()
            eliminados = 0

            for cliente in clientes:
                uid = cliente.id_usuario

                # Ventas donde el usuario es cliente
                ventas_cliente = db.query(VentaDB).filter(VentaDB.cliente_id == uid).all()
                # Ventas donde el usuario aparece como vendedor (por si acaso en datos de prueba)
                ventas_usuario = db.query(VentaDB).filter(VentaDB.id_usuario == uid).all()
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
                mov_sin_venta = db.query(MovimientoInventarioDB).filter(MovimientoInventarioDB.id_usuario == uid, MovimientoInventarioDB.id_venta == None).all()
                for m in mov_sin_venta:
                    db.delete(m)

                # Eliminar direcciones de despacho
                despachos = db.query(DespachoDB).filter(DespachoDB.id_usuario == uid).all()
                for d in despachos:
                    db.delete(d)

                # Eliminar auditoría asociada al usuario
                auds = db.query(AuditoriaDB).filter(AuditoriaDB.usuario_id == uid).all()
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
