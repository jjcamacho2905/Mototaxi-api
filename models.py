from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, DateTime, func
from sqlalchemy.orm import relationship
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    telefono = Column(String, nullable=False)
    foto_path = Column(String, nullable=True)
    password_hash = Column(String, nullable=True)
    activo = Column(Boolean, default=True)

    viajes = relationship("Viaje", back_populates="usuario")


class Conductor(Base):
    __tablename__ = "conductores"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False, unique=True)  # Único para buscar por nombre
    licencia = Column(String, nullable=True)
    foto_path = Column(String, nullable=True)
    activo = Column(Boolean, default=True)

    vehiculos = relationship("Vehiculo", back_populates="conductor")
    viajes = relationship("Viaje", back_populates="conductor")


class Vehiculo(Base):
    __tablename__ = "vehiculos"

    id = Column(Integer, primary_key=True, index=True)
    placa = Column(String, nullable=False)
    modelo = Column(String, nullable=True)
    foto_path = Column(String, nullable=True)
    activo = Column(Boolean, default=True)
    
    # Relación con conductor
    conductor_id = Column(Integer, ForeignKey("conductores.id"), nullable=True)
    conductor = relationship("Conductor", back_populates="vehiculos")
    
    viajes = relationship("Viaje", back_populates="vehiculo")


class Viaje(Base):
    __tablename__ = "viajes"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    conductor_id = Column(Integer, ForeignKey("conductores.id"))
    vehiculo_id = Column(Integer, ForeignKey("vehiculos.id"))
    origen = Column(String, nullable=True)
    destino = Column(String, nullable=True)
    precio = Column(Float, nullable=True)
    fecha = Column(DateTime, nullable=False, server_default=func.now())
    estado = Column(String, nullable=False, default="pendiente")
    activo = Column(Boolean, default=True)

    usuario = relationship("Usuario", back_populates="viajes")
    conductor = relationship("Conductor", back_populates="viajes")
    vehiculo = relationship("Vehiculo", back_populates="viajes")