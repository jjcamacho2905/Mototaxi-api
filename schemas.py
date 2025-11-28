from pydantic import BaseModel, ConfigDict
from typing import Optional

# --- USUARIOS ---
class UsuarioBase(BaseModel):
    nombre: str
    telefono: str

class UsuarioCrear(UsuarioBase):
    pass

class Usuario(UsuarioBase):
    id: int
    activo: bool

    # Pydantic v2: habilita lectura desde objetos ORM (SQLAlchemy)
    model_config = ConfigDict(from_attributes=True)

# --- CONDUCTORES ---
class ConductorBase(BaseModel):
    nombre: str
    licencia: Optional[str] = None

class ConductorCrear(ConductorBase):
    pass

class Conductor(ConductorBase):
    id: int
    activo: bool

    model_config = ConfigDict(from_attributes=True)

# --- VEHICULOS ---
class VehiculoBase(BaseModel):
    placa: str
    modelo: Optional[str] = None

class VehiculoCrear(VehiculoBase):
    pass

class Vehiculo(VehiculoBase):
    id: int
    activo: bool

    model_config = ConfigDict(from_attributes=True)

# --- VIAJES ---
class ViajeBase(BaseModel):
    usuario_id: int
    conductor_id: int
    vehiculo_id: int
    destino: Optional[str] = None

class ViajeCrear(ViajeBase):
    pass

class Viaje(ViajeBase):
    id: int
    activo: bool

    model_config = ConfigDict(from_attributes=True)
