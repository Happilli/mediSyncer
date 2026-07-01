from datetime import date

from pydantic import BaseModel, EmailStr, field_validator

from models.patients import BloodGroup, Gender


class PatientRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: str
    address: str
    date_of_birth: date
    gender: Gender
    blood_group: BloodGroup
    emergency_contact: str

    @field_validator("gender", mode="before")
    @classmethod
    def normalize_gender(cls, v):
        if isinstance(v, str):
            return v.strip().lower()
        return v

    @field_validator("blood_group", mode="before")
    @classmethod
    def normalize_blood_group(cls, v):
        if isinstance(v, str):
            return v.strip().upper()
        return v


class PatientOut(BaseModel):
    id: int
    name: str
    phone: str
    address: str
    date_of_birth: date
    gender: Gender
    blood_group: BloodGroup
    emergency_contact: str
    citizenship_number: str | None = None
    citizenship_photo_url: str | None = None
    is_verified: bool

    class Config:
        from_attributes = True


class PatientUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    address: str | None = None
    emergency_contact: str | None = None
    profile_pic_url: str | None = None
    citizenship_number: str | None = None
    citizenship_photo_url: str | None = None


class PatientPublicOut(BaseModel):
    id: int
    name: str
    phone: str
    gender: Gender
    blood_group: BloodGroup
    emergency_contact: str
    profile_pic_url: str | None = None

    class Config:
        from_attributes = True
