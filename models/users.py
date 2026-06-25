from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel

class UserRole(str, Enum):
    patient = "patient"
    doctor = "doctor"
    hospital = "hospital"
    admin = "admin"

class Users(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str  # stores hash here
    role: UserRole
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
