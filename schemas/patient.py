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
