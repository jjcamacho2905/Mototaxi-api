from fastapi import FastAPI, Request, Depends, HTTPException, UploadFile, File, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
import shutil
import uuid
import os

import models, schemas, crud
from database import engine, get_db, Base

# ✅ DESCOMENTAR ESTA LÍNEA PARA CREAR LAS TABLAS
Base.metadata.create_all(bind=engine)

# 🚀 INICIALIZAR FASTAPI
app = FastAPI(
    title="🚖 Proyecto Mototaxi Supatá - API",
    version="1.0",
    description="Sistema de gestión de mototaxis con usuarios, conductores, vehículos y viajes"
)


# 📁 CONFIGURACIÓN DE TEMPLATES Y ESTÁTICOS
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 📸 CARPETA PARA UPLOADS - CREAR SI NO EXISTE
UPLOAD_DIR = Path("app/static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
print(f"✅ Carpeta de uploads creada/verificada: {UPLOAD_DIR.absolute()}")

# 🔧 WORKAROUND PARA EL ERROR DE UNICODE EN FASTAPI
from fastapi.encoders import ENCODERS_BY_TYPE
ENCODERS_BY_TYPE[bytes] = lambda o: o.decode('utf-8', errors='ignore')

# ============================================
# 🏠 PÁGINA DE INICIO (SIN LOGIN)
# ============================================

@app.get("/", tags=["Inicio"])
def inicio_page(request: Request):
    """Página de inicio sin autenticación"""
    return templates.TemplateResponse("inicio.html", {"request": request})


# ============================================
# 📊 PÁGINAS HTML
# ============================================

@app.get("/dashboard", tags=["Páginas HTML"])
def dashboard_page(request: Request, db: Session = Depends(get_db)):
    """Dashboard con estadísticas completas"""
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    # Contar entidades activas
    total_usuarios = db.query(models.Usuario).filter(models.Usuario.activo == True).count()
    total_conductores = db.query(models.Conductor).filter(models.Conductor.activo == True).count()
    total_vehiculos = db.query(models.Vehiculo).filter(models.Vehiculo.activo == True).count()
    
    # Estadísticas de viajes
    total_viajes = db.query(models.Viaje).filter(models.Viaje.activo == True).count()
    
    viajes_completados = db.query(models.Viaje).filter(
        models.Viaje.estado == 'completado',
        models.Viaje.activo == True
    ).count()
    
    viajes_en_curso = db.query(models.Viaje).filter(
        models.Viaje.estado == 'en_curso',
        models.Viaje.activo == True
    ).count()
    
    viajes_pendientes = db.query(models.Viaje).filter(
        models.Viaje.estado == 'pendiente',
        models.Viaje.activo == True
    ).count()
    
    viajes_cancelados = db.query(models.Viaje).filter(
        models.Viaje.estado == 'cancelado',
        models.Viaje.activo == True
    ).count()
    
    # Ingresos totales (solo viajes completados)
    ingresos_resultado = db.query(func.sum(models.Viaje.precio)).filter(
        models.Viaje.estado == 'completado',
        models.Viaje.activo == True
    ).scalar()
    ingresos_totales = ingresos_resultado or 0
    
    # Ingreso promedio por viaje
    ingreso_promedio = ingresos_totales / viajes_completados if viajes_completados > 0 else 0
    
    # Viajes por día (últimos 7 días)
    hoy = datetime.now()
    viajes_por_dia = []
    
    for i in range(6, -1, -1):
        fecha = hoy - timedelta(days=i)
        fecha_inicio = fecha.replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_fin = fecha.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        count = db.query(models.Viaje).filter(
            models.Viaje.fecha >= fecha_inicio,
            models.Viaje.fecha <= fecha_fin,
            models.Viaje.activo == True
        ).count()
        
        viajes_por_dia.append({
            "fecha": fecha.strftime("%d/%m"),
            "cantidad": count
        })
    
    # Top 5 destinos más solicitados
    destinos_populares = db.query(
        models.Viaje.destino,
        func.count(models.Viaje.id).label('cantidad')
    ).filter(
        models.Viaje.activo == True,
        models.Viaje.destino.isnot(None)
    ).group_by(
        models.Viaje.destino
    ).order_by(
        func.count(models.Viaje.id).desc()
    ).limit(5).all()
    
    # ✅ NUEVOS DATOS: Usuarios y Vehículos Inactivos
    usuarios_inactivos = db.query(models.Usuario).filter(
        models.Usuario.activo == False
    ).limit(10).all()
    
    vehiculos_inactivos = db.query(models.Vehiculo).filter(
        models.Vehiculo.activo == False
    ).limit(10).all()
    
    # Contar totales de inactivos
    total_usuarios_inactivos = db.query(models.Usuario).filter(
        models.Usuario.activo == False
    ).count()
    
    total_vehiculos_inactivos = db.query(models.Vehiculo).filter(
        models.Vehiculo.activo == False
    ).count()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "total_usuarios": total_usuarios,
        "total_conductores": total_conductores,
        "total_vehiculos": total_vehiculos,
        "total_viajes": total_viajes,
        "viajes_completados": viajes_completados,
        "viajes_en_curso": viajes_en_curso,
        "viajes_pendientes": viajes_pendientes,
        "viajes_cancelados": viajes_cancelados,
        "ingresos_totales": ingresos_totales,
        "ingreso_promedio": ingreso_promedio,
        "viajes_por_dia": viajes_por_dia,
        "destinos_populares": destinos_populares,
        # ✅ NUEVOS DATOS
        "usuarios_inactivos": usuarios_inactivos,
        "vehiculos_inactivos": vehiculos_inactivos,
        "total_usuarios_inactivos": total_usuarios_inactivos,
        "total_vehiculos_inactivos": total_vehiculos_inactivos
    })

@app.get("/conductores", tags=["Páginas HTML"])
def conductores_page(request: Request):
    """Página de gestión de conductores"""
    return templates.TemplateResponse("conductores.html", {"request": request})


@app.get("/vehiculos", tags=["Páginas HTML"])
def vehiculos_page(request: Request):
    """Página de gestión de vehículos"""
    return templates.TemplateResponse("vehiculos.html", {"request": request})


@app.get("/viajes", tags=["Páginas HTML"])
def viajes_page(request: Request):
    """Página de gestión de viajes"""
    return templates.TemplateResponse("viajes.html", {"request": request})


@app.get("/buscar", tags=["Páginas HTML"])
def buscar_page(request: Request):
    """Página de búsqueda global"""
    return templates.TemplateResponse("buscar.html", {"request": request})


@app.get("/inactivos", tags=["Páginas HTML"])
def inactivos_page(request: Request, db: Session = Depends(get_db)):
    """Página de gestión de usuarios, conductores y vehículos inactivos"""
    from sqlalchemy.orm import joinedload
    
    # Obtener usuarios inactivos
    usuarios_inactivos = db.query(models.Usuario).filter(
        models.Usuario.activo == False
    ).all()
    
    # Obtener conductores inactivos con sus vehículos
    conductores_inactivos = db.query(models.Conductor).options(
        joinedload(models.Conductor.vehiculos)
    ).filter(
        models.Conductor.activo == False
    ).all()
    
    # Obtener vehículos inactivos
    vehiculos_inactivos = db.query(models.Vehiculo).filter(
        models.Vehiculo.activo == False
    ).all()
    
    # Contar totales
    total_usuarios = len(usuarios_inactivos)
    total_conductores = len(conductores_inactivos)
    total_vehiculos = len(vehiculos_inactivos)
    
    # Obtener estadísticas para el gráfico
    from sqlalchemy import func
    from datetime import datetime
    
    # Datos para el gráfico de estados
    viajes_completados = db.query(models.Viaje).filter(
        models.Viaje.estado == 'completado',
        models.Viaje.activo == True
    ).count()
    
    viajes_en_curso = db.query(models.Viaje).filter(
        models.Viaje.estado == 'en_curso',
        models.Viaje.activo == True
    ).count()
    
    viajes_pendientes = db.query(models.Viaje).filter(
        models.Viaje.estado == 'pendiente',
        models.Viaje.activo == True
    ).count()
    
    viajes_cancelados = db.query(models.Viaje).filter(
        models.Viaje.estado == 'cancelado',
        models.Viaje.activo == True
    ).count()
    
    return templates.TemplateResponse("inactivos.html", {
        "request": request,
        "usuarios": usuarios_inactivos,
        "conductores": conductores_inactivos,
        "vehiculos": vehiculos_inactivos,
        "total_usuarios": total_usuarios,
        "total_conductores": total_conductores,
        "total_vehiculos": total_vehiculos,
        "viajes_completados": viajes_completados,
        "viajes_en_curso": viajes_en_curso,
        "viajes_pendientes": viajes_pendientes,
        "viajes_cancelados": viajes_cancelados
    })


# ============================================
# 👤 USUARIOS HTML
# ============================================

@app.get("/usuarios", tags=["Usuarios HTML"])
def usuarios_crear_form(request: Request):
    """Formulario para crear nuevo usuario"""
    return templates.TemplateResponse("Usuarios.html", {"request": request})


@app.get("/lista-usuarios", tags=["Usuarios HTML"])
def lista_usuarios_page(request: Request, db: Session = Depends(get_db)):
    """Lista completa de todos los usuarios activos"""
    usuarios = db.query(models.Usuario).filter(models.Usuario.activo == True).all()
    return templates.TemplateResponse("lista_usuarios.html", {
        "request": request,
        "usuarios": usuarios
    })


@app.get("/usuarios-inactivos", tags=["Usuarios HTML"])
def usuarios_inactivos_page(request: Request, db: Session = Depends(get_db)):
    """Página de usuarios inactivos"""
    usuarios_inactivos = db.query(models.Usuario).filter(models.Usuario.activo == False).all()
    return templates.TemplateResponse("usuarios_inactivos.html", {
        "request": request,
        "usuarios": usuarios_inactivos
    })


@app.get("/usuarios/nuevo", tags=["Usuarios HTML"])
def nuevo_usuario_form(request: Request):
    """Formulario para crear nuevo usuario (ruta alternativa)"""
    return templates.TemplateResponse("Usuarios.html", {"request": request})


@app.post("/usuarios/nuevo", tags=["Usuarios HTML"])
async def crear_usuario_html(
    request: Request,
    nombre: str = Form(...),
    telefono: str = Form(...),
    foto: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Crear usuario desde formulario HTML con foto obligatoria"""
    
    # Validar que sea imagen
    if not foto.content_type.startswith("image/"):
        raise HTTPException(400, "El archivo debe ser una imagen")
    
    # Validar tamaño (5MB máximo)
    foto.file.seek(0, 2)
    file_size = foto.file.tell()
    foto.file.seek(0)
    
    if file_size > 5 * 1024 * 1024:
        raise HTTPException(400, "La imagen no debe superar 5MB")
    
    # Generar nombre único para la foto
    ext = foto.filename.split(".")[-1]
    filename = f"usuario_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = UPLOAD_DIR / filename
    
    # Guardar archivo
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(foto.file, buffer)
    
    foto_path = f"/static/uploads/{filename}"
    
    print(f"✅ Imagen guardada: {filepath}")
    
    # Crear usuario SIN contraseña
    db_usuario = models.Usuario(
        nombre=nombre.strip(),
        telefono=telefono.strip(),
        foto_path=foto_path,
        password_hash=None,
        activo=True
    )
    
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    
    return {
        "mensaje": f"Usuario '{nombre}' creado exitosamente",
        "id": db_usuario.id,
        "foto_path": foto_path
    }


# ============================================
# 👥 USUARIOS API
# ============================================

@app.get("/api/usuarios/", tags=["Usuarios API"])
def listar_usuarios(db: Session = Depends(get_db)):
    """Listar todos los usuarios"""
    return db.query(models.Usuario).all()


@app.post("/api/usuarios/", tags=["Usuarios API"])
def crear_usuario_api(usuario: schemas.UsuarioCrear, db: Session = Depends(get_db)):
    """Crear usuario desde API"""
    return crud.crear_usuario(db, usuario)


@app.patch("/api/usuarios/{usuario_id}/inactivar", tags=["Usuarios API"])
def inactivar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Inactivar un usuario"""
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(404, "Usuario no encontrado")
    usuario.activo = False
    db.commit()
    db.refresh(usuario)
    return {"mensaje": f"Usuario '{usuario.nombre}' inactivado", "activo": usuario.activo}

@app.patch("/api/usuarios/{usuario_id}/reactivar", tags=["Usuarios API"])
def reactivar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Reactivar un usuario inactivo"""
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(404, "Usuario no encontrado")
    
    if usuario.activo:
        raise HTTPException(400, "El usuario ya está activo")
    
    usuario.activo = True
    db.commit()
    db.refresh(usuario)
    return {
        "mensaje": f"Usuario '{usuario.nombre}' reactivado exitosamente", 
        "activo": usuario.activo
    }


@app.delete("/api/usuarios/{usuario_id}", tags=["Usuarios API"])
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Eliminar usuario permanentemente"""
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(404, "Usuario no encontrado")
    db.delete(usuario)
    db.commit()
    return {"mensaje": "Usuario eliminado correctamente"}


@app.get("/api/usuarios/estado/{activo}", tags=["Usuarios API"])
def listar_usuarios_por_estado(activo: bool, db: Session = Depends(get_db)):
    """Filtrar usuarios por estado (activo/inactivo)"""
    return db.query(models.Usuario).filter(models.Usuario.activo == activo).all()


@app.get("/api/usuarios/buscar/{nombre}", tags=["Usuarios API"])
def buscar_usuario_por_nombre(nombre: str, db: Session = Depends(get_db)):
    """Buscar usuarios por nombre"""
    usuarios = db.query(models.Usuario).filter(
        models.Usuario.nombre.ilike(f"%{nombre}%")
    ).all()
    if not usuarios:
        raise HTTPException(404, "No se encontraron usuarios")
    return usuarios


# ============================================
# 🏍️ CONDUCTORES API
# ============================================

@app.get("/api/conductores/", tags=["Conductores API"])
def listar_conductores(db: Session = Depends(get_db)):
    """Listar todos los conductores activos"""
    return crud.obtener_conductores(db)


@app.post("/api/conductores/", tags=["Conductores API"])
def crear_conductor(conductor: schemas.ConductorCrear, db: Session = Depends(get_db)):
    """Crear un conductor y opcionalmente su vehículo"""
    # Crear conductor
    nuevo_conductor = crud.crear_conductor(db, conductor)
    
    # Si pidió crear vehículo, crearlo y asignarlo al conductor
    if conductor.crear_vehiculo and conductor.placa_vehiculo:
        vehiculo_data = schemas.VehiculoCrear(
            placa=conductor.placa_vehiculo,
            modelo=conductor.modelo_vehiculo,
            conductor_id=nuevo_conductor.id
        )
        vehiculo = crud.crear_vehiculo(db, vehiculo_data)
        print(f"✅ Vehículo {vehiculo.placa} asignado a conductor {nuevo_conductor.nombre}")
    
    return nuevo_conductor


@app.patch("/api/conductores/{conductor_id}/inactivar", tags=["Conductores API"])
def inactivar_conductor(conductor_id: int, db: Session = Depends(get_db)):
    """Inactivar un conductor"""
    conductor = db.query(models.Conductor).filter(models.Conductor.id == conductor_id).first()
    if not conductor:
        raise HTTPException(404, "Conductor no encontrado")
    conductor.activo = False
    db.commit()
    db.refresh(conductor)
    return {"mensaje": f"Conductor '{conductor.nombre}' inactivado", "activo": conductor.activo}


@app.patch("/api/conductores/{conductor_id}/activar", tags=["Conductores API"])
def activar_conductor(conductor_id: int, db: Session = Depends(get_db)):
    """Reactivar un conductor inactivo"""
    conductor = db.query(models.Conductor).filter(models.Conductor.id == conductor_id).first()
    if not conductor:
        raise HTTPException(404, "Conductor no encontrado")
    
    conductor.activo = True
    db.commit()
    db.refresh(conductor)
    
    return {
        "mensaje": f"Conductor '{conductor.nombre}' reactivado exitosamente",
        "activo": conductor.activo
    }


@app.get("/api/conductores/estado/{activo}", tags=["Conductores API"])
def listar_conductores_por_estado(activo: bool, db: Session = Depends(get_db)):
    """Filtrar conductores por estado"""
    return db.query(models.Conductor).filter(models.Conductor.activo == activo).all()


@app.delete("/api/conductores/{conductor_id}", tags=["Conductores API"])
def eliminar_conductor(conductor_id: int, db: Session = Depends(get_db)):
    """Eliminar conductor permanentemente"""
    conductor = db.query(models.Conductor).filter(models.Conductor.id == conductor_id).first()
    if not conductor:
        raise HTTPException(404, "Conductor no encontrado")
    db.delete(conductor)
    db.commit()
    return {"mensaje": "Conductor eliminado correctamente"}


@app.get("/api/conductores/{conductor_id}/estado", tags=["Conductores API"])
def verificar_estado_conductor(conductor_id: int, db: Session = Depends(get_db)):
    """Verificar si un conductor está libre u ocupado"""
    conductor = crud.obtener_conductor_por_id(db, conductor_id)
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")
    
    esta_libre = crud.conductor_esta_libre(db, conductor_id)
    viajes_activos = crud.obtener_viajes_activos_por_conductor(db, conductor_id)
    
    return {
        "conductor": conductor,
        "esta_libre": esta_libre,
        "estado": "libre" if esta_libre else "ocupado",
        "viajes_activos": len(viajes_activos),
        "vehiculos": conductor.vehiculos
    }


# ============================================
# 🚗 VEHÍCULOS API
# ============================================

@app.get("/api/vehiculos/", tags=["Vehículos API"])
def listar_vehiculos(db: Session = Depends(get_db)):
    """Obtener lista de todos los vehículos"""
    return crud.obtener_vehiculos(db)


@app.post("/api/vehiculos/", tags=["Vehículos API"])
def crear_vehiculo(vehiculo: schemas.VehiculoCrear, db: Session = Depends(get_db)):
    """Crear un nuevo vehículo"""
    nuevo_vehiculo = crud.crear_vehiculo(db, vehiculo)
    print(f"✅ Vehículo creado: {nuevo_vehiculo.placa} (Conductor ID: {nuevo_vehiculo.conductor_id})")
    return nuevo_vehiculo


@app.patch("/api/vehiculos/{vehiculo_id}/inactivar", tags=["Vehículos API"])
def inactivar_vehiculo(vehiculo_id: int, db: Session = Depends(get_db)):
    """Inactivar un vehículo"""
    vehiculo = db.query(models.Vehiculo).filter(models.Vehiculo.id == vehiculo_id).first()
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    vehiculo.activo = False
    db.commit()
    db.refresh(vehiculo)
    return {
        "mensaje": f"Vehículo con placa '{vehiculo.placa}' inactivado correctamente",
        "activo": vehiculo.activo
    }


@app.patch("/api/vehiculos/{vehiculo_id}/activar", tags=["Vehículos API"])
def activar_vehiculo(vehiculo_id: int, db: Session = Depends(get_db)):
    """Reactivar un vehículo inactivo"""
    vehiculo = db.query(models.Vehiculo).filter(models.Vehiculo.id == vehiculo_id).first()
    if not vehiculo:
        raise HTTPException(404, "Vehículo no encontrado")
    
    vehiculo.activo = True
    db.commit()
    db.refresh(vehiculo)
    
    return {
        "mensaje": f"Vehículo '{vehiculo.placa}' reactivado exitosamente",
        "activo": vehiculo.activo
    }


@app.get("/api/vehiculos/estado/{activo}", tags=["Vehículos API"])
def listar_vehiculos_por_estado(activo: bool, db: Session = Depends(get_db)):
    """Filtrar vehículos por estado"""
    return db.query(models.Vehiculo).filter(models.Vehiculo.activo == activo).all()


@app.get("/api/vehiculos/buscar/{placa}", tags=["Vehículos API"])
def buscar_vehiculo_por_placa(placa: str, db: Session = Depends(get_db)):
    """Buscar vehículos por placa"""
    vehiculos = db.query(models.Vehiculo).filter(
        models.Vehiculo.placa.ilike(f"%{placa}%")
    ).all()
    if not vehiculos:
        raise HTTPException(status_code=404, detail="No se encontraron vehículos")
    return vehiculos


@app.get("/api/vehiculos/conductor/{conductor_id}", tags=["Vehículos API"])
def obtener_vehiculos_de_conductor(conductor_id: int, db: Session = Depends(get_db)):
    """Obtener todos los vehículos de un conductor específico"""
    vehiculos = crud.obtener_vehiculos_por_conductor(db, conductor_id)
    return {
        "conductor_id": conductor_id,
        "vehiculos": vehiculos,
        "total": len(vehiculos)
    }


@app.delete("/api/vehiculos/{vehiculo_id}", tags=["Vehículos API"])
def eliminar_vehiculo(vehiculo_id: int, db: Session = Depends(get_db)):
    """Eliminar vehículo permanentemente"""
    vehiculo = db.query(models.Vehiculo).filter(models.Vehiculo.id == vehiculo_id).first()
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    db.delete(vehiculo)
    db.commit()
    return {"mensaje": "Vehículo eliminado correctamente"}


# ============================================
# 🚖 VIAJES API
# ============================================

@app.get("/api/viajes/", tags=["Viajes API"])
def listar_viajes(db: Session = Depends(get_db)):
    """Obtener lista de todos los viajes"""
    return crud.obtener_viajes(db)


@app.post("/api/viajes/", tags=["Viajes API"])
def crear_viaje(viaje: schemas.ViajeCrear, db: Session = Depends(get_db)):
    """Crear un nuevo viaje"""
    nuevo_viaje = crud.crear_viaje(db, viaje)
    print(f"✅ Viaje creado: ID={nuevo_viaje.id}, Conductor={nuevo_viaje.conductor_id}, Vehículo={nuevo_viaje.vehiculo_id}")
    return nuevo_viaje


@app.patch("/api/viajes/{viaje_id}/completar", tags=["Viajes API"])
def completar_viaje_endpoint(viaje_id: int, db: Session = Depends(get_db)):
    """Marcar un viaje como COMPLETADO - El conductor quedará LIBRE"""
    viaje = crud.completar_viaje(db, viaje_id)
    if not viaje:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    
    conductor_libre = crud.conductor_esta_libre(db, viaje.conductor_id)
    
    return {
        "mensaje": "Viaje completado exitosamente",
        "viaje": viaje,
        "conductor_libre": conductor_libre
    }


@app.patch("/api/viajes/{viaje_id}/cancelar", tags=["Viajes API"])
def cancelar_viaje_endpoint(viaje_id: int, db: Session = Depends(get_db)):
    """Cancelar un viaje - El conductor quedará LIBRE"""
    viaje = crud.cancelar_viaje(db, viaje_id)
    if not viaje:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    
    conductor_libre = crud.conductor_esta_libre(db, viaje.conductor_id)
    
    return {
        "mensaje": "Viaje cancelado",
        "viaje": viaje,
        "conductor_libre": conductor_libre
    }


@app.patch("/api/viajes/{viaje_id}/estado", tags=["Viajes API"])
def actualizar_estado_viaje_endpoint(
    viaje_id: int, 
    actualizacion: schemas.ViajeActualizar,
    db: Session = Depends(get_db)
):
    """Actualizar el estado de un viaje"""
    viaje = crud.actualizar_estado_viaje(db, viaje_id, actualizacion.estado)
    if not viaje:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    
    return {
        "mensaje": f"Estado actualizado a: {actualizacion.estado}",
        "viaje": viaje
    }


@app.get("/api/viajes/conductor/{conductor_id}/activos", tags=["Viajes API"])
def obtener_viajes_activos_conductor(conductor_id: int, db: Session = Depends(get_db)):
    """Obtener viajes activos (en_curso o pendiente) de un conductor"""
    viajes = crud.obtener_viajes_activos_por_conductor(db, conductor_id)
    return {
        "conductor_id": conductor_id,
        "viajes_activos": viajes,
        "total": len(viajes),
        "esta_libre": len(viajes) == 0
    }


@app.delete("/api/viajes/{viaje_id}", tags=["Viajes API"])
def eliminar_viaje(viaje_id: int, db: Session = Depends(get_db)):
    """Eliminar viaje permanentemente"""
    viaje = crud.eliminar_viaje(db, viaje_id)
    if not viaje:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    return {"mensaje": "Viaje eliminado correctamente"}


# ============================================
# 📸 SUBIDA DE IMÁGENES
# ============================================

@app.post("/api/upload/usuario/{usuario_id}", tags=["Uploads"])
async def subir_foto_usuario(usuario_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Subir foto de perfil de usuario"""
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(404, "Usuario no encontrado")
    
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "El archivo debe ser una imagen")
    
    ext = file.filename.split(".")[-1]
    filename = f"usuario_{usuario_id}_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = UPLOAD_DIR / filename
    
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    usuario.foto_path = f"/static/uploads/{filename}"
    db.commit()
    
    print(f"✅ Foto de usuario guardada: {filepath}")
    
    return {"mensaje": "Foto subida exitosamente", "ruta": usuario.foto_path}


@app.post("/api/upload/conductor/{conductor_id}", tags=["Uploads"])
async def subir_foto_conductor(conductor_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Subir foto de conductor"""
    conductor = db.query(models.Conductor).filter(models.Conductor.id == conductor_id).first()
    if not conductor:
        raise HTTPException(404, "Conductor no encontrado")
    
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "El archivo debe ser una imagen")
    
    ext = file.filename.split(".")[-1]
    filename = f"conductor_{conductor_id}_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = UPLOAD_DIR / filename
    
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    conductor.foto_path = f"/static/uploads/{filename}"
    db.commit()
    
    print(f"✅ Foto de conductor guardada: {filepath}")
    
    return {"mensaje": "Foto subida exitosamente", "ruta": conductor.foto_path}


@app.post("/api/upload/vehiculo/{vehiculo_id}", tags=["Uploads"])
async def subir_foto_vehiculo(vehiculo_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Subir foto de vehículo"""
    vehiculo = db.query(models.Vehiculo).filter(models.Vehiculo.id == vehiculo_id).first()
    if not vehiculo:
        raise HTTPException(404, "Vehículo no encontrado")
    
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "El archivo debe ser una imagen")
    
    ext = file.filename.split(".")[-1]
    filename = f"vehiculo_{vehiculo_id}_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = UPLOAD_DIR / filename
    
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    vehiculo.foto_path = f"/static/uploads/{filename}"
    db.commit()
    
    print(f"✅ Foto de vehículo guardada: {filepath}")
    
    return {"mensaje": "Foto subida exitosamente", "ruta": vehiculo.foto_path}


# ============================================
# 🔍 BÚSQUEDA GLOBAL
# ============================================

@app.get("/api/buscar", tags=["Búsqueda"])
def buscar_global(q: str, db: Session = Depends(get_db)):
    """Búsqueda global en usuarios, conductores y vehículos activos"""
    if not q or len(q.strip()) < 2:
        raise HTTPException(400, "Escribe al menos 2 caracteres")
    
    query = q.strip()
    
    # Buscar usuarios activos
    usuarios = db.query(models.Usuario).filter(
        (models.Usuario.nombre.ilike(f"%{query}%")) | 
        (models.Usuario.telefono.ilike(f"%{query}%"))
    ).filter(models.Usuario.activo == True).all()
    
    # Buscar conductores activos
    conductores = db.query(models.Conductor).filter(
        models.Conductor.nombre.ilike(f"%{query}%")
    ).filter(models.Conductor.activo == True).all()
    
    # Buscar vehículos activos
    vehiculos = db.query(models.Vehiculo).filter(
        models.Vehiculo.placa.ilike(f"%{query}%")
    ).filter(models.Vehiculo.activo == True).all()
    
    total = len(usuarios) + len(conductores) + len(vehiculos)
    
    return {
        "usuarios": usuarios,
        "conductores": conductores,
        "vehiculos": vehiculos,
        "total": total
    }