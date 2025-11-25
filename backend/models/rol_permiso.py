#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class RolPermisoDB(Base):
    __tablename__ = "rol_permiso"

    id_rol = Column(Integer, ForeignKey("roles.id_rol"), primary_key=True)
    id_permiso = Column(Integer, ForeignKey("permisos.id_permiso"), primary_key=True)

    rol = relationship("RolDB", back_populates="permisos")
    permiso = relationship("PermisoDB", back_populates="roles")