from pydantic import BaseModel, EmailStr


class DoctorRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: str
    department: str
    speciality: str
    bio: str
    address: str
    license_number: str
    license_photo_url: str
    years_experience: int


class DoctorOut(BaseModel):
    id: int
    hospital_id: int
    name: str
    phone: str
    department: str
    speciality: str
    bio: str | None = None
    address: str
    years_experience: int | None = None
    is_verified: bool
    profile_pic_url: str | None = None

    class Config:
        from_attributes = True
