from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordCheckRequest(BaseModel):
    email: EmailStr


class ForgotPasswordCheckOut(BaseModel):
    question: str


class ForgotPasswordVerifyRequest(BaseModel):
    email: EmailStr
    security_answer: str
    new_password: str
