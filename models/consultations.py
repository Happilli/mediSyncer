from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Column, DateTime, Field, ForeignKey, Integer, SQLModel, func


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
    diagnosis: str
    notes: Optional[str] = Field(default=None)
    blood_pressure: Optional[str] = Field(default=None)
    heart_rate: Optional[str] = Field(default=None)
    temperature: Optional[str] = Field(default=None)
    weight: Optional[str] = Field(default=None)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
