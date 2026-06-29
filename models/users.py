from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlmodel import Column, DateTime, Field, SQLModel, func


class UserRole(str, Enum):
    patient = "patient"
    doctor = "doctor"
    hospital = "hospital"
    admin = "admin"


class Users(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    password_hash: str = Field(exclude=True)  # stores hash here
    role: UserRole
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
        ),
    )
