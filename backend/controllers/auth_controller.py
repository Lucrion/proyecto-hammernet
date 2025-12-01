#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Controlador de autenticación
Maneja el login y autenticación de usuarios
"""

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from models.usuario import UsuarioDB, Token
from models.pago import PagoDB
from models.venta import VentaDB
from controllers.auditoria_controller import registrar_evento
from core.auth import verificar_contraseña, crear_token



class AuthController:
    """Controlador para manejo de autenticación"""
    
    @staticmethod
    async def login(form_data: OAuth2PasswordRequestForm, db: Session) -> Token:
        """
        Autentica un usuario y devuelve un token de acceso
        
        Args:
            form_data: Datos del formulario de login
            db: Sesión de base de datos
            
        Returns:
            Token: Token de acceso con información del usuario
            
        Raises:
            HTTPException: Si las credenciales son incorrectas
        """
        try:
            s = str(form_data.username).strip().upper()
            usuario = None
            # Solo RUT permitido
            cuerpo = ''.join(ch for ch in s if ch.isdigit())
            dv_prov = None
            if s and not s[-1].isdigit():
                dv_prov = 'K' if s[-1] == 'K' else s[-1]
            if not cuerpo or len(cuerpo) < 7 or len(cuerpo) > 8:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="RUT inválido")
            def _dv_calc(b: str) -> str:
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
            expected = _dv_calc(cuerpo)
            if dv_prov is not None and dv_prov != expected:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="RUT inválido")
            rut_full = f"{cuerpo}{expected}"
            usuario = db.query(UsuarioDB).filter(UsuarioDB.rut == rut_full).first()
            if not usuario:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Credenciales incorrectas"
                )
            
            # Verificar que el usuario esté activo
            if not usuario.activo:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario desactivado"
                )
            
            # Verificar contraseña
            if not verificar_contraseña(form_data.password, usuario.password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Credenciales incorrectas"
                )
            
            # Crear token con el RUT como 'sub' (como string)
            subject = str(usuario.rut)
            token = crear_token(data={"sub": subject})
            
            # Auditoría: login exitoso
            try:
                registrar_evento(
                    db,
                    accion="login",
                    usuario_rut=usuario.rut,
                    entidad_tipo="Usuario",
                    entidad_id=None,
                    detalle="Login exitoso",
                )
            except Exception:
                # No bloquear login si falla auditoría
                pass

            return Token(
                access_token=token,
                token_type="bearer",
                nombre=usuario.nombre,
                rut=usuario.rut,
                role=(getattr(getattr(usuario, "rol_ref", None), "nombre", None))
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno del servidor: {str(e)}"
            )

    @staticmethod
    async def login_por_orden(db: Session, rut: str, buy_order: str) -> Token:
        try:
            s = str(rut or '').strip().upper()
            cuerpo = ''.join(ch for ch in s if ch.isdigit())
            if not cuerpo or len(cuerpo) < 7 or len(cuerpo) > 8:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="RUT inválido")
            def _dv_calc(b: str) -> str:
                acc = 0; f = 2
                for ch in reversed(b):
                    acc += int(ch) * f
                    f = 2 if f == 7 else f + 1
                rest = 11 - (acc % 11)
                return '0' if rest == 11 else ('K' if rest == 10 else str(rest))
            rut_full = f"{cuerpo}{_dv_calc(cuerpo)}"
            usuario = db.query(UsuarioDB).filter(UsuarioDB.rut == rut_full).first()
            if not usuario or not usuario.activo:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario inválido")
            # Buscar pago por buy_order
            pago = db.query(PagoDB).filter(PagoDB.buy_order == str(buy_order)).first()
            if not pago:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Orden no encontrada")
            venta = db.query(VentaDB).filter(VentaDB.id_venta == pago.id_venta).first()
            if not venta:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venta no encontrada")
            # Validar correspondencia
            if venta.rut_usuario and str(rut_full) != str(venta.rut_usuario):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="La orden no corresponde al usuario")
            subject = str(usuario.rut)
            token = crear_token(data={"sub": subject})
            return Token(
                access_token=token,
                token_type="bearer",
                nombre=usuario.nombre,
                rut=usuario.rut,
                role=(getattr(getattr(usuario, "rol_ref", None), "nombre", None))
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error interno del servidor: {str(e)}")

    @staticmethod
    async def login_cliente(form_data: OAuth2PasswordRequestForm, db: Session) -> Token:
        try:
            result = await AuthController.login(form_data, db)
            from models.rol import RolDB
            from models.usuario import UsuarioDB
            rol = (
                db.query(RolDB)
                .join(UsuarioDB, UsuarioDB.id_rol == RolDB.id_rol)
                .filter(UsuarioDB.rut == str(result.rut))
                .first()
            )
            nombre = getattr(rol, 'nombre', None) or (result.role or '')
            if (nombre or '').lower() != 'cliente':
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso restringido a clientes")
            return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error interno del servidor: {str(e)}")

    @staticmethod
    async def login_trabajador(form_data: OAuth2PasswordRequestForm, db: Session) -> Token:
        try:
            result = await AuthController.login(form_data, db)
            if (result.role or '').lower() == 'cliente':
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso restringido a trabajadores")
            return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error interno del servidor: {str(e)}")
