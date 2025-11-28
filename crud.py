from sqlalchemy.orm import Session
import models, schemas


# ==========================
# 👤 CRUD USUARIOS
# ==========================

def crear_usuario(db: Session, usuario: schemas.UsuarioCrear):
    nuevo_usuario = models.Usuario(
        nombre=usuario.nombre,
        correo=usuario.correo,
        activo=True
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario


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
    nuevo_viaje = models.Viaje(
        origen=viaje.origen,
        destino=viaje.destino,
        costo=viaje.costo,
        conductor_id=viaje.conductor_id,
        vehiculo_id=viaje.vehiculo_id,
        usuario_id=viaje.usuario_id
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
