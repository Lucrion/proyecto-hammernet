#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Controlador para gestión de ventas
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, and_, func, or_
from fastapi import HTTPException
from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal
from core.auth import hash_contraseña

from models.venta import (
    VentaDB, DetalleVentaDB, MovimientoInventarioDB,
    Venta, DetalleVenta, MovimientoInventario, VentaCreate, DetalleVentaCreate, VentaGuestCreate
)
from models.producto import ProductoDB
from models.pago import PagoDB
from models.usuario import UsuarioDB
from models.categoria import CategoriaDB
from controllers.auditoria_controller import registrar_evento
import json


class VentaController:
    """Controlador para gestión de ventas"""
    
    @staticmethod
    def crear_venta(db: Session, venta_data: VentaCreate, rut_usuario: str) -> Venta:
        """
        Crear una nueva venta con sus detalles y actualizar inventario
        """
        try:
            # Verificar que el usuario existe
            usuario = db.query(UsuarioDB).filter(UsuarioDB.rut == str(rut_usuario)).first()
            if not usuario:
                # No crear usuarios automáticamente. Forzar registro previo.
                raise HTTPException(status_code=404, detail="Usuario no encontrado. Regístrese antes de realizar una venta")
            
            # Verificar disponibilidad de productos y calcular total
            total_calculado = Decimal('0.00')
            productos_verificados = []
            
            for detalle in venta_data.detalles:
                producto = db.query(ProductoDB).filter(ProductoDB.id_producto == detalle.id_producto).first()
                if not producto:
                    raise HTTPException(status_code=404, detail=f"Producto con ID {detalle.id_producto} no encontrado")
                
                if producto.cantidad_disponible < detalle.cantidad:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Stock insuficiente para {producto.nombre}. Disponible: {producto.cantidad_disponible}, Solicitado: {detalle.cantidad}"
                    )
                
                subtotal = detalle.precio_unitario * detalle.cantidad
                total_calculado += subtotal
                productos_verificados.append({
                    'producto': producto,
                    'detalle': detalle,
                    'subtotal': subtotal
                })
            
            # Crear la venta
            db_venta = VentaDB(
                rut_usuario=str(rut_usuario),
                total_venta=total_calculado,
                estado=venta_data.estado,
                observaciones=venta_data.observaciones,
                tipo_documento=getattr(venta_data, 'tipo_documento', None),
                folio_documento=getattr(venta_data, 'folio_documento', None),
                fecha_emision_sii=getattr(venta_data, 'fecha_emision_sii', None),
                cliente_rut=getattr(venta_data, 'cliente_rut', None)
            )
            db.add(db_venta)
            db.flush()  # Para obtener el ID de la venta
            
            # Crear detalles de venta y actualizar inventario
            for item in productos_verificados:
                producto = item['producto']
                detalle = item['detalle']
                subtotal = item['subtotal']
                
                # Crear detalle de venta
                db_detalle = DetalleVentaDB(
                    id_venta=db_venta.id_venta,
                    id_producto=detalle.id_producto,
                    cantidad=detalle.cantidad,
                    precio_unitario=detalle.precio_unitario,
                    subtotal=subtotal
                )
                db.add(db_detalle)
                
                # Actualizar inventario
                cantidad_anterior = producto.cantidad_disponible
                cantidad_nueva = cantidad_anterior - detalle.cantidad
                producto.cantidad_disponible = cantidad_nueva
                producto.fecha_ultima_venta = datetime.now()
                
                # Registrar movimiento de inventario
                movimiento = MovimientoInventarioDB(
                    id_producto=detalle.id_producto,
                    rut_usuario=str(rut_usuario),
                    id_venta=db_venta.id_venta,
                    tipo_movimiento="venta",
                    cantidad=-detalle.cantidad,  # Negativo porque es una salida
                    cantidad_anterior=cantidad_anterior,
                    cantidad_nueva=cantidad_nueva,
                    motivo=f"Venta #{db_venta.id_venta}"
                )
                db.add(movimiento)
            
            db.commit()

            # Auditoría: venta creada
            try:
                registrar_evento(
                    db,
                    entidad_tipo="venta",
                    entidad_id=db_venta.id_venta,
                    accion="venta_creada",
                    usuario_actor_id=None,
                    detalle=f"Total: {float(total_calculado)} | Detalles: {len(productos_verificados)}"
                )
            except Exception:
                pass
            
            # Cargar la venta completa con relaciones
            venta_completa = db.query(VentaDB).options(
                joinedload(VentaDB.usuario),
                joinedload(VentaDB.detalles_venta).joinedload(DetalleVentaDB.producto)
            ).filter(VentaDB.id_venta == db_venta.id_venta).first()
            
            return VentaController._construir_venta_response(venta_completa)
        
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error al crear venta: {str(e)}")

    @staticmethod
    def _get_or_create_guest_user(db: Session) -> UsuarioDB:
        """Obtiene o crea un usuario de sistema para ventas de invitado"""
        from models.rol import RolDB
        usuario = (
            db.query(UsuarioDB)
            .join(RolDB, UsuarioDB.id_rol == RolDB.id_rol)
            .filter(RolDB.nombre == "invitado", UsuarioDB.nombre == "Invitado")
            .first()
        )
        if usuario:
            return usuario
        # Crear usuario de sistema 'Invitado' sin RUT ni teléfono
        try:
            rol = db.query(RolDB).filter(RolDB.nombre == "invitado").first()
            if not rol:
                rol = RolDB(nombre="invitado")
                db.add(rol)
                db.flush()
            usuario = UsuarioDB(
                nombre="Invitado",
                rut=None,
                email=None,
                password=hash_contraseña("guest_checkout"),
                id_rol=rol.id_rol,
                activo=True
            )
            db.add(usuario)
            db.commit()
            db.refresh(usuario)
            return usuario
        except Exception:
            db.rollback()
            # Fallback: intentar obtener nuevamente por si existe tras rollback
            usuario = (
                db.query(UsuarioDB)
                .join(RolDB, UsuarioDB.id_rol == RolDB.id_rol)
                .filter(RolDB.nombre == "invitado", UsuarioDB.nombre == "Invitado")
                .first()
            )
            if usuario:
                return usuario
            raise HTTPException(status_code=500, detail="No se pudo crear usuario de invitado para ventas")

    @staticmethod
    def crear_venta_invitado(db: Session, venta_guest: VentaGuestCreate) -> Venta:
        """
        Crear una venta como invitado (sin autenticación), guardando datos esenciales del cliente en observaciones.
        """
        try:
            # Usar usuario de sistema para atribuir la venta y movimientos
            usuario_guest = VentaController._get_or_create_guest_user(db)
            rut_usuario = None

            # Verificar disponibilidad de productos y calcular total
            total_calculado = Decimal('0.00')
            productos_verificados = []

            for detalle in venta_guest.detalles:
                producto = db.query(ProductoDB).filter(ProductoDB.id_producto == detalle.id_producto).first()
                if not producto:
                    raise HTTPException(status_code=404, detail=f"Producto con ID {detalle.id_producto} no encontrado")
                if producto.cantidad_disponible < detalle.cantidad:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Stock insuficiente para {producto.nombre}. Disponible: {producto.cantidad_disponible}, Solicitado: {detalle.cantidad}"
                    )
                subtotal = detalle.precio_unitario * detalle.cantidad
                total_calculado += subtotal
                productos_verificados.append({'producto': producto, 'detalle': detalle, 'subtotal': subtotal})

            # Validar total enviado vs calculado (tolerancia mínima)
            try:
                enviado = Decimal(str(venta_guest.total_venta))
            except Exception:
                enviado = total_calculado
            if enviado != total_calculado:
                # Ajustar al calculado para coherencia
                enviado = total_calculado

            # Preparar observaciones con guest_info
            obs = venta_guest.observaciones or ""
            try:
                info = venta_guest.guest_info or {}
                etiqueta = f"VENTA_INVITADO:{json.dumps(info, ensure_ascii=False)}"
                obs = f"{obs}\n{etiqueta}".strip()
            except Exception:
                pass

            # Crear la venta
            db_venta = VentaDB(
                rut_usuario=rut_usuario,
                total_venta=enviado,
                estado=venta_guest.estado,
                observaciones=obs
            )
            db.add(db_venta)
            db.flush()

            # Crear detalles y movimientos
            for item in productos_verificados:
                producto = item['producto']
                detalle = item['detalle']
                subtotal = item['subtotal']

                db_detalle = DetalleVentaDB(
                    id_venta=db_venta.id_venta,
                    id_producto=detalle.id_producto,
                    cantidad=detalle.cantidad,
                    precio_unitario=detalle.precio_unitario,
                    subtotal=subtotal
                )
                db.add(db_detalle)

                cantidad_anterior = producto.cantidad_disponible
                cantidad_nueva = cantidad_anterior - detalle.cantidad
                producto.cantidad_disponible = cantidad_nueva
                producto.fecha_ultima_venta = datetime.now()

                movimiento = MovimientoInventarioDB(
                    id_producto=detalle.id_producto,
                    rut_usuario=rut_usuario,
                    id_venta=db_venta.id_venta,
                    tipo_movimiento="venta",
                    cantidad=-detalle.cantidad,
                    cantidad_anterior=cantidad_anterior,
                    cantidad_nueva=cantidad_nueva,
                    motivo=f"Venta invitado #{db_venta.id_venta}"
                )
                db.add(movimiento)

            db.commit()

            # Auditoría
            try:
                registrar_evento(
                    db,
                    accion="venta_invitado_creada",
                    usuario_rut=None,
                    entidad_tipo="venta",
                    entidad_id=db_venta.id_venta,
                    detalle=f"Total: {float(enviado)} | Detalles: {len(productos_verificados)}"
                )
            except Exception:
                pass

            venta_completa = db.query(VentaDB).options(
                joinedload(VentaDB.usuario),
                joinedload(VentaDB.detalles_venta).joinedload(DetalleVentaDB.producto)
            ).filter(VentaDB.id_venta == db_venta.id_venta).first()

            return VentaController._construir_venta_response(venta_completa)

        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error al crear venta como invitado: {str(e)}")
    
    @staticmethod
    def obtener_ventas(db: Session, skip: int = 0, limit: int = 100, fecha_inicio: Optional[date] = None, fecha_fin: Optional[date] = None, rut_usuario: Optional[str] = None) -> List[Venta]:
        """
        Obtener lista de ventas con filtros opcionales
        """
        try:
            query = db.query(VentaDB).options(
                joinedload(VentaDB.usuario),
                joinedload(VentaDB.detalles_venta).joinedload(DetalleVentaDB.producto)
            )
            
            # Aplicar filtros de fecha si se proporcionan
            if fecha_inicio:
                query = query.filter(func.date(VentaDB.fecha_venta) >= fecha_inicio)
            if fecha_fin:
                query = query.filter(func.date(VentaDB.fecha_venta) <= fecha_fin)
            
            # Aplicar filtro de usuario si se proporciona
            if rut_usuario:
                query = query.filter(VentaDB.rut_usuario == str(rut_usuario))
            
            ventas = query.order_by(desc(VentaDB.fecha_venta)).offset(skip).limit(limit).all()
            
            return [VentaController._construir_venta_response(venta) for venta in ventas]
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al obtener ventas: {str(e)}")
    
    @staticmethod
    def obtener_venta_por_id(db: Session, id_venta: int) -> Venta:
        """
        Obtener una venta específica por ID
        """
        try:
            venta = db.query(VentaDB).options(
                joinedload(VentaDB.usuario),
                joinedload(VentaDB.detalles_venta).joinedload(DetalleVentaDB.producto)
            ).filter(VentaDB.id_venta == id_venta).first()
            
            if not venta:
                raise HTTPException(status_code=404, detail="Venta no encontrada")
            
            return VentaController._construir_venta_response(venta)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al obtener venta: {str(e)}")
    
    @staticmethod
    def cancelar_venta(db: Session, id_venta: int, rut_usuario: str) -> Venta:
        """
        Cancelar una venta y revertir el inventario
        """
        try:
            venta = db.query(VentaDB).options(
                joinedload(VentaDB.detalles_venta).joinedload(DetalleVentaDB.producto)
            ).filter(VentaDB.id_venta == id_venta).first()
            
            if not venta:
                raise HTTPException(status_code=404, detail="Venta no encontrada")
            
            if venta.estado == "cancelada":
                raise HTTPException(status_code=400, detail="La venta ya está cancelada")
            
            # Revertir inventario
            for detalle in venta.detalles_venta:
                producto = detalle.producto
                cantidad_anterior = producto.cantidad_disponible
                cantidad_nueva = cantidad_anterior + detalle.cantidad
                producto.cantidad_disponible = cantidad_nueva
                
                # Registrar movimiento de reversión
                movimiento = MovimientoInventarioDB(
                    id_producto=detalle.id_producto,
                    rut_usuario=str(rut_usuario),
                    id_venta=id_venta,
                    tipo_movimiento="devolucion",
                    cantidad=detalle.cantidad,  # Positivo porque es una entrada
                    cantidad_anterior=cantidad_anterior,
                    cantidad_nueva=cantidad_nueva,
                    motivo=f"Cancelación de venta #{id_venta}"
                )
                db.add(movimiento)
            
            # Actualizar estado de la venta
            venta.estado = "cancelada"
            venta.fecha_actualizacion = datetime.now()
            
            db.commit()

            # Auditoría: venta cancelada
            try:
                registrar_evento(
                    db,
                    accion="venta_cancelada",
                    usuario_rut=str(rut_usuario),
                    entidad_tipo="venta",
                    entidad_id=id_venta,
                    detalle="Inventario revertido por cancelación"
                )
            except Exception:
                pass
            
            return VentaController._construir_venta_response(venta)
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error al cancelar venta: {str(e)}")

    @staticmethod
    def completar_venta(db: Session, id_venta: int, usuario_admin_rut: str = None, metodo: str = None) -> Venta:
        """
        Marcar una venta como completada (entregada). No modifica inventario.
        Registra auditoría con el usuario administrador y método de entrega.
        """
        try:
            venta = db.query(VentaDB).options(
                joinedload(VentaDB.usuario),
                joinedload(VentaDB.detalles_venta).joinedload(DetalleVentaDB.producto)
            ).filter(VentaDB.id_venta == id_venta).first()

            if not venta:
                raise HTTPException(status_code=404, detail="Venta no encontrada")

            if venta.estado == "completada":
                return VentaController._construir_venta_response(venta)

            venta.estado = "completada"
            venta.fecha_actualizacion = datetime.now()
            db.commit()

            try:
                detalle = f"Entrega completada"
                if metodo:
                    detalle += f" | metodo={metodo}"
                if usuario_admin_rut:
                    detalle += f" | admin={usuario_admin_rut}"
                registrar_evento(
                    db,
                    accion="venta_completada",
                    usuario_rut=str(usuario_admin_rut) if usuario_admin_rut else None,
                    entidad_tipo="venta",
                    entidad_id=id_venta,
                    detalle=detalle
                )
            except Exception:
                pass
            return VentaController._construir_venta_response(venta)
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error al completar venta: {str(e)}")
    @staticmethod
    def eliminar_compras_de_clientes(db: Session) -> dict:
        """
        Elimina todas las ventas asociadas a usuarios con role 'cliente'.
        Incluye eliminación de pagos y movimientos de inventario vinculados a esas ventas.
        """
        try:
            from models.rol import RolDB
            clientes = (
                db.query(UsuarioDB.rut)
                .join(RolDB, UsuarioDB.id_rol == RolDB.id_rol)
                .filter(RolDB.nombre == 'cliente')
                .all()
            )
            cliente_ruts = [row.rut for row in clientes]
            if not cliente_ruts:
                return {"ventas_eliminadas": 0, "pagos_eliminados": 0, "movimientos_eliminados": 0, "detalles_eliminados": 0}

            ventas = db.query(VentaDB.id_venta).filter(
                or_(VentaDB.cliente_rut.in_(cliente_ruts), VentaDB.rut_usuario.in_(cliente_ruts))
            ).all()
            venta_ids = [row.id_venta for row in ventas]
            if not venta_ids:
                return {"ventas_eliminadas": 0, "pagos_eliminados": 0, "movimientos_eliminados": 0, "detalles_eliminados": 0}

            movimientos_eliminados = db.query(MovimientoInventarioDB).filter(MovimientoInventarioDB.id_venta.in_(venta_ids)).delete(synchronize_session=False)
            pagos_eliminados = db.query(PagoDB).filter(PagoDB.id_venta.in_(venta_ids)).delete(synchronize_session=False)
            detalles_eliminados = db.query(DetalleVentaDB).filter(DetalleVentaDB.id_venta.in_(venta_ids)).delete(synchronize_session=False)
            ventas_eliminadas = db.query(VentaDB).filter(VentaDB.id_venta.in_(venta_ids)).delete(synchronize_session=False)
            db.commit()

            # Auditoría sencilla
            try:
                registrar_evento(
                    db,
                    entidad_tipo="venta",
                    entidad_id=None,
                    accion="elim_compras_clientes",
                    usuario_actor_id=None,
                    detalle=f"ventas={ventas_eliminadas}, pagos={pagos_eliminados}, movimientos={movimientos_eliminados}, detalles={detalles_eliminados}"
                )
            except Exception:
                pass

            return {
                "ventas_eliminadas": int(ventas_eliminadas or 0),
                "pagos_eliminados": int(pagos_eliminados or 0),
                "movimientos_eliminados": int(movimientos_eliminados or 0),
                "detalles_eliminados": int(detalles_eliminados or 0),
            }
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error al eliminar compras de clientes: {str(e)}")

    @staticmethod
    def set_envio_estado(db: Session, id_venta: int, estado_envio: str) -> Venta:
        try:
            venta = db.query(VentaDB).filter(VentaDB.id_venta == id_venta).first()
            if not venta:
                raise HTTPException(status_code=404, detail="Venta no encontrada")
            estado_envio = (estado_envio or '').strip().lower()
            if estado_envio not in { 'pendiente', 'preparando', 'en camino', 'entregado' }:
                raise HTTPException(status_code=400, detail="Estado de envío inválido")
            obs = (venta.observaciones or '')
            tag = 'ENVIO_ESTADO:'
            # Reemplazar o agregar
            if tag in obs:
                parts = obs.split('\n')
                parts = [p for p in parts if not p.startswith(tag)]
                parts.append(f"{tag}{estado_envio}")
                obs = '\n'.join(parts)
            else:
                obs = (obs + '\n' if obs else '') + f"{tag}{estado_envio}"
            venta.observaciones = obs
            venta.fecha_actualizacion = datetime.now()
            db.commit()
            return VentaController._construir_venta_response(venta)
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error al actualizar estado de envío: {str(e)}")
    
    @staticmethod
    def obtener_movimientos_inventario(db: Session, skip: int = 0, limit: int = 100, id_producto: Optional[int] = None) -> List[MovimientoInventario]:
        """
        Obtener movimientos de inventario con filtros opcionales
        """
        try:
            query = db.query(MovimientoInventarioDB).options(
                joinedload(MovimientoInventarioDB.producto),
                joinedload(MovimientoInventarioDB.usuario),
                joinedload(MovimientoInventarioDB.venta)
            )
            
            if id_producto:
                query = query.filter(MovimientoInventarioDB.id_producto == id_producto)
            
            movimientos = query.order_by(desc(MovimientoInventarioDB.fecha_movimiento)).offset(skip).limit(limit).all()
            
            return [VentaController._construir_movimiento_response(mov) for mov in movimientos]
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al obtener movimientos: {str(e)}")
    
    @staticmethod
    def obtener_estadisticas_ventas(db: Session, fecha_inicio: Optional[date] = None, fecha_fin: Optional[date] = None) -> dict:
        """
        Obtener estadísticas de ventas
        """
        try:
            query = db.query(VentaDB)
            
            if fecha_inicio:
                query = query.filter(func.date(VentaDB.fecha_venta) >= fecha_inicio)
            if fecha_fin:
                query = query.filter(func.date(VentaDB.fecha_venta) <= fecha_fin)
            
            # Estadísticas básicas
            cantidad_ventas = query.filter(VentaDB.estado == "completada").count()
            total_ingresos = query.filter(VentaDB.estado == "completada").with_entities(func.sum(VentaDB.total_venta)).scalar() or 0
            ventas_canceladas = query.filter(VentaDB.estado == "cancelada").count()
            
            # Promedio de venta
            promedio_venta = total_ingresos / cantidad_ventas if cantidad_ventas > 0 else 0
            
            # Productos vendidos (suma de cantidades de detalles de ventas completadas)
            productos_vendidos = db.query(func.sum(DetalleVentaDB.cantidad)).join(VentaDB).filter(
                VentaDB.estado == "completada"
            )
            
            if fecha_inicio:
                productos_vendidos = productos_vendidos.filter(func.date(VentaDB.fecha_venta) >= fecha_inicio)
            if fecha_fin:
                productos_vendidos = productos_vendidos.filter(func.date(VentaDB.fecha_venta) <= fecha_fin)
                
            productos_vendidos = productos_vendidos.scalar() or 0
            
            return {
                "total_ventas": float(total_ingresos),  # Total en dinero
                "cantidad_ventas": cantidad_ventas,     # Número de ventas
                "productos_vendidos": int(productos_vendidos),  # Cantidad de productos
                "promedio_venta": float(promedio_venta),
                "ventas_canceladas": ventas_canceladas
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")

    @staticmethod
    def obtener_ventas_por_dia(
        db: Session,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
    ) -> list:
        """Agrupa ventas por día con ingresos y cantidad.

        Retorna lista de dicts: {fecha: date, ingresos: float, cantidad: int}
        """
        try:
            # Usar func.date para agrupar por día (compatible con SQLite/Postgres)
            query = db.query(
                func.date(VentaDB.fecha_venta).label("fecha"),
                func.sum(VentaDB.total_venta).label("ingresos"),
                func.count(VentaDB.id_venta).label("cantidad"),
            ).filter(VentaDB.estado == "completada")

            if fecha_inicio:
                query = query.filter(func.date(VentaDB.fecha_venta) >= fecha_inicio)
            if fecha_fin:
                query = query.filter(func.date(VentaDB.fecha_venta) <= fecha_fin)

            query = query.group_by(func.date(VentaDB.fecha_venta)).order_by(func.date(VentaDB.fecha_venta))

            resultados = query.all()
            return [
                {
                    "fecha": r[0],
                    "ingresos": float(r[1] or 0),
                    "cantidad": int(r[2] or 0),
                }
                for r in resultados
            ]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al agrupar ventas por día: {str(e)}")

    @staticmethod
    def obtener_top_productos(
        db: Session,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
        limit: int = 5,
    ) -> list:
        """Obtiene top productos por unidades vendidas y ventas totales.

        Retorna lista de dicts: {id_producto, nombre, unidades, ventas}
        """
        try:
            query = (
                db.query(
                    DetalleVentaDB.id_producto.label("id_producto"),
                    func.coalesce(func.sum(DetalleVentaDB.cantidad), 0).label("unidades"),
                    func.coalesce(func.sum(DetalleVentaDB.subtotal), 0).label("ventas"),
                )
                .join(VentaDB, DetalleVentaDB.id_venta == VentaDB.id_venta)
                .filter(VentaDB.estado == "completada")
            )

            if fecha_inicio:
                query = query.filter(func.date(VentaDB.fecha_venta) >= fecha_inicio)
            if fecha_fin:
                query = query.filter(func.date(VentaDB.fecha_venta) <= fecha_fin)

            query = (
                query.group_by(DetalleVentaDB.id_producto)
                .order_by(desc("unidades"))
                .limit(limit)
            )

            resultados = query.all()

            # Enriquecer con nombre de producto
            ids = [r[0] for r in resultados]
            nombres = {}
            if ids:
                for p in db.query(ProductoDB.id_producto, ProductoDB.nombre).filter(ProductoDB.id_producto.in_(ids)).all():
                    nombres[p[0]] = p[1]

            return [
                {
                    "id_producto": int(r[0]),
                    "nombre": nombres.get(int(r[0]), None),
                    "unidades": int(r[1] or 0),
                    "ventas": float(r[2] or 0),
                }
                for r in resultados
            ]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al obtener top productos: {str(e)}")

    @staticmethod
    def obtener_ventas_por_categoria(
        db: Session,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
    ) -> list:
        try:
            query = (
                db.query(
                    ProductoDB.id_categoria.label("id_categoria"),
                    func.coalesce(func.sum(DetalleVentaDB.subtotal), 0).label("ingresos"),
                    func.coalesce(func.sum(DetalleVentaDB.cantidad), 0).label("cantidad"),
                )
                .join(VentaDB, DetalleVentaDB.id_venta == VentaDB.id_venta)
                .join(ProductoDB, DetalleVentaDB.id_producto == ProductoDB.id_producto)
                .filter(VentaDB.estado == "completada")
            )

            if fecha_inicio:
                query = query.filter(func.date(VentaDB.fecha_venta) >= fecha_inicio)
            if fecha_fin:
                query = query.filter(func.date(VentaDB.fecha_venta) <= fecha_fin)

            query = query.group_by(ProductoDB.id_categoria)
            resultados = query.all()

            ids = [int(r[0]) for r in resultados if r[0] is not None]
            nombres = {}
            if ids:
                for c in db.query(CategoriaDB.id_categoria, CategoriaDB.nombre).filter(CategoriaDB.id_categoria.in_(ids)).all():
                    nombres[c[0]] = c[1]

            return [
                {
                    "id_categoria": int(r[0]) if r[0] is not None else None,
                    "categoria": nombres.get(int(r[0]), "Sin categoría") if r[0] is not None else "Sin categoría",
                    "ingresos": float(r[1] or 0),
                    "cantidad": int(r[2] or 0),
                }
                for r in resultados
            ]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al agrupar ventas por categoría: {str(e)}")
    
    @staticmethod
    def _construir_venta_response(venta: VentaDB) -> Venta:
        """
        Construir respuesta de venta con todos los campos necesarios
        """
        detalles = []
        for detalle in venta.detalles_venta:
            detalles.append(DetalleVenta(
                id_detalle=detalle.id_detalle,
                id_venta=detalle.id_venta,
                id_producto=detalle.id_producto,
                cantidad=detalle.cantidad,
                precio_unitario=detalle.precio_unitario,
                subtotal=detalle.subtotal,
                fecha_creacion=detalle.fecha_creacion,
                producto_nombre=detalle.producto.nombre if detalle.producto else None
            ))
        
        return Venta(
            id_venta=venta.id_venta,
            rut_usuario=venta.rut_usuario,
            fecha_venta=venta.fecha_venta,
            total_venta=venta.total_venta,
            estado=venta.estado,
            observaciones=venta.observaciones,
            fecha_creacion=venta.fecha_creacion,
            fecha_actualizacion=venta.fecha_actualizacion,
            usuario=venta.usuario.nombre if venta.usuario else None,
            detalles_venta=detalles
        )
    
    @staticmethod
    def _construir_movimiento_response(movimiento: MovimientoInventarioDB) -> MovimientoInventario:
        """
        Construir respuesta de movimiento de inventario
        """
        return MovimientoInventario(
            id_movimiento=movimiento.id_movimiento,
            id_producto=movimiento.id_producto,
            rut_usuario=movimiento.rut_usuario,
            id_venta=movimiento.id_venta,
            tipo_movimiento=movimiento.tipo_movimiento,
            cantidad=movimiento.cantidad,
            cantidad_anterior=movimiento.cantidad_anterior,
            cantidad_nueva=movimiento.cantidad_nueva,
            motivo=movimiento.motivo,
            fecha_movimiento=movimiento.fecha_movimiento,
            fecha_creacion=movimiento.fecha_creacion,
            producto_nombre=movimiento.producto.nombre if movimiento.producto else None,
            usuario_nombre=movimiento.usuario.nombre if movimiento.usuario else None
        )
