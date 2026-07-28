from fastapi import APIRouter, Depends
from sqlmodel import Session

from database import get_session
from models.users import Users
from schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordCheckOut,
    ForgotPasswordCheckRequest,
    ForgotPasswordVerifyRequest,
    LoginRequest,
)
from schemas.patient import PatientRegister
from services.auth_service import (
    change_password,
    forgot_password_check,
    forgot_password_verify,
    login_user,
    register_patient,
)
from utils.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register/patient")
def patient_register(data: PatientRegister, session: Session = Depends(get_session)):
    return register_patient(data, session)


@router.post("/login")
def login(data: LoginRequest, session: Session = Depends(get_session)):
    return login_user(data.email, data.password, session)


@router.post("/forgot-password/check", response_model=ForgotPasswordCheckOut)
def check_forgot_password(
    data: ForgotPasswordCheckRequest, session: Session = Depends(get_session)
):
    return forgot_password_check(data.email, session)


@router.post("/forgot-password/verify")
def verify_forgot_password(
    data: ForgotPasswordVerifyRequest, session: Session = Depends(get_session)
):
    return forgot_password_verify(
        data.email, data.security_answer, data.new_password, session
    )


@router.post("/change-password")
def change_my_password(
    data: ChangePasswordRequest,
    session: Session = Depends(get_session),
    current_user: Users = Depends(get_current_user),
):
    return change_password(
        data.current_password, data.new_password, current_user, session
    )
