from datetime import date, time
from typing import Optional

from sqlmodel import Column, Field, ForeignKey, Integer, SQLModel


class Timeslots(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    doctor_id: int = Field(
        sa_column=Column(Integer, ForeignKey("doctors.id", ondelete="CASCADE"))
    )
    hospital_id: int = Field(
        sa_column=Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"))
    )
    date: date
    time: time
    is_available: bool = Field(default=True)
