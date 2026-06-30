from pydantic import BaseModel, EmailStr


class HospitalRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    address: str
    phone: str
    registration_number: str
    website: str | None = None
    description: str | None = None


class HospitalOut(BaseModel):
    id: int
    name: str
    address: str
    phone: str
    website: str | None = None
    description: str | None = None
    image_url: str | None = None
    is_active: bool
    registration_number: str

    class Config:
        from_attributes = True
