from datetime import datetime
from typing import Optional

from sqlmodel import Column, Field, ForeignKey, Integer, SQLModel


class Consultations(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    appointment_id: int = Field(
        sa_column=Column(Integer, ForeignKey("appointments.id", ondelete="CASCADE"))
    )
    doctor_id: int = Field(
        sa_column=Column(Integer, ForeignKey("doctors.id", ondelete="CASCADE"))
    )
    hospital_id: int = Field(
        sa_column=Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"))
    )
    complaint: str
    symptoms: str
    diagonosis: str
    notes: Optional[str] = Field(default=None)
    blood_pressure: Optional[str] = Field(default=None)
    heart_rate: Optional[str] = Field(default=None)
    temperature: Optional[str] = Field(default=None)
    weight: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now)
