from datetime import datetime

from pydantic import BaseModel


class AppointmentCreate(BaseModel):
    timeslot_id: int
    notes: str | None = None


class AppointmentOut(BaseModel):
    id: int
    doctor_id: int
    patient_id: int
    hospital_id: int
    appointment_at: datetime
    status: str
    notes: str | None = None

    class Config:
        from_attributes = True
