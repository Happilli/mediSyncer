from fastapi import APIRouter, Depends
from sqlmodel import Session

from database import get_session
from models.patients import Patients
from schemas.appointment import AppointmentCreate, AppointmentOut
from services.appointment_service import book_appointment
from utils.dependencies import required_verified_patient

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("/", status_code=201, response_model=AppointmentOut)
def create_appointment(
    data: AppointmentCreate,
    session: Session = Depends(get_session),
    patient: Patients = Depends(required_verified_patient),
):
    return book_appointment(data, patient, session)
