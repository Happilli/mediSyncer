from datetime import datetime, time
from typing import Optional

from sqlmodel import Column, Field, ForeignKey, Integer, SQLModel


class Medications(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    prescription_id: int = Field(
        sa_column=Column(Integer, ForeignKey("prescriptions.id", ondelete="CASCADE"))
    )
    patient_id: int = Field(
        sa_column=Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"))
    )
    name: str
    dosage: str
    dosage_time: time
    instruction: str
    frequency_per_day: int = Field(ge=1, le=6)
    duration_days: int = Field(ge=1)
    is_taken: bool = Field(default=False)
    taken_at: datetime | None = None
