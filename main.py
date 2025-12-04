from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from fastapi import Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
import shutil
import uuid
import models, schemas, crud

from database import engine, get_db, Base

# ⚙️ CREA LA BASE DE DATOS AUTOMÁTICAMENTE
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

# 📸 CARPETA PARA UPLOADS
UPLOAD_DIR = Path("app/static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

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
def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/conductores", tags=["Páginas HTML"])
def conductores_page(request: Request):
    return templates.TemplateResponse("conductores.html", {"request": request})


@app.get("/vehiculos", tags=["Páginas HTML"])
def vehiculos_page(request: Request):
    return templates.TemplateResponse("vehiculos.html", {"request": request})


@app.get("/viajes", tags=["Páginas HTML"])
def viajes_page(request: Request):
    """Página de gestión de viajes"""
    return templates.TemplateResponse("viajes.html", {"request": request})


@app.get("/buscar", tags=["Páginas HTML"])
def buscar_page(request: Request):
    """Página de búsqueda"""
    return templates.TemplateResponse("buscar.html", {"request": request})


# ============================================
# 👤 USUARIOS HTML
# ============================================

@app.get("/usuarios", tags=["Usuarios HTML"])
def usuarios_lista(request: Request, db: Session = Depends(get_db)):
    """Lista de usuarios (página principal)"""
    usuarios = db.query(models.Usuario).filter(models.Usuario.activo == True).all()
    return templates.TemplateResponse("Usuarios.html", {
        "request": request,
        "usuarios": usuarios
    })


@app.get("/usuarios/nuevo", tags=["Usuarios HTML"])
def nuevo_usuario_form(request: Request):
    """Formulario para crear nuevo usuario"""
    return templates.TemplateResponse("usuario_form.html", {"request": request})


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
    import uuid
    ext = foto.filename.split(".")[-1]
    filename = f"usuario_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = UPLOAD_DIR / filename
    
    # Guardar archivo
    import shutil
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(foto.file, buffer)
    
    foto_path = f"/static/uploads/{filename}"
    
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
    return db.query(models.Usuario).all()


@app.post("/api/usuarios/", tags=["Usuarios API"])
def crear_usuario_api(usuario: schemas.UsuarioCrear, db: Session = Depends(get_db)):
    return crud.crear_usuario(db, usuario)


@app.patch("/api/usuarios/{usuario_id}/inactivar", tags=["Usuarios API"])
def inactivar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(404, "Usuario no encontrado")
    usuario.activo = False
    db.commit()
    db.refresh(usuario)
    return {"mensaje": f"Usuario '{usuario.nombre}' inactivado", "activo": usuario.activo}


@app.delete("/api/usuarios/{usuario_id}", tags=["Usuarios API"])
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(404, "Usuario no encontrado")
    db.delete(usuario)
    db.commit()
    return {"mensaje": "Usuario eliminado correctamente"}


@app.get("/api/usuarios/estado/{activo}", tags=["Usuarios API"])
def listar_usuarios_por_estado(activo: bool, db: Session = Depends(get_db)):
    return db.query(models.Usuario).filter(models.Usuario.activo == activo).all()


@app.get("/api/usuarios/buscar/{nombre}", tags=["Usuarios API"])
def buscar_usuario_por_nombre(nombre: str, db: Session = Depends(get_db)):
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
    return crud.obtener_conductores(db)


@app.post("/api/conductores/", tags=["Conductores API"])
def crear_conductor(conductor: schemas.ConductorCrear, db: Session = Depends(get_db)):
    # Si viene con datos de vehículo, crearlo también
    if hasattr(conductor, 'crear_vehiculo') and conductor.crear_vehiculo:
        # Crear conductor
        nuevo_conductor = crud.crear_conductor(db, conductor)
        
        # Crear vehículo asociado
        if conductor.placa_vehiculo:
            vehiculo_data = schemas.VehiculoCrear(
                placa=conductor.placa_vehiculo,
                modelo=conductor.modelo_vehiculo
            )
            vehiculo = crud.crear_vehiculo(db, vehiculo_data, conductor_id=nuevo_conductor.id)
        
        return nuevo_conductor
    
    return crud.crear_conductor(db, conductor)


@app.patch("/api/conductores/{conductor_id}/inactivar", tags=["Conductores API"])
def inactivar_conductor(conductor_id: int, db: Session = Depends(get_db)):
    conductor = db.query(models.Conductor).filter(models.Conductor.id == conductor_id).first()
    if not conductor:
        raise HTTPException(404, "Conductor no encontrado")
    conductor.activo = False
    db.commit()
    db.refresh(conductor)
    return {"mensaje": f"Conductor '{conductor.nombre}' inactivado", "activo": conductor.activo}


@app.get("/api/conductores/estado/{activo}", tags=["Conductores API"])
def listar_conductores_por_estado(activo: bool, db: Session = Depends(get_db)):
    return db.query(models.Conductor).filter(models.Conductor.activo == activo).all()


@app.delete("/api/conductores/{conductor_id}", tags=["Conductores API"])
def eliminar_conductor(conductor_id: int, db: Session = Depends(get_db)):
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
    return crud.crear_vehiculo(db, vehiculo)


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
    return crud.crear_viaje(db, viaje)


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
    
    return {"mensaje": "Foto subida exitosamente", "ruta": vehiculo.foto_path}


# ============================================
# 🔍 BÚSQUEDA GLOBAL
# ============================================

@app.get("/api/buscar", tags=["Búsqueda"])
def buscar_global(q: str, db: Session = Depends(get_db)):
    """Búsqueda global"""
    if not q or len(q.strip()) < 2:
        raise HTTPException(400, "Escribe al menos 2 caracteres")
    
    query = q.strip()
    
    # Buscar usuarios
    usuarios = db.query(models.Usuario).filter(
        (models.Usuario.nombre.ilike(f"%{query}%")) | 
        (models.Usuario.telefono.ilike(f"%{query}%"))
    ).filter(models.Usuario.activo == True).all()
    
    # Buscar conductores
    conductores = db.query(models.Conductor).filter(
        models.Conductor.nombre.ilike(f"%{query}%")
    ).filter(models.Conductor.activo == True).all()
    
    # Buscar vehículos
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