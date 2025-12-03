from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
from typing import Optional
from datetime import datetime

# --- USUARIOS ---
class UsuarioBase(BaseModel):
    nombre: str
    telefono: str
    foto_path: Optional[str] = None

class UsuarioCrear(UsuarioBase):
    # Contraseña en texto plano sólo para recepción; se guardará hasheada
    contrasena: str

    # Validación simple: limitar longitud para evitar contraseñas excesivas
    # (bcrypt puro limita a 72 bytes; con bcrypt_sha256 ya no aplica, pero dejamos una cota razonable)
    def model_post_init(self, __context):
        if len(self.contrasena) > 256:
            raise ValueError("La contraseña es demasiado larga (máximo 256 caracteres)")

class Usuario(UsuarioBase):
    id: int
    activo: bool

    # Pydantic v2: habilita lectura desde objetos ORM (SQLAlchemy)
    model_config = ConfigDict(from_attributes=True)

# --- CONDUCTORES ---
class ConductorBase(BaseModel):
    nombre: str
    licencia: Optional[str] = None
    foto_path: Optional[str] = None

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
    origen: Optional[str] = None
    destino: Optional[str] = None
    precio: Optional[float] = None
    fecha: Optional[datetime] = None
    estado: Optional[str] = None

    @field_validator('precio')
    @classmethod
    def precio_positivo(cls, v):
        if v is not None and v < 0:
            raise ValueError("El precio debe ser positivo")
        return v

class ViajeCrear(ViajeBase):
    pass

class ViajeActualizar(BaseModel):
    """Schema para actualizar solo el estado de un viaje"""
    estado: str
    
    @field_validator('estado')
    @classmethod
    def validar_estado(cls, v):
        estados_validos = ['pendiente', 'en_curso', 'completado', 'cancelado']
        if v not in estados_validos:
            raise ValueError(f"Estado debe ser uno de: {', '.join(estados_validos)}")
        return v

class Viaje(ViajeBase):
    id: int
    activo: bool

    model_config = ConfigDict(from_attributes=True)