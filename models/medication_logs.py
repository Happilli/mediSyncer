from datetime import date as date_type
from datetime import datetime
from typing import Optional

from sqlmodel import (
    Column,
    Date,
    DateTime,
    Field,
    ForeignKey,
    Integer,
    SQLModel,
    UniqueConstraint,
    column,
)


class MedicationLogs(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("medication_id", "log_date", name="uq_medication_log_date)"),
    )
    id: Optional[int] = Field(default=None, primary_key=True)
    medication_id: int = Field(
        sa_column=Column(Integer, ForeignKey("medications.id", ondelete="CASCADE"))
    )
    patient_id: int = Field(
        sa_column=Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"))
    )
    log_date: date_type = Field(sa_column=Column(Date, nullable=False))
    taken_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(), nullable=True)
    )
