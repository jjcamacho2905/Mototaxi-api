from sqlalchemy.orm import Session
import models, schemas
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
    """Hashea una contraseña usando PBKDF2-SHA256"""
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str):
    """Verifica una contraseña contra su hash"""
    return pwd_context.verify(password, hashed)

# ======================
# 👤 CRUD USUARIOS
# ======================
def crear_usuario(db: Session, usuario: schemas.UsuarioCrear):
    """Crea un nuevo usuario con contraseña hasheada"""
    aplicar_reglas_usuario(db, usuario.nombre, usuario.telefono, usuario.contrasena, es_nuevo=True)
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
    """Autentica un usuario por nombre y contraseña"""
    usuario = db.query(models.Usuario).filter(models.Usuario.nombre == nombre.strip()).first()
    if not usuario or not usuario.activo or not usuario.password_hash:
        return None
    if not pwd_context.verify(contrasena, usuario.password_hash):
        return None
    return usuario

def obtener_usuarios(db: Session):
    """Obtiene todos los usuarios activos"""
    return db.query(models.Usuario).filter(models.Usuario.activo == True).all()

def obtener_usuario_por_id(db: Session, usuario_id: int):
    """Obtiene un usuario por su ID"""
    return db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()

def obtener_usuarios_por_estado(db: Session, activo: bool, skip: int = 0, limit: int = 100):
    """Obtiene usuarios filtrados por estado (activo/inactivo)"""
    return db.query(models.Usuario).filter(models.Usuario.activo == activo).offset(skip).limit(limit).all()

def buscar_usuario_por_nombre(db: Session, nombre: str):
    """Busca usuarios por nombre (búsqueda parcial)"""
    BusinessRules.validar_termino_busqueda(nombre)
    return db.query(models.Usuario).filter(
        models.Usuario.nombre.ilike(f"%{nombre.strip()}%"),
        models.Usuario.activo == True
    ).all()

def inactivar_usuario(db: Session, usuario_id: int):
    """Inactiva un usuario (soft delete) - valida que no tenga viajes activos"""
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        return None
    
    # Validar que no tenga viajes activos
    viajes_activos = db.query(models.Viaje).filter(
        models.Viaje.usuario_id == usuario_id,
        models.Viaje.estado.in_(['pendiente', 'en_curso']),
        models.Viaje.activo == True
    ).count()
    
    if viajes_activos > 0:
        from fastapi import HTTPException
        raise HTTPException(400, f"No se puede inactivar: el usuario tiene {viajes_activos} viaje(s) activo(s)")
    
    usuario.activo = False
    db.commit()
    db.refresh(usuario)
    return usuario

def eliminar_usuario(db: Session, usuario_id: int):
    """Elimina lógicamente un usuario (alias de inactivar_usuario)"""
    return inactivar_usuario(db, usuario_id)

def actualizar_foto_usuario(db: Session, usuario_id: int, foto_path: str):
    """Actualiza la ruta de la foto de un usuario"""
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        return None
    usuario.foto_path = foto_path
    db.commit()
    db.refresh(usuario)
    return usuario

# ======================
# 🏍️ CRUD CONDUCTORES
# ======================
def crear_conductor(db: Session, conductor: schemas.ConductorCrear):
    """Crea un nuevo conductor"""
    aplicar_reglas_conductor(db, conductor.nombre, conductor.licencia, es_nuevo=True)
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

def crear_conductor_con_vehiculo(db: Session, conductor: schemas.ConductorCrear, placa: str, modelo: str = None):
    """Crea un conductor y opcionalmente le asigna un vehículo nuevo"""
    # Crear conductor
    nuevo_conductor = crear_conductor(db, conductor)
    
    # Crear vehículo si se proporciona placa
    if placa:
        vehiculo = schemas.VehiculoCrear(placa=placa, modelo=modelo)
        nuevo_vehiculo = crear_vehiculo(db, vehiculo)
        nuevo_vehiculo.conductor_id = nuevo_conductor.id
        db.commit()
        db.refresh(nuevo_conductor)
    
    return nuevo_conductor

def obtener_conductores(db: Session):
    """Obtiene todos los conductores activos"""
    return db.query(models.Conductor).filter(models.Conductor.activo == True).all()

def obtener_conductor_por_id(db: Session, conductor_id: int):
    """Obtiene un conductor por su ID"""
    return db.query(models.Conductor).filter(models.Conductor.id == conductor_id).first()

def obtener_conductores_por_estado(db: Session, activo: bool):
    """Obtiene conductores filtrados por estado"""
    return db.query(models.Conductor).filter(models.Conductor.activo == activo).all()

def buscar_conductor_por_nombre(db: Session, nombre: str):
    """Busca conductores por nombre"""
    BusinessRules.validar_termino_busqueda(nombre)
    return db.query(models.Conductor).filter(
        models.Conductor.nombre.ilike(f"%{nombre.strip()}%"),
        models.Conductor.activo == True
    ).all()

def inactivar_conductor(db: Session, conductor_id: int):
    """Inactiva un conductor - valida que no tenga viajes activos"""
    conductor = db.query(models.Conductor).filter(models.Conductor.id == conductor_id).first()
    if not conductor:
        return None
    
    # Validar que no tenga viajes activos
    viajes_activos = db.query(models.Viaje).filter(
        models.Viaje.conductor_id == conductor_id,
        models.Viaje.estado.in_(['pendiente', 'en_curso']),
        models.Viaje.activo == True
    ).count()
    
    if viajes_activos > 0:
        from fastapi import HTTPException
        raise HTTPException(400, f"No se puede inactivar: el conductor tiene {viajes_activos} viaje(s) activo(s)")
    
    conductor.activo = False
    db.commit()
    db.refresh(conductor)
    return conductor

def eliminar_conductor(db: Session, conductor_id: int):
    """Elimina lógicamente un conductor"""
    return inactivar_conductor(db, conductor_id)

def conductor_esta_libre(db: Session, conductor_id: int) -> bool:
    """Verifica si un conductor está libre (sin viajes activos)"""
    viajes_activos = db.query(models.Viaje).filter(
        models.Viaje.conductor_id == conductor_id,
        models.Viaje.estado.in_(['pendiente', 'en_curso']),
        models.Viaje.activo == True
    ).count()
    return viajes_activos == 0

def actualizar_foto_conductor(db: Session, conductor_id: int, foto_path: str):
    """Actualiza la ruta de la foto de un conductor"""
    conductor = db.query(models.Conductor).filter(models.Conductor.id == conductor_id).first()
    if not conductor:
        return None
    conductor.foto_path = foto_path
    db.commit()
    db.refresh(conductor)
    return conductor

# ======================
# 🚗 CRUD VEHÍCULOS
# ======================
def crear_vehiculo(db: Session, vehiculo: schemas.VehiculoCrear):
    """Crea un nuevo vehículo"""
    aplicar_reglas_vehiculo(db, vehiculo.placa, es_nuevo=True)
    placa_limpia = vehiculo.placa.strip().upper().replace("-", "").replace(" ", "")
    
    nuevo_vehiculo = models.Vehiculo(
        placa=placa_limpia,
        modelo=vehiculo.modelo.strip() if vehiculo.modelo else None,
        conductor_id=vehiculo.conductor_id if hasattr(vehiculo, 'conductor_id') else None,
        activo=True
    )
    db.add(nuevo_vehiculo)
    db.commit()
    db.refresh(nuevo_vehiculo)
    return nuevo_vehiculo

def obtener_vehiculos(db: Session):
    """Obtiene todos los vehículos activos"""
    return db.query(models.Vehiculo).filter(models.Vehiculo.activo == True).all()

def obtener_vehiculo_por_id(db: Session, vehiculo_id: int):
    """Obtiene un vehículo por su ID"""
    return db.query(models.Vehiculo).filter(models.Vehiculo.id == vehiculo_id).first()

def obtener_vehiculos_por_estado(db: Session, activo: bool):
    """Obtiene vehículos filtrados por estado"""
    return db.query(models.Vehiculo).filter(models.Vehiculo.activo == activo).all()

def obtener_vehiculos_por_conductor(db: Session, conductor_id: int):
    """Obtiene todos los vehículos de un conductor específico"""
    return db.query(models.Vehiculo).filter(
        models.Vehiculo.conductor_id == conductor_id,
        models.Vehiculo.activo == True
    ).all()

def obtener_vehiculos_sin_conductor(db: Session):
    """Obtiene vehículos que no tienen conductor asignado"""
    return db.query(models.Vehiculo).filter(
        models.Vehiculo.conductor_id == None,
        models.Vehiculo.activo == True
    ).all()

def asignar_vehiculo_a_conductor(db: Session, vehiculo_id: int, conductor_id: int):
    """Asigna un vehículo a un conductor"""
    vehiculo = db.query(models.Vehiculo).filter(models.Vehiculo.id == vehiculo_id).first()
    if not vehiculo:
        return None
    
    conductor = db.query(models.Conductor).filter(models.Conductor.id == conductor_id).first()
    if not conductor:
        from fastapi import HTTPException
        raise HTTPException(404, "Conductor no encontrado")
    
    vehiculo.conductor_id = conductor_id
    db.commit()
    db.refresh(vehiculo)
    return vehiculo

def desasignar_vehiculo_de_conductor(db: Session, vehiculo_id: int):
    """Quita la asignación de un vehículo de su conductor"""
    vehiculo = db.query(models.Vehiculo).filter(models.Vehiculo.id == vehiculo_id).first()
    if not vehiculo:
        return None
    
    vehiculo.conductor_id = None
    db.commit()
    db.refresh(vehiculo)
    return vehiculo

def buscar_vehiculo_por_placa(db: Session, placa: str):
    """Busca vehículos por placa (búsqueda parcial)"""
    BusinessRules.validar_termino_busqueda(placa)
    placa_limpia = placa.strip().upper().replace("-", "").replace(" ", "")
    return db.query(models.Vehiculo).filter(
        models.Vehiculo.placa.ilike(f"%{placa_limpia}%"),
        models.Vehiculo.activo == True
    ).all()

def inactivar_vehiculo(db: Session, vehiculo_id: int):
    """Inactiva un vehículo - valida que no tenga viajes activos"""
    vehiculo = db.query(models.Vehiculo).filter(models.Vehiculo.id == vehiculo_id).first()
    if not vehiculo:
        return None
    
    # Validar que no tenga viajes activos
    viajes_activos = db.query(models.Viaje).filter(
        models.Viaje.vehiculo_id == vehiculo_id,
        models.Viaje.estado.in_(['pendiente', 'en_curso']),
        models.Viaje.activo == True
    ).count()
    
    if viajes_activos > 0:
        from fastapi import HTTPException
        raise HTTPException(400, f"No se puede inactivar: el vehículo tiene {viajes_activos} viaje(s) activo(s)")
    
    vehiculo.activo = False
    db.commit()
    db.refresh(vehiculo)
    return vehiculo

def eliminar_vehiculo(db: Session, vehiculo_id: int):
    """Elimina lógicamente un vehículo"""
    return inactivar_vehiculo(db, vehiculo_id)

def actualizar_foto_vehiculo(db: Session, vehiculo_id: int, foto_path: str):
    """Actualiza la ruta de la foto de un vehículo"""
    vehiculo = db.query(models.Vehiculo).filter(models.Vehiculo.id == vehiculo_id).first()
    if not vehiculo:
        return None
    vehiculo.foto_path = foto_path
    db.commit()
    db.refresh(vehiculo)
    return vehiculo

# ======================
# 🚖 CRUD VIAJES
# ======================
def crear_viaje(db: Session, viaje: schemas.ViajeCrear):
    """Crea un nuevo viaje con validaciones completas"""
    aplicar_reglas_viaje(
        db, viaje.usuario_id, viaje.conductor_id, viaje.vehiculo_id,
        viaje.origen or "Centro Supatá", viaje.destino or "Destino",
        viaje.precio or 5000.0, viaje.estado or "pendiente"
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
    return db.query(models.Viaje).filter(models.Viaje.activo == True).all()

def obtener_viaje_por_id(db: Session, viaje_id: int):
    """Obtiene un viaje por su ID"""
    return db.query(models.Viaje).filter(models.Viaje.id == viaje_id).first()

def obtener_viajes_por_estado(db: Session, estado: str):
    """Obtiene viajes filtrados por estado"""
    return db.query(models.Viaje).filter(
        models.Viaje.estado == estado,
        models.Viaje.activo == True
    ).all()

def obtener_viajes_por_usuario(db: Session, usuario_id: int):
    """Obtiene todos los viajes de un usuario"""
    return db.query(models.Viaje).filter(
        models.Viaje.usuario_id == usuario_id,
        models.Viaje.activo == True
    ).all()

def obtener_viajes_por_conductor(db: Session, conductor_id: int):
    """Obtiene todos los viajes de un conductor"""
    return db.query(models.Viaje).filter(
        models.Viaje.conductor_id == conductor_id,
        models.Viaje.activo == True
    ).all()

def obtener_viajes_activos_por_conductor(db: Session, conductor_id: int):
    """Obtiene viajes activos (pendiente o en_curso) de un conductor"""
    return db.query(models.Viaje).filter(
        models.Viaje.conductor_id == conductor_id,
        models.Viaje.estado.in_(['pendiente', 'en_curso']),
        models.Viaje.activo == True
    ).all()

def obtener_viajes_por_vehiculo(db: Session, vehiculo_id: int):
    """Obtiene todos los viajes de un vehículo"""
    return db.query(models.Viaje).filter(
        models.Viaje.vehiculo_id == vehiculo_id,
        models.Viaje.activo == True
    ).all()

def actualizar_estado_viaje(db: Session, viaje_id: int, nuevo_estado: str):
    """Actualiza el estado de un viaje con validación de transiciones"""
    viaje = db.query(models.Viaje).filter(models.Viaje.id == viaje_id).first()
    if not viaje:
        return None
    
    BusinessRules.validar_estado_viaje(nuevo_estado)
    BusinessRules.validar_cambio_estado_viaje(viaje.estado, nuevo_estado)
    
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
    """Elimina permanentemente un viaje (solo si no está en curso o completado)"""
    viaje = db.query(models.Viaje).filter(models.Viaje.id == viaje_id).first()
    if not viaje:
        return None
    
    if viaje.estado in ['en_curso', 'completado']:
        from fastapi import HTTPException
        raise HTTPException(400, f"No se puede eliminar un viaje en estado '{viaje.estado}'")
    
    db.delete(viaje)
    db.commit()
    return viaje

def inactivar_viaje(db: Session, viaje_id: int):
    """Inactiva un viaje (soft delete)"""
    viaje = db.query(models.Viaje).filter(models.Viaje.id == viaje_id).first()
    if not viaje:
        return None
    
    viaje.activo = False
    db.commit()
    db.refresh(viaje)
    return viaje

# ======================
# 📊 ESTADÍSTICAS Y CONSULTAS
# ======================
def contar_viajes_por_estado(db: Session):
    """Cuenta los viajes agrupados por estado"""
    from sqlalchemy import func
    return db.query(
        models.Viaje.estado,
        func.count(models.Viaje.id).label('total')
    ).filter(
        models.Viaje.activo == True
    ).group_by(models.Viaje.estado).all()

def calcular_ingresos_totales(db: Session):
    """Calcula los ingresos totales de todos los viajes completados"""
    from sqlalchemy import func
    resultado = db.query(func.sum(models.Viaje.precio)).filter(
        models.Viaje.estado == 'completado',
        models.Viaje.activo == True
    ).scalar()
    return resultado or 0.0

def obtener_conductores_mas_activos(db: Session, limite: int = 5):
    """Obtiene los conductores con más viajes completados"""
    from sqlalchemy import func
    return db.query(
        models.Conductor,
        func.count(models.Viaje.id).label('total_viajes')
    ).join(
        models.Viaje, models.Conductor.id == models.Viaje.conductor_id
    ).filter(
        models.Viaje.estado == 'completado',
        models.Viaje.activo == True,
        models.Conductor.activo == True
    ).group_by(
        models.Conductor.id
    ).order_by(
        func.count(models.Viaje.id).desc()
    ).limit(limite).all()

def obtener_usuarios_mas_frecuentes(db: Session, limite: int = 5):
    """Obtiene los usuarios con más viajes"""
    from sqlalchemy import func
    return db.query(
        models.Usuario,
        func.count(models.Viaje.id).label('total_viajes')
    ).join(
        models.Viaje, models.Usuario.id == models.Viaje.usuario_id
    ).filter(
        models.Viaje.activo == True,
        models.Usuario.activo == True
    ).group_by(
        models.Usuario.id
    ).order_by(
        func.count(models.Viaje.id).desc()
    ).limit(limite).all()