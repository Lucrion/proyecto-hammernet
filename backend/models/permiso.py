#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional
from .base import Base


class PermisoDB(Base):
    __tablename__ = "permisos"

    id_permiso = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(100), unique=True, nullable=False)

    roles = relationship("RolPermisoDB", back_populates="permiso")


class Permiso(BaseModel):
    id_permiso: int
    descripcion: str

    class Config:
        orm_mode = True