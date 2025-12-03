from sqlalchemy.orm import Session
import models
import schemas
from passlib.context import CryptContext
from business_rules import (
    aplicar_reglas_usuario,
    aplicar_reglas_conductor,
    aplicar_reglas_vehiculo,
    aplicar_reglas_viaje,
    BusinessRules
)

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# ======================
# 🔐 Funciones de seguridad
# ======================
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str):
    return pwd_context.verify(password, hashed)

# ======================
# 👤 CRUD USUARIOS (MEJORADO)
# ======================
def crear_usuario(db: Session, usuario: schemas.UsuarioCrear):
    """
    Crea un usuario con validaciones de reglas de negocio.
    """
    aplicar_reglas_usuario(
        db, 
        usuario.nombre, 
        usuario.telefono, 
        usuario.contrasena,
        es_nuevo=True
    )
    
    nombre_limpio = usuario.nombre.strip()
    telefono_limpio = usuario.telefono.strip()
    
    nuevo = models.Usuario(
        nombre=nombre_limpio,
        telefono=telefono_limpio,
        foto_path=getattr(usuario, 'foto_path', None),
        password_hash=hash_password(usuario.contrasena),
        activo=True,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


def autenticar_usuario(db: Session, nombre: str, contrasena: str):
    """Autentica usuario por nombre y contraseña."""
    usuario = db.query(models.Usuario).filter(
        models.Usuario.nombre == nombre.strip()
    ).first()
    
    if not usuario:
        return None
    
    if not usuario.activo:
        return None
    
    if not usuario.password_hash:
        return None
    
    if not pwd_context.verify(contrasena, usuario.password_hash):
        return None
    
    return usuario


def obtener_usuarios(db: Session):
    """Obtiene todos los usuarios activos"""
    return db.query(models.Usuario).filter(
        models.Usuario.activo == True
    ).all()


def obtener_usuarios_por_estado(db: Session, activo: bool, skip: int = 0, limit: int = 100):
    """Obtiene usuarios filtrados por estado"""
    return (
        db.query(models.Usuario)
        .filter(models.Usuario.activo == activo)
        .offset(skip)
        .limit(limit)
        .all()
    )


def buscar_usuario_por_nombre(db: Session, nombre: str):
    """Busca usuarios por nombre (búsqueda parcial, case-insensitive)."""
    BusinessRules.validar_termino_busqueda(nombre)
    
    return db.query(models.Usuario).filter(
        models.Usuario.nombre.ilike(f"%{nombre.strip()}%"),
        models.Usuario.activo == True
    ).all()


def inactivar_usuario(db: Session, usuario_id: int):
    """Inactiva un usuario (soft delete)."""
    usuario = db.query(models.Usuario).filter(
        models.Usuario.id == usuario_id
    ).first()
    
    if not usuario:
        return None
    
    viajes_activos = db.query(models.Viaje).filter(
        models.Viaje.usuario_id == usuario_id,
        models.Viaje.estado.in_(['pendiente', 'en_curso']),
        models.Viaje.activo == True
    ).count()
    
    if viajes_activos > 0:
        from fastapi import HTTPException
        raise HTTPException(
            400,
            f"No se puede inactivar: el usuario tiene {viajes_activos} viaje(s) activo(s)"
        )
    
    usuario.activo = False
    db.commit()
    db.refresh(usuario)
    return usuario


def eliminar_usuario(db: Session, usuario_id: int):
    """Elimina un usuario (soft delete)."""
    return inactivar_usuario(db, usuario_id)


# ==========================
# 🏍️ CRUD CONDUCTORES (MEJORADO)
# ==========================

def crear_conductor(db: Session, conductor: schemas.ConductorCrear):
    """Crea un conductor con validaciones."""
    aplicar_reglas_conductor(
        db,
        conductor.nombre,
        conductor.licencia,
        es_nuevo=True
    )
    
    nombre_limpio = conductor.nombre.strip()
    licencia_limpia = conductor.licencia.strip().upper() if conductor.licencia else None
    
    nuevo_conductor = models.Conductor(
        nombre=nombre_limpio,
        licencia=licencia_limpia,
        activo=True
    )
    db.add(nuevo_conductor)
    db.commit()
    db.refresh(nuevo_conductor)
    return nuevo_conductor


def obtener_conductores(db: Session):
    """Obtiene todos los conductores activos"""
    return db.query(models.Conductor).filter(
        models.Conductor.activo == True
    ).all()


def obtener_conductores_por_estado(db: Session, activo: bool):
    """Obtiene conductores filtrados por estado"""
    return db.query(models.Conductor).filter(
        models.Conductor.activo == activo
    ).all()


def inactivar_conductor(db: Session, conductor_id: int):
    """Inactiva un conductor."""
    conductor = db.query(models.Conductor).filter(
        models.Conductor.id == conductor_id
    ).first()
    
    if not conductor:
        return None
    
    viajes_activos = db.query(models.Viaje).filter(
        models.Viaje.conductor_id == conductor_id,
        models.Viaje.estado.in_(['pendiente', 'en_curso']),
        models.Viaje.activo == True
    ).count()
    
    if viajes_activos > 0:
        from fastapi import HTTPException
        raise HTTPException(
            400,
            f"No se puede inactivar: el conductor tiene {viajes_activos} viaje(s) activo(s)"
        )
    
    conductor.activo = False
    db.commit()
    db.refresh(conductor)
    return conductor


def eliminar_conductor(db: Session, conductor_id: int):
    """Elimina un conductor (soft delete)"""
    return inactivar_conductor(db, conductor_id)


# ==========================
# 🚘 CRUD VEHÍCULOS (MEJORADO)
# ==========================

def crear_vehiculo(db: Session, vehiculo: schemas.VehiculoCrear):
    """Crea un vehículo con validaciones."""
    aplicar_reglas_vehiculo(db, vehiculo.placa, es_nuevo=True)
    
    placa_limpia = vehiculo.placa.strip().upper().replace("-", "").replace(" ", "")
    
    nuevo_vehiculo = models.Vehiculo(
        placa=placa_limpia,
        modelo=vehiculo.modelo.strip() if vehiculo.modelo else None,
        activo=True
    )
    db.add(nuevo_vehiculo)
    db.commit()
    db.refresh(nuevo_vehiculo)
    return nuevo_vehiculo


def obtener_vehiculos(db: Session):
    """Obtiene todos los vehículos activos"""
    return db.query(models.Vehiculo).filter(
        models.Vehiculo.activo == True
    ).all()


def obtener_vehiculos_por_estado(db: Session, activo: bool):
    """Obtiene vehículos filtrados por estado"""
    return db.query(models.Vehiculo).filter(
        models.Vehiculo.activo == activo
    ).all()


def buscar_vehiculo_por_placa(db: Session, placa: str):
    """Busca vehículos por placa (búsqueda parcial)."""
    BusinessRules.validar_termino_busqueda(placa)
    
    placa_limpia = placa.strip().upper().replace("-", "").replace(" ", "")
    
    return db.query(models.Vehiculo).filter(
        models.Vehiculo.placa.ilike(f"%{placa_limpia}%"),
        models.Vehiculo.activo == True
    ).all()


def inactivar_vehiculo(db: Session, vehiculo_id: int):
    """Inactiva un vehículo."""
    vehiculo = db.query(models.Vehiculo).filter(
        models.Vehiculo.id == vehiculo_id
    ).first()
    
    if not vehiculo:
        return None
    
    viajes_activos = db.query(models.Viaje).filter(
        models.Viaje.vehiculo_id == vehiculo_id,
        models.Viaje.estado.in_(['pendiente', 'en_curso']),
        models.Viaje.activo == True
    ).count()
    
    if viajes_activos > 0:
        from fastapi import HTTPException
        raise HTTPException(
            400,
            f"No se puede inactivar: el vehículo tiene {viajes_activos} viaje(s) activo(s)"
        )
    
    vehiculo.activo = False
    db.commit()
    db.refresh(vehiculo)
    return vehiculo


def eliminar_vehiculo(db: Session, vehiculo_id: int):
    """Elimina un vehículo (soft delete)"""
    return inactivar_vehiculo(db, vehiculo_id)


# ==========================
# 🚖 CRUD VIAJES (MEJORADO)
# ==========================

def crear_viaje(db: Session, viaje: schemas.ViajeCrear):
    """Crea un viaje con todas las validaciones de negocio."""
    aplicar_reglas_viaje(
        db,
        viaje.usuario_id,
        viaje.conductor_id,
        viaje.vehiculo_id,
        viaje.origen or "Centro Supatá",
        viaje.destino or "Destino",
        viaje.precio or 5000.0,
        viaje.estado or "pendiente"
    )
    
    origen_limpio = viaje.origen.strip() if viaje.origen else "Centro Supatá"
    destino_limpio = viaje.destino.strip() if viaje.destino else None
    estado = (viaje.estado or 'pendiente').strip().lower()
    
    nuevo_viaje = models.Viaje(
        origen=origen_limpio,
        destino=destino_limpio,
        precio=viaje.precio,
        fecha=viaje.fecha,
        estado=estado,
        conductor_id=viaje.conductor_id,
        vehiculo_id=viaje.vehiculo_id,
        usuario_id=viaje.usuario_id,
        activo=True,
    )
    db.add(nuevo_viaje)
    db.commit()
    db.refresh(nuevo_viaje)
    return nuevo_viaje


def obtener_viajes(db: Session):
    """Obtiene todos los viajes activos"""
    return db.query(models.Viaje).filter(
        models.Viaje.activo == True
    ).all()


def actualizar_estado_viaje(db: Session, viaje_id: int, nuevo_estado: str):
    """Actualiza el estado de un viaje."""
    viaje = db.query(models.Viaje).filter(
        models.Viaje.id == viaje_id
    ).first()
    
    if not viaje:
        return None
    
    BusinessRules.validar_estado_viaje(nuevo_estado)
    BusinessRules.validar_cambio_estado_viaje(viaje.estado, nuevo_estado)
    
    viaje.estado = nuevo_estado
    db.commit()
    db.refresh(viaje)
    return viaje


def eliminar_viaje(db: Session, viaje_id: int):
    """Elimina un viaje."""
    viaje = db.query(models.Viaje).filter(
        models.Viaje.id == viaje_id
    ).first()
    
    if not viaje:
        return None
    
    if viaje.estado in ['en_curso', 'completado']:
        from fastapi import HTTPException
        raise HTTPException(
            400,
            f"No se puede eliminar un viaje en estado '{viaje.estado}'"
        )
    
    db.delete(viaje)
    db.commit()
    return viaje