from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, crud
from database import engine, get_db, Base

# ⚙️ CREA LA BASE AUTOMÁTICAMENTE
Base.metadata.create_all(bind=engine)

app = FastAPI(title="🚖 Proyecto Mototaxi - API", version="1.0")

#Usuario
@app.get("/api/usuarios/", tags=["Usuarios"])
def listar_usuarios(db: Session = Depends(get_db)):
    """Lista todos los usuarios registrados"""
    return db.query(models.Usuario).all()


@app.post("/api/usuarios/", tags=["Usuarios"])
def crear_usuario(usuario: schemas.UsuarioCrear, db: Session = Depends(get_db)):
    """Crea un nuevo usuario"""
    return crud.crear_usuario(db, usuario)


@app.patch("/api/usuarios/{usuario_id}/inactivar", tags=["Usuarios"])
def inactivar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Inactiva un usuario sin eliminarlo"""
    usuario = crud.inactivar_usuario(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"mensaje": f"Usuario '{usuario.nombre}' inactivado correctamente", "activo": usuario.activo}


@app.delete("/api/usuarios/{usuario_id}", tags=["Usuarios"])
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Elimina un usuario permanentemente"""
    eliminado = crud.eliminar_usuario(db, usuario_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"mensaje": "Usuario eliminado correctamente"}

#endpoint
@app.get("/api/usuarios/estado/{activo}", tags=["Usuarios"])
def listar_usuarios_por_estado(activo: bool, db: Session = Depends(get_db)):
    """Filtra usuarios por estado (activos o inactivos)"""
    return crud.obtener_usuarios_por_estado(db, activo)


@app.get("/api/usuarios/buscar/{nombre}", tags=["Usuarios"])
def buscar_usuario_por_nombre(nombre: str, db: Session = Depends(get_db)):
    """Busca usuarios por nombre (atributo diferente al ID)"""
    usuarios = crud.buscar_usuario_por_nombre(db, nombre)
    if not usuarios:
        raise HTTPException(status_code=404, detail="No se encontraron usuarios con ese nombre")
    return usuarios

#Conductores
@app.get("/api/conductores/", tags=["Conductores"])
def listar_conductores(db: Session = Depends(get_db)):
    """Lista todos los conductores registrados"""
    return crud.obtener_conductores(db)


@app.post("/api/conductores/", tags=["Conductores"])
def crear_conductor(conductor: schemas.ConductorCrear, db: Session = Depends(get_db)):
    """Crea un nuevo conductor"""
    return crud.crear_conductor(db, conductor)


@app.patch("/api/conductores/{conductor_id}/inactivar", tags=["Conductores"])
def inactivar_conductor(conductor_id: int, db: Session = Depends(get_db)):
    """Inactiva un conductor sin eliminarlo"""
    conductor = crud.inactivar_conductor(db, conductor_id)
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")
    return {"mensaje": f"Conductor '{conductor.nombre}' inactivado correctamente", "activo": conductor.activo}


@app.get("/api/conductores/estado/{activo}", tags=["Conductores"])
def listar_conductores_por_estado(activo: bool, db: Session = Depends(get_db)):
    """Filtra conductores por estado (activos o inactivos)"""
    return crud.obtener_conductores_por_estado(db, activo)


@app.delete("/api/conductores/{conductor_id}", tags=["Conductores"])
def eliminar_conductor(conductor_id: int, db: Session = Depends(get_db)):
    """Elimina un conductor permanentemente"""
    eliminado = crud.eliminar_conductor(db, conductor_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")
    return {"mensaje": "Conductor eliminado correctamente"}


#Vehiculos
@app.get("/api/vehiculos/", tags=["Vehículos"])
def listar_vehiculos(db: Session = Depends(get_db)):
    """Lista todos los vehículos registrados"""
    return crud.obtener_vehiculos(db)


@app.post("/api/vehiculos/", tags=["Vehículos"])
def crear_vehiculo(vehiculo: schemas.VehiculoCrear, db: Session = Depends(get_db)):
    """Crea un nuevo vehículo"""
    return crud.crear_vehiculo(db, vehiculo)


@app.patch("/api/vehiculos/{vehiculo_id}/inactivar", tags=["Vehículos"])
def inactivar_vehiculo(vehiculo_id: int, db: Session = Depends(get_db)):
    """Inactiva un vehículo sin eliminarlo"""
    vehiculo = crud.inactivar_vehiculo(db, vehiculo_id)
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return {"mensaje": f"Vehículo con placa '{vehiculo.placa}' inactivado correctamente", "activo": vehiculo.activo}


@app.get("/api/vehiculos/estado/{activo}", tags=["Vehículos"])
def listar_vehiculos_por_estado(activo: bool, db: Session = Depends(get_db)):
    """Filtra vehículos por estado (activos o inactivos)"""
    return crud.obtener_vehiculos_por_estado(db, activo)


@app.get("/api/vehiculos/buscar/{placa}", tags=["Vehículos"])
def buscar_vehiculo_por_placa(placa: str, db: Session = Depends(get_db)):
    """Busca vehículos por placa (atributo diferente al ID)"""
    vehiculos = crud.buscar_vehiculo_por_placa(db, placa)
    if not vehiculos:
        raise HTTPException(status_code=404, detail="No se encontraron vehículos con esa placa")
    return vehiculos


@app.delete("/api/vehiculos/{vehiculo_id}", tags=["Vehículos"])
def eliminar_vehiculo(vehiculo_id: int, db: Session = Depends(get_db)):
    """Elimina un vehículo permanentemente"""
    eliminado = crud.eliminar_vehiculo(db, vehiculo_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return {"mensaje": "Vehículo eliminado correctamente"}


# Viajes
@app.get("/api/viajes/", tags=["Viajes"])
def listar_viajes(db: Session = Depends(get_db)):
    """Lista todos los viajes registrados"""
    return crud.obtener_viajes(db)


@app.post("/api/viajes/", tags=["Viajes"])
def crear_viaje(viaje: schemas.ViajeCrear, db: Session = Depends(get_db)):
    """Crea un nuevo viaje"""
    return crud.crear_viaje(db, viaje)


@app.delete("/api/viajes/{viaje_id}", tags=["Viajes"])
def eliminar_viaje(viaje_id: int, db: Session = Depends(get_db)):
    """Elimina un viaje permanentemente"""
    eliminado = crud.eliminar_viaje(db, viaje_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    return {"mensaje": "Viaje eliminado correctamente"}


