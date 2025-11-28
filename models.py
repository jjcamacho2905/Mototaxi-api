from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    telefono = Column(String, nullable=False)
    activo = Column(Boolean, default=True)

    viajes = relationship("Viaje", back_populates="usuario")


class Conductor(Base):
    __tablename__ = "conductores"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    licencia = Column(String, nullable=True)
    activo = Column(Boolean, default=True)

    viajes = relationship("Viaje", back_populates="conductor")


class Vehiculo(Base):
    __tablename__ = "vehiculos"

    id = Column(Integer, primary_key=True, index=True)
    placa = Column(String, nullable=False)
    modelo = Column(String, nullable=True)
    activo = Column(Boolean, default=True)

    viajes = relationship("Viaje", back_populates="vehiculo")


class Viaje(Base):
    __tablename__ = "viajes"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    conductor_id = Column(Integer, ForeignKey("conductores.id"))
    vehiculo_id = Column(Integer, ForeignKey("vehiculos.id"))
    destino = Column(String, nullable=True)
    activo = Column(Boolean, default=True)

    usuario = relationship("Usuario", back_populates="viajes")
    conductor = relationship("Conductor", back_populates="viajes")
    vehiculo = relationship("Vehiculo", back_populates="viajes")
