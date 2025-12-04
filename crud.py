from sqlalchemy.orm import Session
import models, schemas
from passlib.context import CryptContext
from fastapi import HTTPException

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str):
    return pwd_context.verify(password, hashed)

# ======================
# 👤 USUARIOS
# ======================
def crear_usuario(db: Session, usuario: schemas.UsuarioCrear):
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
    usuario = db.query(models.Usuario).filter(models.Usuario.nombre == nombre.strip()).first()
    if not usuario or not usuario.activo or not usuario.password_hash:
        return None
    if not pwd_context.verify(contrasena, usuario.password_hash):
        return None
    return usuario

def obtener_usuarios(db: Session):
    return db.query(models.Usuario).filter(models.Usuario.activo == True).all()

def obtener_usuario_por_id(db: Session, usuario_id: int):
    return db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()

# ======================
# 🏍️ CONDUCTORES
# ======================
def crear_conductor(db: Session, conductor: schemas.ConductorCrear):
    nombre_limpio = conductor.nombre.strip()
    licencia_limpia = conductor.licencia.strip().upper() if conductor.licencia else None
    
    # Verificar si ya existe
    existe = db.query(models.Conductor).filter(models.Conductor.nombre == nombre_limpio).first()
    if existe:
        raise HTTPException(400, f"Ya existe un conductor con el nombre '{nombre_limpio}'")
    
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
    return db.query(models.Conductor).filter(models.Conductor.activo == True).all()

def obtener_conductor_por_id(db: Session, conductor_id: int):
    return db.query(models.Conductor).filter(models.Conductor.id == conductor_id).first()

def obtener_conductor_por_nombre(db: Session, nombre: str):
    """Buscar conductor por nombre exacto"""
    return db.query(models.Conductor).filter(
        models.Conductor.nombre == nombre.strip(),
        models.Conductor.activo == True
    ).first()

def conductor_esta_libre(db: Session, conductor_id: int) -> bool:
    """Verifica si un conductor está libre (sin viajes activos)"""
    viajes_activos = db.query(models.Viaje).filter(
        models.Viaje.conductor_id == conductor_id,
        models.Viaje.estado.in_(['pendiente', 'en_curso']),
        models.Viaje.activo == True
    ).count()
    return viajes_activos == 0

def obtener_conductores_disponibles(db: Session):
    """Obtiene solo conductores que están LIBRES (sin viajes activos)"""
    conductores = db.query(models.Conductor).filter(models.Conductor.activo == True).all()
    
    conductores_libres = []
    for conductor in conductores:
        if conductor_esta_libre(db, conductor.id):
            conductores_libres.append(conductor)
    
    return conductores_libres

# ======================
# 🚗 VEHÍCULOS
# ======================
def crear_vehiculo(db: Session, vehiculo: schemas.VehiculoCrear, conductor_id: int = None, conductor_nombre: str = None):
    """
    Crear vehículo y asignarlo a un conductor (por ID o nombre)
    """
    placa_limpia = vehiculo.placa.strip().upper().replace("-", "").replace(" ", "")
    
    # Verificar si ya existe la placa
    existe = db.query(models.Vehiculo).filter(models.Vehiculo.placa == placa_limpia).first()
    if existe:
        raise HTTPException(400, f"Ya existe un vehículo con la placa '{placa_limpia}'")
    
    # Buscar conductor si se proporciona
    conductor_final_id = None
    
    if conductor_id:
        conductor = obtener_conductor_por_id(db, conductor_id)
        if not conductor:
            raise HTTPException(404, f"No se encontró conductor con ID {conductor_id}")
        conductor_final_id = conductor_id
    
    elif conductor_nombre:
        conductor = obtener_conductor_por_nombre(db, conductor_nombre)
        if not conductor:
            raise HTTPException(404, f"No se encontró conductor con nombre '{conductor_nombre}'")
        conductor_final_id = conductor.id
    
    nuevo_vehiculo = models.Vehiculo(
        placa=placa_limpia,
        modelo=vehiculo.modelo.strip() if vehiculo.modelo else None,
        conductor_id=conductor_final_id,
        activo=True
    )
    db.add(nuevo_vehiculo)
    db.commit()
    db.refresh(nuevo_vehiculo)
    return nuevo_vehiculo

def obtener_vehiculos(db: Session):
    return db.query(models.Vehiculo).filter(models.Vehiculo.activo == True).all()

def obtener_vehiculos_por_conductor(db: Session, conductor_id: int):
    """Obtiene todos los vehículos de un conductor"""
    return db.query(models.Vehiculo).filter(
        models.Vehiculo.conductor_id == conductor_id,
        models.Vehiculo.activo == True
    ).all()

def obtener_vehiculo_por_id(db: Session, vehiculo_id: int):
    return db.query(models.Vehiculo).filter(models.Vehiculo.id == vehiculo_id).first()

# ======================
# 🚖 VIAJES
# ======================
def crear_viaje(db: Session, viaje: schemas.ViajeCrear):
    """
    Crear un viaje verificando que el conductor esté disponible
    """
    # Verificar que el conductor existe y está libre
    conductor = obtener_conductor_por_id(db, viaje.conductor_id)
    if not conductor:
        raise HTTPException(404, "Conductor no encontrado")
    
    if not conductor.activo:
        raise HTTPException(400, "El conductor está inactivo")
    
    if not conductor_esta_libre(db, viaje.conductor_id):
        raise HTTPException(400, f"El conductor {conductor.nombre} ya tiene un viaje activo")
    
    # Verificar usuario
    usuario = obtener_usuario_por_id(db, viaje.usuario_id)
    if not usuario:
        raise HTTPException(404, "Usuario no encontrado")
    
    # Verificar vehículo (opcional - puede ir sin vehículo específico)
    if viaje.vehiculo_id:
        vehiculo = obtener_vehiculo_por_id(db, viaje.vehiculo_id)
        if not vehiculo:
            raise HTTPException(404, "Vehículo no encontrado")
    
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
    return db.query(models.Viaje).filter(models.Viaje.activo == True).all()

def obtener_viajes_activos_por_conductor(db: Session, conductor_id: int):
    """Obtiene viajes activos (pendiente o en_curso) de un conductor"""
    return db.query(models.Viaje).filter(
        models.Viaje.conductor_id == conductor_id,
        models.Viaje.estado.in_(['pendiente', 'en_curso']),
        models.Viaje.activo == True
    ).all()

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

def actualizar_estado_viaje(db: Session, viaje_id: int, nuevo_estado: str):
    viaje = db.query(models.Viaje).filter(models.Viaje.id == viaje_id).first()
    if not viaje:
        return None
    
    viaje.estado = nuevo_estado
    db.commit()
    db.refresh(viaje)
    return viaje

def eliminar_viaje(db: Session, viaje_id: int):
    viaje = db.query(models.Viaje).filter(models.Viaje.id == viaje_id).first()
    if not viaje:
        return None
    
    db.delete(viaje)
    db.commit()
    return viaje