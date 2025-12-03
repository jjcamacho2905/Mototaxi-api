from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas, database

router = APIRouter()

@router.post("/", response_model=schemas.Usuario)
def create_user(user: schemas.UsuarioCrear, db: Session = Depends(database.get_db)):
    return crud.crear_usuario(db, user)


@router.get("/", response_model=list[schemas.Usuario])
def list_users(db: Session = Depends(database.get_db)):
    return crud.obtener_usuarios(db)


@router.get("/{user_id}", response_model=schemas.Usuario)
def get_user(user_id: int, db: Session = Depends(database.get_db)):
    user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(database.get_db)):
    user = crud.inactivar_usuario(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"detail": "Usuario desactivado"}
