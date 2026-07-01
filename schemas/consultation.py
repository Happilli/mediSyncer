from datetime import datetime

from pydantic import BaseModel


class ConsultationCreate(BaseModel):
    appointment_id: int
    complaint: str
    symptoms: str
    diagnosis: str
    notes: str | None = None
    blood_pressure: str | None = None
    heart_rate: str | None = None
    temperature: str | None = None
    weight: str | None = None


class ConsultationOut(BaseModel):
    id: int
    appointment_id: int
    doctor_id: int
    hospital_id: int
    complaint: str
    symptoms: str
    diagnosis: str
    notes: str | None = None
    blood_pressure: str | None = None
    heart_rate: str | None = None
    temperature: str | None = None
    weight: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True
