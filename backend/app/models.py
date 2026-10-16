from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from .database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String(120), nullable=False, index=True)
    doctor_name = Column(String(120), nullable=False, default="General")
    reason = Column(Text, nullable=False, default="")
    status = Column(String(20), nullable=False, default="scheduled")  # scheduled|checked-in|completed|cancelled
    priority = Column(String(10), nullable=False, default="medium")  # low|medium|high|urgent
    scheduled_for = Column(String(30), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
