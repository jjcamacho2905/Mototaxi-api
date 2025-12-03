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


# ============================================
# 🔐 LOGIN & REGISTRO
# ============================================

@app.get("/", tags=["Autenticación"])
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", tags=["Autenticación"])
def login(request: Request,
          username: str = Form(...),
          password: str = Form(...),
          db: Session = Depends(get_db)):

    usuario = crud.autenticar_usuario(db, username, password)

    if not usuario:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Usuario o contraseña incorrectos"}
        )

    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/register", tags=["Autenticación"])
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register", tags=["Autenticación"])
def register_user(
    request: Request,
    nombre: str = Form(...),
    telefono: str = Form(...),
    contrasena: str = Form(...),
    db: Session = Depends(get_db)
):
    """Registrar un nuevo usuario"""
    # Verificar si el usuario ya existe
    usuario_existente = db.query(models.Usuario).filter(
        models.Usuario.nombre == nombre
    ).first()
    
    if usuario_existente:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "El usuario ya existe"}
        )
    
    # Crear nuevo usuario usando el schema correcto
    nuevo_usuario = schemas.UsuarioCrear(
        nombre=nombre,
        telefono=telefono,
        contrasena=contrasena
    )
    crud.crear_usuario(db, nuevo_usuario)
    
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "mensaje": "Usuario registrado exitosamente"}
    )


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


# ============================================
# 👤 USUARIOS HTML
# ============================================

@app.get("/usuarios", tags=["Usuarios HTML"])
def usuarios_html(request: Request, db: Session = Depends(get_db)):
    usuarios = db.query(models.Usuario).all()
    return templates.TemplateResponse(
        "usuarios.html", {"request": request, "usuarios": usuarios}
    )


@app.get("/usuarios/nuevo", tags=["Usuarios HTML"])
def nuevo_usuario_form(request: Request):
    return templates.TemplateResponse("usuario_form.html", {"request": request})


@app.post("/usuarios/nuevo", tags=["Usuarios HTML"])
async def crear_usuario_html(
    request: Request,
    nombre: str = Form(...),
    telefono: str = Form(...),
    contrasena: str = Form(...),
    foto: UploadFile = File(None),  # ← NUEVO: imagen opcional
    db: Session = Depends(get_db)
):
    """Crear usuario desde formulario HTML con foto"""
    
    # Crear usuario
    nuevo = schemas.UsuarioCrear(
        nombre=nombre,
        telefono=telefono,
        contrasena=contrasena
    )
    usuario_creado = crud.crear_usuario(db, nuevo)
    
    # Subir foto si existe
    if foto and foto.filename:
        if foto.content_type.startswith("image/"):
            extension = foto.filename.split(".")[-1]
            filename = f"usuario_{usuario_creado.id}_{uuid.uuid4()}.{extension}"
            filepath = UPLOAD_DIR / filename
            
            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(foto.file, buffer)
            
            usuario_creado.foto_path = f"/static/uploads/{filename}"
            db.commit()
    
    return templates.TemplateResponse(
        "usuario_ok.html",
        {"request": request, "nombre": nombre}
    )
    
@app.get("/viajes", tags=["Páginas HTML"])
def viajes_page(request: Request):
    """Página de gestión de viajes"""
    return templates.TemplateResponse("viajes.html", {"request": request})


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
    usuario = crud.inactivar_usuario(db, usuario_id)
    if not usuario:
        raise HTTPException(404, "Usuario no encontrado")
    return {"mensaje": f"Usuario '{usuario.nombre}' inactivado", "activo": usuario.activo}


@app.delete("/api/usuarios/{usuario_id}", tags=["Usuarios API"])
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    eliminado = crud.eliminar_usuario(db, usuario_id)
    if not eliminado:
        raise HTTPException(404, "Usuario no encontrado")
    return {"mensaje": "Usuario eliminado correctamente"}


@app.get("/api/usuarios/estado/{activo}", tags=["Usuarios API"])
def listar_usuarios_por_estado(activo: bool, db: Session = Depends(get_db)):
    return crud.obtener_usuarios_por_estado(db, activo)


@app.get("/api/usuarios/buscar/{nombre}", tags=["Usuarios API"])
def buscar_usuario_por_nombre(nombre: str, db: Session = Depends(get_db)):
    usuarios = crud.buscar_usuario_por_nombre(db, nombre)
    if not usuarios:
        raise HTTPException(404, "No se encontraron usuarios")
    return usuarios


# ============================================
# 🏍️ CONDUCTORES API
# (SIN CAMBIOS)
# ============================================

@app.get("/api/conductores/", tags=["Conductores API"])
def listar_conductores(db: Session = Depends(get_db)):
    return crud.obtener_conductores(db)


@app.post("/api/conductores/", tags=["Conductores API"])
def crear_conductor(conductor: schemas.ConductorCrear, db: Session = Depends(get_db)):
    return crud.crear_conductor(db, conductor)


@app.patch("/api/conductores/{conductor_id}/inactivar", tags=["Conductores API"])
def inactivar_conductor(conductor_id: int, db: Session = Depends(get_db)):
    conductor = crud.inactivar_conductor(db, conductor_id)
    if not conductor:
        raise HTTPException(404, "Conductor no encontrado")
    return {"mensaje": f"Conductor '{conductor.nombre}' inactivado", "activo": conductor.activo}


@app.get("/api/conductores/estado/{activo}", tags=["Conductores API"])
def listar_conductores_por_estado(activo: bool, db: Session = Depends(get_db)):
    return crud.obtener_conductores_por_estado(db, activo)


@app.delete("/api/conductores/{conductor_id}", tags=["Conductores API"])
def eliminar_conductor(conductor_id: int, db: Session = Depends(get_db)):
    eliminado = crud.eliminar_conductor(db, conductor_id)
    if not eliminado:
        raise HTTPException(404, "Conductor no encontrado")
    return {"mensaje": "Conductor eliminado correctamente"}


# ============================================
# 🚗 SECCIÓN: VEHÍCULOS API
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
    vehiculo = crud.inactivar_vehiculo(db, vehiculo_id)
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return {
        "mensaje": f"Vehículo con placa '{vehiculo.placa}' inactivado correctamente",
        "activo": vehiculo.activo
    }


@app.get("/api/vehiculos/estado/{activo}", tags=["Vehículos API"])
def listar_vehiculos_por_estado(activo: bool, db: Session = Depends(get_db)):
    """Filtrar vehículos por estado"""
    return crud.obtener_vehiculos_por_estado(db, activo)


@app.get("/api/vehiculos/buscar/{placa}", tags=["Vehículos API"])
def buscar_vehiculo_por_placa(placa: str, db: Session = Depends(get_db)):
    """Buscar vehículos por placa"""
    vehiculos = crud.buscar_vehiculo_por_placa(db, placa)
    if not vehiculos:
        raise HTTPException(status_code=404, detail="No se encontraron vehículos")
    return vehiculos


@app.delete("/api/vehiculos/{vehiculo_id}", tags=["Vehículos API"])
def eliminar_vehiculo(vehiculo_id: int, db: Session = Depends(get_db)):
    """Eliminar vehículo permanentemente"""
    eliminado = crud.eliminar_vehiculo(db, vehiculo_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return {"mensaje": "Vehículo eliminado correctamente"}


# ============================================
# 🚖 SECCIÓN: VIAJES API
# ============================================

@app.get("/api/viajes/", tags=["Viajes API"])
def listar_viajes(db: Session = Depends(get_db)):
    """Obtener lista de todos los viajes"""
    return crud.obtener_viajes(db)


@app.post("/api/viajes/", tags=["Viajes API"])
def crear_viaje(viaje: schemas.ViajeCrear, db: Session = Depends(get_db)):
    """Crear un nuevo viaje"""
    return crud.crear_viaje(db, viaje)


@app.delete("/api/viajes/{viaje_id}", tags=["Viajes API"])
def eliminar_viaje(viaje_id: int, db: Session = Depends(get_db)):
    """Eliminar viaje permanentemente"""
    eliminado = crud.eliminar_viaje(db, viaje_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    return {"mensaje": "Viaje eliminado correctamente"}


# ============================================
# 📸 SECCIÓN: SUBIDA DE IMÁGENES
# ============================================

@app.post("/api/upload/usuario/{usuario_id}", tags=["Multimedia"])
async def subir_foto_usuario(
    usuario_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Subir foto de perfil de usuario"""
    # Validar tipo de archivo
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Solo se permiten imágenes")
    
    # Buscar usuario
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Generar nombre único para el archivo
    extension = file.filename.split(".")[-1]
    filename = f"usuario_{usuario_id}_{uuid.uuid4()}.{extension}"
    filepath = UPLOAD_DIR / filename
    
    # Guardar archivo
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Actualizar ruta en base de datos
    usuario.foto_path = f"/static/uploads/{filename}"
    db.commit()
    
    return {
        "mensaje": "Foto subida exitosamente",
        "foto_path": usuario.foto_path
    }


@app.post("/api/upload/conductor/{conductor_id}", tags=["Multimedia"])
async def subir_foto_conductor(
    conductor_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Subir foto de perfil de conductor"""
    # Validar tipo de archivo
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Solo se permiten imágenes")
    
    # Buscar conductor
    conductor = db.query(models.Conductor).filter(models.Conductor.id == conductor_id).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")
    
    # Generar nombre único para el archivo
    extension = file.filename.split(".")[-1]
    filename = f"conductor_{conductor_id}_{uuid.uuid4()}.{extension}"
    filepath = UPLOAD_DIR / filename
    
    # Guardar archivo
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Actualizar ruta en base de datos
    conductor.foto_path = f"/static/uploads/{filename}"
    db.commit()
    
    return {
        "mensaje": "Foto subida exitosamente",
        "foto_path": conductor.foto_path
    }


@app.post("/api/upload/vehiculo/{vehiculo_id}", tags=["Multimedia"])
async def subir_foto_vehiculo(
    vehiculo_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Subir foto de vehículo"""
    # Validar tipo de archivo
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Solo se permiten imágenes")
    
    # Buscar vehículo
    vehiculo = db.query(models.Vehiculo).filter(models.Vehiculo.id == vehiculo_id).first()
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    
    # Generar nombre único para el archivo
    extension = file.filename.split(".")[-1]
    filename = f"vehiculo_{vehiculo_id}_{uuid.uuid4()}.{extension}"
    filepath = UPLOAD_DIR / filename
    
    # Guardar archivo
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Actualizar ruta en base de datos
    vehiculo.foto_path = f"/static/uploads/{filename}"
    db.commit()
    
    return {
        "mensaje": "Foto subida exitosamente",
        "foto_path": vehiculo.foto_path
    }


# ============================================
# 🔍 SECCIÓN: BÚSQUEDA GLOBAL
# ============================================


@app.get("/buscar", tags=["Búsqueda"])
def buscar_page(request: Request, q: str = ""):
    return templates.TemplateResponse("buscar.html", {"request": request, "query": q})


@app.get("/api/buscar", tags=["Búsqueda"])
def buscar_global(q: str, db: Session = Depends(get_db)):
    resultados = {
        "usuarios": crud.buscar_usuario_por_nombre(db, q),
        "conductores": db.query(models.Conductor).filter(models.Conductor.nombre.ilike(f"%{q}%")).all(),
        "vehiculos": crud.buscar_vehiculo_por_placa(db, q)
    }
    resultados["total"] = (
        len(resultados["usuarios"])
        + len(resultados["conductores"])
        + len(resultados["vehiculos"])
    )
    return resultados


# ============================================
# ℹ️ INFO API
# ============================================

@app.get("/info", tags=["Información"])
def info():
    return {
        "nombre": "API Mototaxi Supatá",
        "version": "1.0",
        "descripcion": "Sistema de gestión de mototaxis",
        "endpoints": {
            "docs": "/docs",
            "dashboard": "/dashboard",
            "usuarios": "/usuarios",
            "conductores": "/conductores",
            "vehiculos": "/vehiculos"
        }
    }





