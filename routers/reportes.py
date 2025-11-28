from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import csv, io
from .. import database, models
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.get("/viajes")
def report_viajes(db: Session = Depends(database.get_db)):
    trips = db.query(models.Trip).filter(models.Trip.activo==True).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['id', 'usuario_id', 'conductor_id', 'origen', 'destino', 'estado', 'created_at'])
    for t in trips:
        writer.writerow([t.id, t.usuario_id, t.conductor_id, t.origen, t.destino, t.estado, t.created_at])
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type='text/csv', headers={"Content-Disposition":"attachment; filename=report_viajes.csv"})
