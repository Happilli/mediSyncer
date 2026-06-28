from typing import Optional

from sqlmodel import Field, SQLModel


class Doctors(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    name: str
    phone: str
    department: str
    speciality: str
    bio: Optional[str] = Field(default=None)
    address: str
    years_experience: Optional[int] = Field(default=None)
    license_number: str
    profile_pic_url: Optional[str] = Field(default=None)

