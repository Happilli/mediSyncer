from datetime import date as dihh
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
    instruction: str
    duration_days: int = Field(ge=1)
    start_date: Optional[dihh] = Field(default=None)
