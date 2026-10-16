from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from .database import get_db
from . import models, schemas

router = APIRouter(prefix="/api/appointments", tags=["appointments"])

ALLOWED_STATUS = {"scheduled", "checked-in", "completed", "cancelled"}
ALLOWED_PRIORITY = {"low", "medium", "high", "urgent"}


@router.get("", response_model=list[schemas.AppointmentOut])
def list_appointments(status: str | None = None, db: Session = Depends(get_db)):
    q = db.query(models.Appointment).order_by(models.Appointment.id.desc())
    if status:
        q = q.filter(models.Appointment.status == status)
    return q.all()


@router.get("/stats")
def appointment_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(models.Appointment.id)).scalar() or 0
    by_status = dict(
        db.query(models.Appointment.status, func.count(models.Appointment.id))
        .group_by(models.Appointment.status)
        .all()
    )
    urgent = (
        db.query(func.count(models.Appointment.id))
        .filter(models.Appointment.priority == "urgent")
        .scalar()
        or 0
    )
    return {"total": total, "by_status": by_status, "urgent": urgent}


@router.get("/{appt_id}", response_model=schemas.AppointmentOut)
def get_appointment(appt_id: int, db: Session = Depends(get_db)):
    obj = db.get(models.Appointment, appt_id)
    if not obj:
        raise HTTPException(status_code=404, detail="appointment not found")
    return obj


@router.post("", response_model=schemas.AppointmentOut, status_code=201)
def create_appointment(payload: schemas.AppointmentCreate, db: Session = Depends(get_db)):
    if payload.status not in ALLOWED_STATUS:
        raise HTTPException(status_code=422, detail=f"invalid status: {payload.status}")
    if payload.priority not in ALLOWED_PRIORITY:
        raise HTTPException(status_code=422, detail=f"invalid priority: {payload.priority}")
    obj = models.Appointment(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/{appt_id}", response_model=schemas.AppointmentOut)
def update_appointment(appt_id: int, payload: schemas.AppointmentUpdate, db: Session = Depends(get_db)):
    obj = db.get(models.Appointment, appt_id)
    if not obj:
        raise HTTPException(status_code=404, detail="appointment not found")
    data = payload.model_dump(exclude_unset=True)
    if "status" in data and data["status"] not in ALLOWED_STATUS:
        raise HTTPException(status_code=422, detail=f"invalid status: {data['status']}")
    if "priority" in data and data["priority"] not in ALLOWED_PRIORITY:
        raise HTTPException(status_code=422, detail=f"invalid priority: {data['priority']}")
    for k, v in data.items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{appt_id}", status_code=204)
def delete_appointment(appt_id: int, db: Session = Depends(get_db)):
    obj = db.get(models.Appointment, appt_id)
    if not obj:
        raise HTTPException(status_code=404, detail="appointment not found")
    db.delete(obj)
    db.commit()
    return None
