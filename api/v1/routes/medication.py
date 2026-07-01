from fastapi import APIRouter, Depends
from sqlmodel import Session

from database import get_session
from models.patients import Patients
from schemas.prescription import MedicationOut
from services.medication_service import list_my_medications, mark_medication_taken
from utils.dependencies import required_verified_patient

router = APIRouter(prefix="/medications", tags=["medications"])


@router.get("/me", response_model=list[MedicationOut])
def my_medications(
    session: Session = Depends(get_session),
    patient: Patients = Depends(required_verified_patient),
):
    return list_my_medications(patient, session)


@router.patch("/{medication_id}/taken", response_model=MedicationOut)
def mark_taken(
    medication_id: int,
    session: Session = Depends(get_session),
    patient: Patients = Depends(required_verified_patient),
):
    return mark_medication_taken(medication_id, patient, session)
