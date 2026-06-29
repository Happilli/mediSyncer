from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime
from sqlmodel import Column, Field, ForeignKey, Integer, SQLModel, func


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
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    follow_up_date: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
