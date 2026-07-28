from pydantic import BaseModel, EmailStr


class HospitalRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    address: str
    phone: str
    registration_number: str
    security_answer: str | None = None
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


class HospitalUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    phone: str | None = None
    website: str | None = None
    description: str | None = None


class HospitalSecurityAnswerUpdate(BaseModel):
    current_password: str
    security_answer: str


class HospitalDashboardOut(HospitalOut):
    total_doctors: int
    verified_doctors: int
    total_appointments: int
    has_security_answer: bool
