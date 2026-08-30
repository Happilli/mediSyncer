from datetime import time
from typing import Optional

from sqlmodel import Column, Field, ForeignKey, Integer, SQLModel


class MedicationTimes(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    medication_id: int = Field(
        sa_column=Column(Integer, ForeignKey("medications.id", ondelete="CASCADE"))
    )
    dosage_time: time
    label: Optional[str] = Field(default=None)
