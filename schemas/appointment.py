from datetime import datetime
from typing import Optional

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


class AppointmentPatientOut(BaseModel):
    id: int
    name: str
    phone: str


class AppointmentDoctorOut(BaseModel):
    id: int
    name: str
    department: str
    speciality: str


class HospitalAppointmentOut(BaseModel):
    id: int
    patient: AppointmentPatientOut
    doctor: AppointmentDoctorOut
    hospital_id: int
    appointment_at: datetime
    status: AppointmentStatus
    notes: Optional[str] = None
