from pydantic import BaseModel, Field
from typing import Optional


class AppointmentCreate(BaseModel):
    patient_name: str = Field(min_length=1, max_length=120)
    doctor_name: str = Field(default="General", max_length=120)
    reason: str = Field(default="", max_length=1000)
    status: str = Field(default="scheduled")
    priority: str = Field(default="medium")
    scheduled_for: Optional[str] = None


class AppointmentUpdate(BaseModel):
    patient_name: Optional[str] = Field(default=None, max_length=120)
    doctor_name: Optional[str] = Field(default=None, max_length=120)
    reason: Optional[str] = Field(default=None, max_length=1000)
    status: Optional[str] = None
    priority: Optional[str] = None
    scheduled_for: Optional[str] = None


class AppointmentOut(AppointmentCreate):
    id: int

    class Config:
        from_attributes = True
