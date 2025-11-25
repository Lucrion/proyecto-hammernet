#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional
from .base import Base


class RolDB(Base):
    __tablename__ = "roles"

    id_rol = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)

    usuarios = relationship("UsuarioDB", back_populates="rol_ref")
    permisos = relationship("RolPermisoDB", back_populates="rol")


class Rol(BaseModel):
    id_rol: int
    nombre: str

    class Config:
        orm_mode = True