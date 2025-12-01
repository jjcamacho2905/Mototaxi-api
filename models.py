from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, DateTime, func
from sqlalchemy.orm import relationship
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    # Nombre de la persona (se usará también para login simple)
    nombre = Column(String, nullable=False)
    telefono = Column(String, nullable=False)
    # Ruta del archivo multimedia (foto del usuario)
    foto_path = Column(String, nullable=True)
    # Almacenamos el hash de la contraseña (nunca el texto plano)
    password_hash = Column(String, nullable=True)
    activo = Column(Boolean, default=True)

    viajes = relationship("Viaje", back_populates="usuario")


class Conductor(Base):
    __tablename__ = "conductores"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    licencia = Column(String, nullable=True)
    # Ruta del archivo multimedia (foto del conductor)
    foto_path = Column(String, nullable=True)
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
    origen = Column(String, nullable=True)
    destino = Column(String, nullable=True)
    precio = Column(Float, nullable=True)
    fecha = Column(DateTime, nullable=False, server_default=func.now())
    estado = Column(String, nullable=False, default="pendiente")
    activo = Column(Boolean, default=True)

    usuario = relationship("Usuario", back_populates="viajes")
    conductor = relationship("Conductor", back_populates="viajes")
    vehiculo = relationship("Vehiculo", back_populates="viajes")
