from datetime import date, datetime, time

from pydantic import BaseModel, field_validator

from models.prescriptions import DispenseStatus


class MedicationTimeCreate(BaseModel):
    dosage_time: time
    label: str | None = None


class MedicationCreate(BaseModel):
    name: str
    dosage: str
    instruction: str
    duration_days: int
    dosage_times: list[MedicationTimeCreate]

    @field_validator("dosage_times")
    @classmethod
    def at_least_one_time(cls, v):
        if not v:
            raise ValueError("At least one dosage time is required")
        return v



class MedicationOut(BaseModel):
    schedule_id: int
    medication_id: int
    prescription_id: int
    patient_id: int
    name: str
    dosage: str
    instruction: str
    dosage_time: time
    label: str | None = None
    frequency_per_day: int
    duration_days: int
    start_date: date | None = None
    end_date: date | None = None
    is_taken: bool
    taken_at: datetime | None = None
    is_active: bool
    doctor_id: int
    doctor_name: str
    dispense_status: str | None = None

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
    hospital_id: int
    diagnosis: str
    instructions: str
    dispense_status: DispenseStatus
    created_at: datetime
    follow_up_date: datetime | None = None

    class Config:
        from_attributes = True


class PrescriptionDetailOut(PrescriptionOut):
    medications: list[MedicationOut] = []


class DispenseQueueItemOut(BaseModel):
    prescription_id: int
    patient_name: str
    medicine_names: list[str]
    created_at: datetime
