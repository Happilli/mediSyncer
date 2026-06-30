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
