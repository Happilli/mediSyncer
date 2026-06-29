from typing import Optional

from sqlmodel import Column, Field, ForeignKey, Integer, SQLModel


class Patients(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(
        sa_column=Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    )
    name: str
    phone: str
    address: str
    date_of_birth: str
    gender: str
    blood_group: str
    emergency_contact: str
    profile_pic_url: Optional[str] = Field(default=None)
