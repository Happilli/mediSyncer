from datetime import datetime, timezone

from pydantic import BaseModel, EmailStr, field_validator


class DoctorRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: str
    department: str
    speciality: str
    security_answer: str | None = None
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

    @field_validator("appointment_at")
    @classmethod
    def must_be_future(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        if v <= datetime.now(timezone.utc):
            raise ValueError("appointment_at must be in the future")
        return v


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
    years_experience: int | None = None

class DoctorAdminUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    department: str | None = None
    speciality: str | None = None
    bio: str | None = None
    address: str | None = None
    years_experience: int | None = None


class DoctorAdminOut(DoctorOut):
    license_number: str | None = None
    license_photo_url: str | None = None


class DoctorProfileOut(DoctorOut):
    patients_this_month: int
    total_patients: int
    has_security_answer: bool = False


class DoctorListItemOut(BaseModel):
    id: int
    name: str
    is_verified: bool
    profile_pic_url: str | None = None

    class Config:
        from_attributes = True


class DoctorSecurityAnswerUpdate(BaseModel):
    current_password: str
    security_answer: str
