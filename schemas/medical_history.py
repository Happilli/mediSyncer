from datetime import datetime

from pydantic import BaseModel


class MedicalHistoryOut(BaseModel):
    id: int
    doctor_id: int
    patient_id: int
    title: str
    description: str
    date: datetime

    class Config:
        from_attributes = True
