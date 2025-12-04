from sqlalchemy.orm import Session
from fastapi import HTTPException
import models
from datetime import datetime, timedelta
import re


class BusinessRules:
    """Clase que centraliza todas las reglas de negocio del sistema"""
    
    @staticmethod
    def validar_nombre_usuario(nombre: str) -> None:
        if not nombre or not nombre.strip():
            raise HTTPException(400, "El nombre no puede estar vacío")
        nombre = nombre.strip()
        if len(nombre) < 3:
            raise HTTPException(400, "El nombre debe tener al menos 3 caracteres")
        if len(nombre) > 50:
            raise HTTPException(400, "El nombre no puede exceder 50 caracteres")
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\-]+$', nombre):
            raise HTTPException(400, "El nombre solo puede contener letras, espacios y guiones")
    
    @staticmethod
    def validar_telefono(telefono: str) -> None:
        if not telefono or not telefono.strip():
            raise HTTPException(400, "El teléfono no puede estar vacío")
        telefono_limpio = telefono.strip().replace(" ", "").replace("-", "").replace("+", "")
        if not telefono_limpio.isdigit():
            raise HTTPException(400, "El teléfono debe contener solo números")
        if len(telefono_limpio) < 7 or len(telefono_limpio) > 15:
            raise HTTPException(400, "El teléfono debe tener entre 7 y 15 dígitos")
    
    @staticmethod
    def validar_contrasena(contrasena: str) -> None:
        if not contrasena:
            raise HTTPException(400, "La contraseña no puede estar vacía")
        if len(contrasena) < 4:
            raise HTTPException(400, "La contraseña debe tener al menos 4 caracteres")
        if len(contrasena) > 256:
            raise HTTPException(400, "La contraseña no puede exceder 256 caracteres")
    
    @staticmethod
    def validar_usuario_unico(db: Session, nombre: str) -> None:
        usuario_existente = db.query(models.Usuario).filter(models.Usuario.nombre == nombre.strip()).first()
        if usuario_existente:
            raise HTTPException(400, f"El usuario '{nombre}' ya está registrado")
    
    @staticmethod
    def validar_licencia(licencia: str) -> None:
        """Validar licencia (opcional, de 1 a 6 caracteres)"""
        if not licencia:  # Si está vacía, permitirlo
            return
        
        licencia = licencia.strip()
        if len(licencia) < 1:
            raise HTTPException(400, "La licencia no puede estar vacía")
        if len(licencia) > 6:
            raise HTTPException(400, "La licencia debe tener entre 1 y 6 caracteres")
    
    @staticmethod
    def validar_conductor_disponible(db: Session, conductor_id: int) -> None:
       """Valida que el conductor no tenga viajes activos"""
    conductor = db.query(models.Conductor).filter(models.Conductor.id == conductor_id).first()
    if not conductor:
        raise HTTPException(404, "Conductor no encontrado")
    if not conductor.activo:
        raise HTTPException(400, "El conductor está inactivo y no puede ser asignado")
    
    # Contar viajes activos (pendiente o en_curso)
    viajes_activos = db.query(models.Viaje).filter(
        models.Viaje.conductor_id == conductor_id,
        models.Viaje.estado.in_(['pendiente', 'en_curso']),
        models.Viaje.activo == True
    ).count()
    
    if viajes_activos > 0:
        raise HTTPException(
            400, 
            f"El conductor ya tiene {viajes_activos} viaje(s) activo(s) y no puede ser asignado a otro viaje"
        )
    
    @staticmethod
    def validar_licencia_unica(db: Session, licencia: str, conductor_id: int = None) -> None:
        if not licencia or not licencia.strip():
            return  # Si está vacía, no validar unicidad
        
        query = db.query(models.Conductor).filter(models.Conductor.licencia == licencia.strip().upper())
        if conductor_id:
            query = query.filter(models.Conductor.id != conductor_id)
        conductor_existente = query.first()
        if conductor_existente:
            raise HTTPException(400, f"La licencia '{licencia}' ya está registrada")
    
    @staticmethod
    def validar_placa(placa: str) -> None:
        if not placa or not placa.strip():
            raise HTTPException(400, "La placa no puede estar vacía")
        placa = placa.strip().upper().replace("-", "").replace(" ", "")
        if len(placa) != 6:
            raise HTTPException(400, "La placa debe tener 6 caracteres (formato: ABC123)")
        if not re.match(r'^[A-Z]{3}[0-9]{3}$', placa):
            raise HTTPException(400, "La placa debe tener el formato ABC123")
    
    @staticmethod
    def validar_placa_unica(db: Session, placa: str, vehiculo_id: int = None) -> None:
        placa_limpia = placa.strip().upper().replace("-", "").replace(" ", "")
        query = db.query(models.Vehiculo).filter(models.Vehiculo.placa == placa_limpia)
        if vehiculo_id:
            query = query.filter(models.Vehiculo.id != vehiculo_id)
        vehiculo_existente = query.first()
        if vehiculo_existente:
            raise HTTPException(400, f"La placa '{placa}' ya está registrada")
    
    @staticmethod
    def validar_vehiculo_disponible(db: Session, vehiculo_id: int) -> None:
        vehiculo = db.query(models.Vehiculo).filter(models.Vehiculo.id == vehiculo_id).first()
        if not vehiculo:
            raise HTTPException(404, "Vehículo no encontrado")
        if not vehiculo.activo:
            raise HTTPException(400, "El vehículo está inactivo y no puede ser asignado")
        viajes_activos = db.query(models.Viaje).filter(
            models.Viaje.vehiculo_id == vehiculo_id,
            models.Viaje.estado.in_(['pendiente', 'en_curso']),
            models.Viaje.activo == True
        ).count()
        if viajes_activos > 0:
            raise HTTPException(400, f"El vehículo ya está asignado a {viajes_activos} viaje(s) activo(s)")
    
    @staticmethod
    def validar_precio_viaje(precio: float) -> None:
        if precio is None:
            raise HTTPException(400, "El precio del viaje es obligatorio")
        if precio <= 0:
            raise HTTPException(400, "El precio debe ser mayor a cero")
        if precio > 500000:
            raise HTTPException(400, "El precio excede el máximo permitido (500,000 COP)")
    
    @staticmethod
    def validar_ubicaciones_viaje(origen: str, destino: str) -> None:
        if not origen or not origen.strip():
            raise HTTPException(400, "El origen del viaje es obligatorio")
        if not destino or not destino.strip():
            raise HTTPException(400, "El destino del viaje es obligatorio")
        origen = origen.strip()
        destino = destino.strip()
        if len(origen) < 3:
            raise HTTPException(400, "El origen debe tener al menos 3 caracteres")
        if len(destino) < 3:
            raise HTTPException(400, "El destino debe tener al menos 3 caracteres")
        if origen.lower() == destino.lower():
            raise HTTPException(400, "El origen y destino no pueden ser iguales")
    
    @staticmethod
    def validar_estado_viaje(estado: str) -> None:
        estados_validos = ['pendiente', 'en_curso', 'completado', 'cancelado']
        if estado not in estados_validos:
            raise HTTPException(400, f"Estado inválido. Debe ser uno de: {', '.join(estados_validos)}")
    
    @staticmethod
    def validar_cambio_estado_viaje(estado_actual: str, nuevo_estado: str) -> None:
        transiciones_validas = {
            'pendiente': ['en_curso', 'cancelado'],
            'en_curso': ['completado', 'cancelado'],
            'completado': [],
            'cancelado': []
        }
        estados_permitidos = transiciones_validas.get(estado_actual, [])
        if nuevo_estado not in estados_permitidos:
            raise HTTPException(400, f"No se puede cambiar de '{estado_actual}' a '{nuevo_estado}'")
    
    @staticmethod
    def validar_usuario_activo(db: Session, usuario_id: int) -> None:
        usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
        if not usuario:
            raise HTTPException(404, "Usuario no encontrado")
        if not usuario.activo:
            raise HTTPException(400, "El usuario está inactivo y no puede solicitar viajes")
    
    @staticmethod
    def validar_limite_viajes_usuario(db: Session, usuario_id: int) -> None:
        viajes_activos = db.query(models.Viaje).filter(
            models.Viaje.usuario_id == usuario_id,
            models.Viaje.estado.in_(['pendiente', 'en_curso']),
            models.Viaje.activo == True
        ).count()
        if viajes_activos >= 2:
            raise HTTPException(400, "El usuario ya tiene 2 viajes activos")
    
    @staticmethod
    def validar_termino_busqueda(termino: str) -> None:
        if not termino or not termino.strip():
            raise HTTPException(400, "El término de búsqueda no puede estar vacío")
        termino = termino.strip()
        if len(termino) < 2:
            raise HTTPException(400, "El término de búsqueda debe tener al menos 2 caracteres")
        if len(termino) > 50:
            raise HTTPException(400, "El término de búsqueda no puede exceder 50 caracteres")


def aplicar_reglas_usuario(db: Session, nombre: str, telefono: str, contrasena: str, es_nuevo: bool = True) -> None:
    BusinessRules.validar_nombre_usuario(nombre)
    BusinessRules.validar_telefono(telefono)
    BusinessRules.validar_contrasena(contrasena)
    if es_nuevo:
        BusinessRules.validar_usuario_unico(db, nombre)


def aplicar_reglas_conductor(db: Session, nombre: str, licencia: str, es_nuevo: bool = True, conductor_id: int = None) -> None:
    BusinessRules.validar_nombre_usuario(nombre)
    
    # Solo validar formato de licencia si no está vacía
    if licencia and licencia.strip():
        BusinessRules.validar_licencia(licencia)
        # ❌ ELIMINADO: Ya no validamos que la licencia sea única
        # Las licencias pueden repetirse entre conductores


def aplicar_reglas_vehiculo(db: Session, placa: str, es_nuevo: bool = True, vehiculo_id: int = None) -> None:
    BusinessRules.validar_placa(placa)
    if es_nuevo:
        BusinessRules.validar_placa_unica(db, placa, vehiculo_id)


def aplicar_reglas_viaje(db: Session, usuario_id: int, conductor_id: int, vehiculo_id: int, origen: str, destino: str, precio: float, estado: str) -> None:
    BusinessRules.validar_usuario_activo(db, usuario_id)
    BusinessRules.validar_limite_viajes_usuario(db, usuario_id)
    BusinessRules.validar_conductor_disponible(db, conductor_id)
    BusinessRules.validar_vehiculo_disponible(db, vehiculo_id)
    BusinessRules.validar_ubicaciones_viaje(origen, destino)
    BusinessRules.validar_precio_viaje(precio)
    BusinessRules.validar_estado_viaje(estado)