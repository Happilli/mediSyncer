from typing import Optional
from sqlmodel import Field, SQLModel


class Hospitals(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id : int = Field(foreign_key="users.id")
    name: str 
    address: str
    phone: str
    website: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    image_url: Optional[str] = Field(default=None)
    is_active: bool = Field(default=False)
    registration_number: str
