from fastapi import APIRouter, Depends
from sqlmodel import Session

from database import get_session
from models.doctors import Doctors
from models.users import Users
from schemas.consultation import ConsultationCreate, ConsultationOut
from services.consultation_service import (
    create_consultation,
    get_consultation_by_appointment,
)
from utils.dependencies import get_current_user, required_verified_doctor

router = APIRouter(prefix="/consultations", tags=["consultations"])


@router.post("/", status_code=201, response_model=ConsultationOut)
def create_new_consultation(
    data: ConsultationCreate,
    session: Session = Depends(get_session),
    doctor: Doctors = Depends(required_verified_doctor),
):
    return create_consultation(data, doctor, session)


@router.get("/appointment/{appointment_id}", response_model=ConsultationOut)
def get_consultation_for_appointment(
    appointment_id: int,
    session: Session = Depends(get_session),
    current_user: Users = Depends(get_current_user),
):
    return get_consultation_by_appointment(
        appointment_id, session, current_user.id, current_user.role.value
    )
