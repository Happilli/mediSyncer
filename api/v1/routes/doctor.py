from fastapi import APIRouter, Depends
from sqlmodel import Session

from database import get_session
from models.users import Users
from schemas.doctor import DoctorRegister
from services.doctor_service import DoctorRegister, register_doctor
from utils.dependencies import require_hospital

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.post("/register", status_code=201)
def register_hospital_doctor(
    data: DoctorRegister,
    session: Session = Depends(get_session),
    current_hospital: Users = Depends(require_hospital),
):
    return register_doctor(data, session, current_hospital)
