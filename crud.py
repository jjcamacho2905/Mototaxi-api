from sqlalchemy.orm import Session
from fastapi import HTTPException
import models, schemas
from passlib.context import CryptContext
import re

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# ======================
# 🔐 Funciones de seguridad
# ======================
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str):
    return pwd_context.verify(password, hashed)

# ======================
# 📋 VALIDACIONES
# ======================

def validar_nombre(nombre: str) -> str:
    """Valida y limpia el nombre"""
    if not nombre or not nombre.strip():
        raise HTTPException(400, "El nombre no puede estar vacío")
    nombre = nombre.strip()
    if len(nombre) < 3:
        raise HTTPException(400, "El nombre debe tener al menos 3 caracteres")
    if len(nombre) > 100:
        raise HTTPException(400, "El nombre es demasiado largo")
    return nombre

def validar_telefono(telefono: str) -> str:
    """Valida y limpia el teléfono"""
    if not telefono or not telefono.strip():
        raise HTTPException(400, "El teléfono no puede estar vacío")
    telefono = telefono.strip()
    return telefono

def validar_licencia(licencia: str) -> str:
    """Valida y limpia la licencia"""
    if not licencia or not licencia.strip():
        # Permitir licencia vacía
        return None
    licencia = licencia.strip().upper()
    if len(licencia) < 2:
        raise HTTPException(400, "La licencia debe tener al menos 2 caracteres")
    return licencia

def validar_placa(placa: str) -> str:
    """Valida y limpia la placa"""
    if not placa or not placa.strip():
        raise HTTPException(400, "La placa no puede estar vacía")
    placa = placa.strip().upper().replace("-", "").replace(" ", "")
    if len(placa) < 4:
        raise HTTPException(400, "La placa es demasiado corta")
    return placa

# ======================
# 👤 CRUD USUARIOS
# ======================
def crear_usuario(db: Session, usuario: schemas.UsuarioCrear):
    nombre = validar_nombre(usuario.nombre)
    telefono = validar_telefono(usuario.telefono)
    
    # Verificar si ya existe
    existe = db.query(models.Usuario).filter(models.Usuario.nombre == nombre).first()
    if existe:
        raise HTTPException(400, f"El usuario '{nombre}' ya existe")
    
    nuevo = models.Usuario(
        nombre=nombre,
        telefono=telefono,
        foto_path=getattr(usuario, 'foto_path', None),
        password_hash=hash_password(usuario.contrasena),
        activo=True,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

def autenticar_usuario(db: Session, nombre: str, contrasena: str):
    usuario = db.query(models.Usuario).filter(models.Usuario.nombre == nombre.strip()).first()
    if not usuario or not usuario.activo or not usuario.password_hash:
        return None
    if not pwd_context.verify(contrasena, usuario.password_hash):
        return None
    return usuario

def obtener_usuarios(db: Session):
    return db.query(models.Usuario).filter(models.Usuario.activo == True).all()

def obtener_usuarios_por_estado(db: Session, activo: bool, skip: int = 0, limit: int = 100):
    return db.query(models.Usuario).filter(models.Usuario.activo == activo).offset(skip).limit(limit).all()

def buscar_usuario_por_nombre(db: Session, nombre: str):
    if not nombre or len(nombre.strip()) < 2:
        raise HTTPException(400, "El término de búsqueda debe tener al menos 2 caracteres")
    return db.query(models.Usuario).filter(
        models.Usuario.nombre.ilike(f"%{nombre.strip()}%"),
        models.Usuario.activo == True
    ).all()

def inactivar_usuario(db: Session, usuario_id: int):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        return None
    
    viajes_activos = db.query(models.Viaje).filter(
        models.Viaje.usuario_id == usuario_id,
        models.Viaje.estado.in_(['pendiente', 'en_curso']),
        models.Viaje.activo == True
    ).count()
    
    if viajes_activos > 0:
        raise HTTPException(400, f"No se puede inactivar: el usuario tiene {viajes_activos} viaje(s) activo(s)")
    
    usuario.activo = False
    db.commit()
    db.refresh(usuario)
    return usuario

def eliminar_usuario(db: Session, usuario_id: int):
    return inactivar_usuario(db, usuario_id)

# ======================
# 🏍️ CRUD CONDUCTORES
# ======================
def crear_conductor(db: Session, conductor: schemas.ConductorCrear):
    nombre = validar_nombre(conductor.nombre)
    licencia = validar_licencia(conductor.licencia) if conductor.licencia else None
    
    # ✅ PERMITIR LICENCIAS DUPLICADAS - Eliminada validación
    
    nuevo_conductor = models.Conductor(
        nombre=nombre,
        licencia=licencia,
        activo=True
    )
    db.add(nuevo_conductor)
    db.commit()
    db.refresh(nuevo_conductor)
    return nuevo_conductor

def obtener_conductores(db: Session):
    return db.query(models.Conductor).filter(models.Conductor.activo == True).all()

def obtener_conductor_por_id(db: Session, conductor_id: int):
    return db.query(models.Conductor).filter(models.Conductor.id == conductor_id).first()

def obtener_conductores_por_estado(db: Session, activo: bool):
    return db.query(models.Conductor).filter(models.Conductor.activo == activo).all()

def inactivar_conductor(db: Session, conductor_id: int):
    conductor = db.query(models.Conductor).filter(models.Conductor.id == conductor_id).first()
    if not conductor:
        return None
    
    viajes_activos = db.query(models.Viaje).filter(
        models.Viaje.conductor_id == conductor_id,
        models.Viaje.estado.in_(['pendiente', 'en_curso']),
        models.Viaje.activo == True
    ).count()
    
    if viajes_activos > 0:
        raise HTTPException(400, f"No se puede inactivar: el conductor tiene {viajes_activos} viaje(s) activo(s)")
    
    conductor.activo = False
    db.commit()
    db.refresh(conductor)
    return conductor

def eliminar_conductor(db: Session, conductor_id: int):
    return inactivar_conductor(db, conductor_id)

def conductor_esta_libre(db: Session, conductor_id: int) -> bool:
    """Verifica si un conductor está libre (sin viajes activos)"""
    viajes_activos = db.query(models.Viaje).filter(
        models.Viaje.conductor_id == conductor_id,
        models.Viaje.estado.in_(['pendiente', 'en_curso']),
        models.Viaje.activo == True
    ).count()
    return viajes_activos == 0

# ======================
# 🚗 CRUD VEHÍCULOS
# ======================
def crear_vehiculo(db: Session, vehiculo: schemas.VehiculoCrear):
    placa = validar_placa(vehiculo.placa)
    
    # ✅ PERMITIR PLACAS DUPLICADAS - Eliminada validación
    # Si quieres que las placas sean únicas, descomenta las siguientes líneas:
    # existe = db.query(models.Vehiculo).filter(models.Vehiculo.placa == placa).first()
    # if existe:
    #     raise HTTPException(400, f"La placa '{placa}' ya está registrada")
    
    nuevo_vehiculo = models.Vehiculo(
        placa=placa,
        modelo=vehiculo.modelo.strip() if vehiculo.modelo else None,
        activo=True
    )
    db.add(nuevo_vehiculo)
    db.commit()
    db.refresh(nuevo_vehiculo)
    return nuevo_vehiculo

def obtener_vehiculos(db: Session):
    return db.query(models.Vehiculo).filter(models.Vehiculo.activo == True).all()

def obtener_vehiculos_por_estado(db: Session, activo: bool):
    return db.query(models.Vehiculo).filter(models.Vehiculo.activo == activo).all()

def obtener_vehiculos_por_conductor(db: Session, conductor_id: int):
    """Obtiene todos los vehículos de un conductor"""
    return db.query(models.Vehiculo).filter(
        models.Vehiculo.conductor_id == conductor_id,
        models.Vehiculo.activo == True
    ).all()

def buscar_vehiculo_por_placa(db: Session, placa: str):
    if not placa or len(placa.strip()) < 2:
        raise HTTPException(400, "El término de búsqueda debe tener al menos 2 caracteres")
    placa_limpia = placa.strip().upper()
    return db.query(models.Vehiculo).filter(
        models.Vehiculo.placa.ilike(f"%{placa_limpia}%"),
        models.Vehiculo.activo == True
    ).all()

def inactivar_vehiculo(db: Session, vehiculo_id: int):
    vehiculo = db.query(models.Vehiculo).filter(models.Vehiculo.id == vehiculo_id).first()
    if not vehiculo:
        return None
    
    viajes_activos = db.query(models.Viaje).filter(
        models.Viaje.vehiculo_id == vehiculo_id,
        models.Viaje.estado.in_(['pendiente', 'en_curso']),
        models.Viaje.activo == True
    ).count()
    
    if viajes_activos > 0:
        raise HTTPException(400, f"No se puede inactivar: el vehículo tiene {viajes_activos} viaje(s) activo(s)")
    
    vehiculo.activo = False
    db.commit()
    db.refresh(vehiculo)
    return vehiculo

def eliminar_vehiculo(db: Session, vehiculo_id: int):
    return inactivar_vehiculo(db, vehiculo_id)

# ======================
# 🚖 CRUD VIAJES
# ======================
def crear_viaje(db: Session, viaje: schemas.ViajeCrear):
    # Validaciones básicas
    if not viaje.usuario_id or not viaje.conductor_id or not viaje.vehiculo_id:
        raise HTTPException(400, "Faltan datos obligatorios del viaje")
    
    # Verificar que existan
    usuario = db.query(models.Usuario).filter(models.Usuario.id == viaje.usuario_id).first()
    if not usuario or not usuario.activo:
        raise HTTPException(400, "Usuario no válido o inactivo")
    
    conductor = db.query(models.Conductor).filter(models.Conductor.id == viaje.conductor_id).first()
    if not conductor or not conductor.activo:
        raise HTTPException(400, "Conductor no válido o inactivo")
    
    vehiculo = db.query(models.Vehiculo).filter(models.Vehiculo.id == viaje.vehiculo_id).first()
    if not vehiculo or not vehiculo.activo:
        raise HTTPException(400, "Vehículo no válido o inactivo")
    
    origen = viaje.origen.strip() if viaje.origen else "Centro Supatá"
    destino = viaje.destino.strip() if viaje.destino else "Destino"
    estado = (viaje.estado or 'pendiente').strip().lower()
    
    nuevo_viaje = models.Viaje(
        origen=origen,
        destino=destino,
        precio=viaje.precio or 5000.0,
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
    return db.query(models.Viaje).filter(models.Viaje.activo == True).all()

def obtener_viajes_activos_por_conductor(db: Session, conductor_id: int):
    """Obtiene viajes activos (pendiente o en_curso) de un conductor"""
    return db.query(models.Viaje).filter(
        models.Viaje.conductor_id == conductor_id,
        models.Viaje.estado.in_(['pendiente', 'en_curso']),
        models.Viaje.activo == True
    ).all()

def actualizar_estado_viaje(db: Session, viaje_id: int, nuevo_estado: str):
    viaje = db.query(models.Viaje).filter(models.Viaje.id == viaje_id).first()
    if not viaje:
        return None
    
    estados_validos = ['pendiente', 'en_curso', 'completado', 'cancelado']
    if nuevo_estado not in estados_validos:
        raise HTTPException(400, f"Estado inválido. Debe ser uno de: {', '.join(estados_validos)}")
    
    viaje.estado = nuevo_estado
    db.commit()
    db.refresh(viaje)
    return viaje

def completar_viaje(db: Session, viaje_id: int):
    """Completa un viaje y libera al conductor"""
    viaje = db.query(models.Viaje).filter(models.Viaje.id == viaje_id).first()
    if not viaje:
        return None
    
    viaje.estado = 'completado'
    db.commit()
    db.refresh(viaje)
    return viaje

def cancelar_viaje(db: Session, viaje_id: int):
    """Cancela un viaje y libera al conductor"""
    viaje = db.query(models.Viaje).filter(models.Viaje.id == viaje_id).first()
    if not viaje:
        return None
    
    viaje.estado = 'cancelado'
    db.commit()
    db.refresh(viaje)
    return viaje

def eliminar_viaje(db: Session, viaje_id: int):
    viaje = db.query(models.Viaje).filter(models.Viaje.id == viaje_id).first()
    if not viaje:
        return None
    
    if viaje.estado in ['en_curso', 'completado']:
        raise HTTPException(400, f"No se puede eliminar un viaje en estado '{viaje.estado}'")
    
    db.delete(viaje)
    db.commit()
    return viaje