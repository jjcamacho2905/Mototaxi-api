from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas, database

router = APIRouter()

@router.post("/", response_model=schemas.DriverOut)
def create_driver(driver: schemas.DriverCreate, db: Session = Depends(database.get_db)):
    return crud.create_driver(db, driver)

@router.get("/", response_model=list[schemas.DriverOut])
def list_drivers(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    return crud.get_drivers(db, skip, limit)

@router.get("/{driver_id}", response_model=schemas.DriverOut)
def get_driver(driver_id: int, db: Session = Depends(database.get_db)):
    driver = crud.get_driver(db, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")
    return driver

@router.put("/{driver_id}", response_model=schemas.DriverOut)
def update_driver(driver_id: int, driver: schemas.DriverCreate, db: Session = Depends(database.get_db)):
    db_driver = crud.get_driver(db, driver_id)
    if not db_driver:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")
    db_driver.nombre = driver.nombre
    db_driver.licencia = driver.licencia
    db.commit()
    db.refresh(db_driver)
    return db_driver

@router.delete("/{driver_id}")
def delete_driver(driver_id: int, db: Session = Depends(database.get_db)):
    driver = crud.soft_delete_driver(db, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")
    return {"detail": "Conductor desactivado"}
