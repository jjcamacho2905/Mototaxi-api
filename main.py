from fastapi import FastAPI, Depends, HTTPException
from fastapi import Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import models, schemas, crud
from database import engine, get_db, Base

# ⚙️ CREA LA BASE AUTOMÁTICAMENTE
Base.metadata.create_all(bind=engine)

app = FastAPI(title="🚖 Proyecto Mototaxi - API", version="1.0")

# TEMPLATES Y STATIC
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# ============================================
# 🔐 LOGIN y REGISTRO
# ============================================

@app.get("/")
def login_page(request: Request):
    # Aquí va el código correctamente indentado dentro de la función
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    usuario = crud.autenticar_usuario(db, username, password)

    if not usuario:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Usuario o contraseña incorrectos"}
        )

    return templates.TemplateResponse(
        "usuarios.html",
        {"request": request, "usuarios": crud.obtener_usuarios(db)}
    )


@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


# ============================================
# USUARIOS HTML
# ============================================

@app.get("/usuarios")
def usuarios_html(request: Request, db: Session = Depends(get_db)):
    usuarios = db.query(models.Usuario).all()
    return templates.TemplateResponse(
        "usuarios.html",
        {"request": request, "usuarios": usuarios}
    )


@app.get("/usuarios/nuevo")
def nuevo_usuario_form(request: Request):
    return templates.TemplateResponse("usuario_form.html", {"request": request})


@app.post("/usuarios/nuevo")
def crear_usuario_html(
    request: Request,
    nombre: str = Form(...),
    telefono: str = Form(...),
    db: Session = Depends(get_db)
):
    nuevo = schemas.UsuarioCrear(nombre=nombre, telefono=telefono)
    crud.crear_usuario(db, nuevo)
    return templates.TemplateResponse("usuario_ok.html", {"request": request})


# ============================================
# USUARIOS API
# ============================================

@app.get("/api/usuarios/", tags=["Usuarios"])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(models.Usuario).all()


@app.post("/api/usuarios/", tags=["Usuarios"])
def crear_usuario(usuario: schemas.UsuarioCrear, db: Session = Depends(get_db)):
    return crud.crear_usuario(db, usuario)


@app.patch("/api/usuarios/{usuario_id}/inactivar", tags=["Usuarios"])
def inactivar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = crud.inactivar_usuario(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {
        "mensaje": f"Usuario '{usuario.nombre}' inactivado correctamente",
        "activo": usuario.activo
    }


@app.delete("/api/usuarios/{usuario_id}", tags=["Usuarios"])
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    eliminado = crud.eliminar_usuario(db, usuario_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"mensaje": "Usuario eliminado correctamente"}


@app.get("/api/usuarios/estado/{activo}", tags=["Usuarios"])
def listar_usuarios_por_estado(activo: bool, db: Session = Depends(get_db)):
    return crud.obtener_usuarios_por_estado(db, activo)


@app.get("/api/usuarios/buscar/{nombre}", tags=["Usuarios"])
def buscar_usuario_por_nombre(nombre: str, db: Session = Depends(get_db)):
    usuarios = crud.buscar_usuario_por_nombre(db, nombre)
    if not usuarios:
        raise HTTPException(status_code=404, detail="No se encontraron usuarios con ese nombre")
    return usuarios


# ============================================
# CONDUCTORES
# ============================================

@app.get("/api/conductores/", tags=["Conductores"])
def listar_conductores(db: Session = Depends(get_db)):
    return crud.obtener_conductores(db)


@app.post("/api/conductores/", tags=["Conductores"])
def crear_conductor(conductor: schemas.ConductorCrear, db: Session = Depends(get_db)):
    return crud.crear_conductor(db, conductor)


@app.patch("/api/conductores/{conductor_id}/inactivar", tags=["Conductores"])
def inactivar_conductor(conductor_id: int, db: Session = Depends(get_db)):
    conductor = crud.inactivar_conductor(db, conductor_id)
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")
    return {
        "mensaje": f"Conductor '{conductor.nombre}' inactivado correctamente",
        "activo": conductor.activo
    }


@app.get("/api/conductores/estado/{activo}", tags=["Conductores"])
def listar_conductores_por_estado(activo: bool, db: Session = Depends(get_db)):
    return crud.obtener_conductores_por_estado(db, activo)


@app.delete("/api/conductores/{conductor_id}", tags=["Conductores"])
def eliminar_conductor(conductor_id: int, db: Session = Depends(get_db)):
    eliminado = crud.eliminar_conductor(db, conductor_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")
    return {"mensaje": "Conductor eliminado correctamente"}


# ============================================
# VEHÍCULOS
# ============================================

@app.get("/api/vehiculos/", tags=["Vehículos"])
def listar_vehiculos(db: Session = Depends(get_db)):
    return crud.obtener_vehiculos(db)


@app.post("/api/vehiculos/", tags=["Vehículos"])
def crear_vehiculo(vehiculo: schemas.VehiculoCrear, db: Session = Depends(get_db)):
    return crud.crear_vehiculo(db, vehiculo)


@app.patch("/api/vehiculos/{vehiculo_id}/inactivar", tags=["Vehículos"])
def inactivar_vehiculo(vehiculo_id: int, db: Session = Depends(get_db)):
    vehiculo = crud.inactivar_vehiculo(db, vehiculo_id)
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return {
        "mensaje": f"Vehículo con placa '{vehiculo.placa}' inactivado correctamente",
        "activo": vehiculo.activo
    }


@app.get("/api/vehiculos/estado/{activo}", tags=["Vehículos"])
def listar_vehiculos_por_estado(activo: bool, db: Session = Depends(get_db)):
    return crud.obtener_vehiculos_por_estado(db, activo)


@app.get("/api/vehiculos/buscar/{placa}", tags=["Vehículos"])
def buscar_vehiculo_por_placa(placa: str, db: Session = Depends(get_db)):
    vehiculos = crud.buscar_vehiculo_por_placa(db, placa)
    if not vehiculos:
        raise HTTPException(status_code=404, detail="No se encontraron vehículos con esa placa")
    return vehiculos


@app.delete("/api/vehiculos/{vehiculo_id}", tags=["Vehículos"])
def eliminar_vehiculo(vehiculo_id: int, db: Session = Depends(get_db)):
    eliminado = crud.eliminar_vehiculo(db, vehiculo_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return {"mensaje": "Vehículo eliminado correctamente"}


# ============================================
# VIAJES
# ============================================

@app.get("/api/viajes/", tags=["Viajes"])
def listar_viajes(db: Session = Depends(get_db)):
    return crud.obtener_viajes(db)


@app.post("/api/viajes/", tags=["Viajes"])
def crear_viaje(viaje: schemas.ViajeCrear, db: Session = Depends(get_db)):
    return crud.crear_viaje(db, viaje)


@app.delete("/api/viajes/{viaje_id}", tags=["Viajes"])
def eliminar_viaje(viaje_id: int, db: Session = Depends(get_db)):
    eliminado = crud.eliminar_viaje(db, viaje_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    return {"mensaje": "Viaje eliminado correctamente"}
