from datetime import datetime
from typing import Optional

from sqlmodel import Column, DateTime, Field, ForeignKey, Integer, SQLModel, func


class Appointments(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    doctor_id: int = Field(
        sa_column=Column(Integer, ForeignKey("doctors.id", ondelete="CASCADE"))
    )
    patient_id: int = Field(
        sa_column=Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"))
    )
    hospital_id: int = Field(
        sa_column=Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"))
    )
    appointment_at: datetime

    status: str = Field(default="pending")
    notes: Optional[str] = Field(default=None)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
