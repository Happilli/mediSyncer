from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlmodel import Column, DateTime, Field, ForeignKey, Integer, SQLModel, func


class NotificationType(str, Enum):
    appointment_booked = "appointment_booked"
    appointment_confirmed = "appointment_confirmed"
    appointment_cancelled = "appointment_cancelled"
    appointment_completed = "appointment_completed"
    doctor_registered = "doctor_registered"
    doctor_verified = "doctor_verified"
    patient_verification_requested = "patient_verification_requested"
    patient_verified = "patient_verified"
    patient_verification_rejected = "patient_verification_rejected"
    consultation_created = "consultation_created"
    prescription_created = "prescription_created"
    prescription_pending_dispense = "prescription_pending_dispense"
    prescription_ready = "prescription_ready"
    prescription_collected = "prescription_collected"
    system = "system"


class Notifications(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(
        sa_column=Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    )
    type: NotificationType
    title: str
    message: str
    related_id: Optional[int] = Field(default=None)
    related_type: Optional[str] = Field(default=None)
    is_read: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
