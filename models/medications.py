from typing import Optional

from sqlmodel import Column, Field, ForeignKey, Integer, SQLModel


class Medications(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    prescriptions_id: int = Field(
        sa_column=Column(Integer, ForeignKey("prescriptions.id", ondelete="CASCADE"))
    )
    patient_id: int = Field(
        sa_column=Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"))
    )
    name: str
    dosage: str
    frequency: str
    time: str
    duration: str
    is_taken: bool = Field(default=False)
