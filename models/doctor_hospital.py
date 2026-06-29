from typing import Optional

from sqlmodel import Column, Field, ForeignKey, Integer, SQLModel


class Doctor_Hospital(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hospital_id: int = Field(
        sa_column=Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"))
    )
    doctor_id: int = Field(
        sa_column=Column(Integer, ForeignKey("doctors.id", ondelete="CASCADE"))
    )
