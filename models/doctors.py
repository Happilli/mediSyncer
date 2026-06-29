from typing import Optional

from sqlmodel import Column, Field, ForeignKey, Integer, SQLModel


class Doctors(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(
        sa_column=Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    )
    hospital_id: int = Field(
        sa_column=Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"))
    )
    name: str
    phone: str
    department: str
    speciality: str
    bio: Optional[str] = Field(default=None)
    address: str
    years_experience: Optional[int] = Field(default=None)
    license_number: Optional[str] = Field(default=None)
    license_photo_url: Optional[str] = Field(default=None)
    is_verified: bool = Field(default=False)
    profile_pic_url: Optional[str] = Field(default=None)
