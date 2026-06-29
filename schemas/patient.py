from datetime import date

from pydantic import BaseModel, EmailStr, field_validator


class PatientRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: str
    address: str
    date_of_birth: date
    gender: str
    blood_group: str
    emergency_contact: str

    @field_validator("gender")
    def normalize_gender(cls, v):
        return v.lower()

    @field_validator("blood_group")
    def normalize_blood_group(cls, v):
        return v.lower()
