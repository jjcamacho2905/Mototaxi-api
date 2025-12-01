from sqlalchemy.orm import Session
import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# ======================
# 🔐 Funciones de seguridad
# ======================
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str):
    return pwd_context.verify(password, hashed)

# ======================
# 👤 CRUD USUARIOS
# ======================
def crear_usuario(db: Session, usuario: schemas.UsuarioCrear):
    """Crea un usuario guardando la contraseña como hash seguro.

    Usamos 'nombre' como identificador sencillo para el login.
    """
    nuevo = models.Usuario(
        nombre=usuario.nombre,
        telefono=usuario.telefono,
        foto_path=getattr(usuario, 'foto_path', None),
        password_hash=hash_password(usuario.contrasena),
        activo=True,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


def autenticar_usuario(db: Session, nombre: str, contrasena: str):
    """Autentica por 'nombre' y verifica la contraseña contra el hash."""
    usuario = db.query(models.Usuario).filter(models.Usuario.nombre == nombre).first()
    if not usuario:
        return None
    if not usuario.password_hash:
        return None
    if not pwd_context.verify(contrasena, usuario.password_hash):
        return None
    return usuario




def obtener_usuarios(db: Session):
    return db.query(models.Usuario).all()


def obtener_usuarios_por_estado(db: Session, activo: bool, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Usuario)
        .filter(models.Usuario.activo == activo)
        .offset(skip)
        .limit(limit)
        .all()
    )


def buscar_usuario_por_nombre(db: Session, nombre: str):
    return db.query(models.Usuario).filter(models.Usuario.nombre.ilike(f"%{nombre}%")).all()


def inactivar_usuario(db: Session, usuario_id: int):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        return None
    usuario.activo = False
    db.commit()
    db.refresh(usuario)
    return usuario


def eliminar_usuario(db: Session, usuario_id: int):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        return None
    db.delete(usuario)
    db.commit()
    return usuario



# ==========================
# 🏍️ CRUD CONDUCTORES
# ==========================

def crear_conductor(db: Session, conductor: schemas.ConductorCrear):
    nuevo_conductor = models.Conductor(
        nombre=conductor.nombre,
        licencia=conductor.licencia,
        activo=True
    )
    db.add(nuevo_conductor)
    db.commit()
    db.refresh(nuevo_conductor)
    return nuevo_conductor


def obtener_conductores(db: Session):
    return db.query(models.Conductor).all()


def obtener_conductores_por_estado(db: Session, activo: bool):
    return db.query(models.Conductor).filter(models.Conductor.activo == activo).all()


def inactivar_conductor(db: Session, conductor_id: int):
    conductor = db.query(models.Conductor).filter(models.Conductor.id == conductor_id).first()
    if not conductor:
        return None
    conductor.activo = False
    db.commit()
    db.refresh(conductor)
    return conductor


def eliminar_conductor(db: Session, conductor_id: int):
    conductor = db.query(models.Conductor).filter(models.Conductor.id == conductor_id).first()
    if not conductor:
        return None
    db.delete(conductor)
    db.commit()
    return conductor



# ==========================
# 🚘 CRUD VEHÍCULOS
# ==========================

def crear_vehiculo(db: Session, vehiculo: schemas.VehiculoCrear):
    nuevo_vehiculo = models.Vehiculo(
        placa=vehiculo.placa,
        modelo=vehiculo.modelo,
        activo=True
    )
    db.add(nuevo_vehiculo)
    db.commit()
    db.refresh(nuevo_vehiculo)
    return nuevo_vehiculo


def obtener_vehiculos(db: Session):
    return db.query(models.Vehiculo).all()


def obtener_vehiculos_por_estado(db: Session, activo: bool):
    return db.query(models.Vehiculo).filter(models.Vehiculo.activo == activo).all()


def buscar_vehiculo_por_placa(db: Session, placa: str):
    return db.query(models.Vehiculo).filter(models.Vehiculo.placa.ilike(f"%{placa}%")).all()


def inactivar_vehiculo(db: Session, vehiculo_id: int):
    vehiculo = db.query(models.Vehiculo).filter(models.Vehiculo.id == vehiculo_id).first()
    if not vehiculo:
        return None
    vehiculo.activo = False
    db.commit()
    db.refresh(vehiculo)
    return vehiculo


def eliminar_vehiculo(db: Session, vehiculo_id: int):
    vehiculo = db.query(models.Vehiculo).filter(models.Vehiculo.id == vehiculo_id).first()
    if not vehiculo:
        return None
    db.delete(vehiculo)
    db.commit()
    return vehiculo



# ==========================
# 🚖 CRUD VIAJES
# ==========================

def crear_viaje(db: Session, viaje: schemas.ViajeCrear):
    """Crea un viaje con campos enriquecidos (origen, destino, precio, fecha, estado)."""
    nuevo_viaje = models.Viaje(
        origen=getattr(viaje, 'origen', None),
        destino=getattr(viaje, 'destino', None),
        precio=getattr(viaje, 'precio', None),
        fecha=getattr(viaje, 'fecha', None),
        estado=getattr(viaje, 'estado', 'pendiente') or 'pendiente',
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
    return db.query(models.Viaje).all()


def eliminar_viaje(db: Session, viaje_id: int):
    viaje = db.query(models.Viaje).filter(models.Viaje.id == viaje_id).first()
    if not viaje:
        return None
    db.delete(viaje)
    db.commit()
    return viaje
