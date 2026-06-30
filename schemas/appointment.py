from datetime import datetime

from pydantic import BaseModel

from models.appointments import AppointmentStatus


class AppointmentCreate(BaseModel):
    timeslot_id: int
    notes: str | None = None


class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus


class AppointmentOut(BaseModel):
    id: int
    doctor_id: int
    patient_id: int
    hospital_id: int
    appointment_at: datetime
    status: AppointmentStatus
    notes: str | None = None

    class Config:
        from_attributes = True
