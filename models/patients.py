from datetime import date
from enum import Enum
from typing import Optional

from sqlmodel import Column, Field, ForeignKey, Integer, SQLModel


class Gender(str, Enum):
    male = "male"
    female = "female"
    other = "other"


class BloodGroup(str, Enum):
    a_pos = "A+"
    a_neg = "A-"
    b_pos = "B+"
    b_neg = "B-"
    ab_pos = "AB+"
    ab_neg = "AB-"
    o_pos = "O+"
    o_neg = "O-"


class Patients(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(
        sa_column=Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    )
    name: str
    phone: str
    address: str
    date_of_birth: date
    gender: Gender
    blood_group: BloodGroup
    emergency_contact: str
    profile_pic_url: Optional[str] = Field(default=None)
    citizenship_number: Optional[str] = Field(default=None)
    citizenship_photo_url: Optional[str] = Field(default=None)
    is_verified: bool = Field(default=False)
