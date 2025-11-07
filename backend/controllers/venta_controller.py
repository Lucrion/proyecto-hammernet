#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Controlador para gestión de ventas
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, and_, func
from fastapi import HTTPException
from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal
from core.auth import hash_contraseña

from models.venta import (
    VentaDB, DetalleVentaDB, MovimientoInventarioDB,
    Venta, DetalleVenta, MovimientoInventario, VentaCreate, DetalleVentaCreate
)
from models.producto import ProductoDB
from models.usuario import UsuarioDB
from controllers.auditoria_controller import registrar_evento


class VentaController:
    """Controlador para gestión de ventas"""
    
    @staticmethod
    def crear_venta(db: Session, venta_data: VentaCreate, id_usuario: int) -> Venta:
        """
        Crear una nueva venta con sus detalles y actualizar inventario
        """
        try:
            # Verificar que el usuario existe
            usuario = db.query(UsuarioDB).filter(UsuarioDB.id_usuario == id_usuario).first()
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
                id_usuario=id_usuario,
                total_venta=total_calculado,
                estado=venta_data.estado,
                observaciones=venta_data.observaciones
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
                    id_usuario=id_usuario,
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
                    usuario_actor_id=id_usuario,
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
    def obtener_ventas(db: Session, skip: int = 0, limit: int = 100, fecha_inicio: Optional[date] = None, fecha_fin: Optional[date] = None, id_usuario: Optional[int] = None) -> List[Venta]:
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
            if id_usuario:
                query = query.filter(VentaDB.id_usuario == id_usuario)
            
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
    def cancelar_venta(db: Session, id_venta: int, id_usuario: int) -> Venta:
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
                    id_usuario=id_usuario,
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
                    entidad_tipo="venta",
                    entidad_id=id_venta,
                    accion="venta_cancelada",
                    usuario_actor_id=id_usuario,
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
            id_usuario=venta.id_usuario,
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
            id_usuario=movimiento.id_usuario,
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