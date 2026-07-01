from datetime import datetime, time

from pydantic import BaseModel


class MedicationCreate(BaseModel):
    name: str
    dosage: str
    dosage_time: time
    instruction: str
    frequency_per_day: int
    duration_days: int


class MedicationOut(BaseModel):
    id: int
    prescription_id: int
    patient_id: int
    name: str
    dosage: str
    dosage_time: time
    instruction: str
    frequency_per_day: int
    duration_days: int
    is_taken: bool
    taken_at: datetime | None = None

    class Config:
        from_attributes = True


class PrescriptionCreate(BaseModel):
    appointment_id: int
    diagnosis: str
    instructions: str
    follow_up_date: datetime | None = None
    medications: list[MedicationCreate] = []


class PrescriptionOut(BaseModel):
    id: int
    doctor_id: int
    appointment_id: int
    patient_id: int
    diagnosis: str
    instructions: str
    created_at: datetime
    follow_up_date: datetime

    class Config:
        from_attributes = True


class PrescriptionDetailOut(PrescriptionOut):
    medications: list[MedicationOut] = []
