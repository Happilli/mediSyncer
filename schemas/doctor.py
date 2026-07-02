from datetime import datetime

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
    license_number: str | None = None
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


class TimeSlotCreate(BaseModel):
    appointment_at: datetime


class TimeSlotOut(BaseModel):
    id: int
    doctor_id: int
    hospital_id: int
    appointment_at: datetime
    is_available: bool

    class Config:
        from_attributes = True


class DoctorUpdate(BaseModel):
    phone: str | None = None
    bio: str | None = None
    address: str | None = None
    profile_pic_url: str | None = None
    years_experience: int | None = None


class DoctorAdminOut(DoctorOut):
    license_number: str | None = None
    license_photo_url: str | None = None


class DoctorProfileOut(DoctorOut):
    patients_this_month: int
    total_patients: int
