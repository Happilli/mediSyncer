from fastapi import APIRouter, Depends
from sqlmodel import Session

from database import get_session
from models.doctors import Doctors
from models.patients import Patients
from schemas.medical_history import MedicalHistoryOut
from services.medical_history_service import (
    list_my_history,
    list_patient_history_for_doctor,
)
from utils.dependencies import required_verified_doctor, required_verified_patient

router = APIRouter(prefix="/medical-history", tags=["medical-history"])


@router.get("/me", response_model=list[MedicalHistoryOut])
def my_medical_history(
    session: Session = Depends(get_session),
    patient: Patients = Depends(required_verified_patient),
):
    return list_my_history(patient, session)


@router.get("/patient/{patient_id}", response_model=list[MedicalHistoryOut])
def patient_medical_history_for_doctor(
    patient_id: int,
    session: Session = Depends(get_session),
    doctor: Doctors = Depends(required_verified_doctor),
):
    return list_patient_history_for_doctor(patient_id, doctor, session)
