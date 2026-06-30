from fastapi import APIRouter, Depends
from sqlmodel import Session

from database import get_session
from models.users import Users
from schemas.patient import PatientOut
from services.patient_service import (
    list_unverified_patients,
    verify_patient,
)
from utils.dependencies import require_admin

router = APIRouter(prefix="/patients", tags=["patients"])


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
