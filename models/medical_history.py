from datetime import datetime
from typing import Optional

from sqlmodel import Column, DateTime, Field, ForeignKey, Integer, SQLModel, func


class Medical_History(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    doctor_id: int = Field(
        sa_column=Column(Integer, ForeignKey("doctors.id", ondelete="CASCADE"))
    )
    patient_id: int = Field(
        sa_column=Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"))
    )
    title: str
    description: str
    date: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
