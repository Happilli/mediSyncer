from datetime import date, datetime, time
from typing import Optional

from sqlmodel import Column, Field, ForeignKey, Integer, SQLModel


class Appointments(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    doctor_id: int = Field(
        sa_column=Column(Integer, ForeignKey("doctors.id", ondelete="CASCADE"))
    )
    patient_id: int = Field(
        sa_column=Column(Integer, ForeignKey("doctors.id", ondelete="CASCADE"))
    )
    hospital_id: int = Field(
        sa_column=Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"))
    )
    date: date
    time: time
    status: str = Field(default="pending")
    notes: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now)
