from fastapi import APIRouter, Depends
from sqlmodel import Session

from database import get_session
from models.patients import Patients
from models.users import Users
from schemas.patient import PatientOut, PatientUpdate
from services.patient_service import (
    list_unverified_patients,
    update_patient_profile,
    verify_patient,
)
from utils.dependencies import get_own_patient_profile, require_admin

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("/me", response_model=PatientOut)
def my_patient_profile(patient: Patients = Depends(get_own_patient_profile)):
    return patient


@router.patch("/me", response_model=PatientOut)
def update_my_patient_profile(
    data: PatientUpdate,
    session: Session = Depends(get_session),
    patient: Patients = Depends(get_own_patient_profile),
):
    return update_patient_profile(patient, data, session)


@router.get("/pending", status_code=201, response_model=list[PatientOut])
def get_pending_patients(
    session: Session = Depends(get_session), _: Users = Depends(require_admin)
):
    return list_unverified_patients(session)


@router.post("/{patient_id}/verify", status_code=201)
def verify_patient_route(
    patient_id: int,
    session: Session = Depends(get_session),
    _: Users = Depends(require_admin),
):
    return verify_patient(patient_id, session)
