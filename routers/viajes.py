from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas, database

router = APIRouter()

@router.post("/", response_model=schemas.TripOut)
def create_trip(trip: schemas.TripCreate, db: Session = Depends(database.get_db)):
    return crud.create_trip(db, trip)

@router.get("/", response_model=list[schemas.TripOut])
def list_trips(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    return crud.get_trips(db, skip, limit)

@router.get("/{trip_id}", response_model=schemas.TripOut)
def get_trip(trip_id: int, db: Session = Depends(database.get_db)):
    t = crud.get_trip(db, trip_id)
    if not t:
        raise HTTPException(status_code=404, detail='Viaje no encontrado')
    return t

@router.put("/{trip_id}", response_model=schemas.TripOut)
def update_trip(trip_id: int, data: schemas.TripUpdate, db: Session = Depends(database.get_db)):
    t = crud.update_trip(db, trip_id, data.dict(exclude_unset=True))
    if not t:
        raise HTTPException(status_code=404, detail='Viaje no encontrado')
    return t

@router.delete("/{trip_id}")
def delete_trip(trip_id: int, db: Session = Depends(database.get_db)):
    t = crud.soft_delete_trip(db, trip_id)
    if not t:
        raise HTTPException(status_code=404, detail='Viaje no encontrado')
    return {"detail": "Viaje desactivado"}

@router.patch("/{trip_id}/asignar", response_model=schemas.TripOut)
def asignar_conductor(trip_id: int, payload: dict, db: Session = Depends(database.get_db)):
    # payload expected: {"conductor_id": int}
    data = {}
    if 'conductor_id' in payload:
        data['conductor_id'] = payload['conductor_id']
        data['estado'] = 'en_curso'
    t = crud.update_trip(db, trip_id, data)
    if not t:
        raise HTTPException(status_code=404, detail='Viaje no encontrado')
    return t
