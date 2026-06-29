from fastapi import APIRouter, Depends
from sqlmodel import Session

from database import get_session
from schemas.auth import LoginRequest
from schemas.patient import PatientRegister
from services.auth_service import login_user, register_patient

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register/patient")
def patient_register(data: PatientRegister, session: Session = Depends(get_session)):
    return register_patient(data, session)


@router.post("/login")
def login(data: LoginRequest, session: Session = Depends(get_session)):
    return login_user(data.email, data.password, session)
