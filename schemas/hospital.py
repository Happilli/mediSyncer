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
