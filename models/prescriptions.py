from datetime import datetime
from typing import Optional

from sqlmodel import Column, Field, ForeignKey, Integer, SQLModel


class Prescriptions(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    doctor_id: int = Field(
        sa_column=Column(Integer, ForeignKey("doctors.id", ondelete="CASCADE"))
    )
    appointment_id: int = Field(
        sa_column=Column(Integer, ForeignKey("appointments.id", ondelete="CASCADE"))
    )
    patient_id: int = Field(
        sa_column=Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"))
    )

    diagnosis: str
    instructions: str
    created_at: datetime = Field(default_factory=datetime.now)
    follow_up_date: datetime = Field(default_factory=datetime.now)
