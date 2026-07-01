from fastapi import APIRouter, Depends
from sqlmodel import Session

from database import get_session
from models.doctors import Doctors
from models.patients import Patients
from models.users import Users
from schemas.prescription import (
    PrescriptionCreate,
    PrescriptionDetailOut,
    PrescriptionOut,
)
from services.prescription_service import (
    create_prescription,
    get_prescription_detail,
    list_my_prescriptions,
)
from utils.dependencies import (
    get_current_user,
    required_verified_doctor,
    required_verified_patient,
)

router = APIRouter(prefix="/prescriptions", tags=["prescriptions"])


@router.post("/", status_code=201, response_model=PrescriptionDetailOut)
def create_new_prescription(
    data: PrescriptionCreate,
    session: Session = Depends(get_session),
    doctor: Doctors = Depends(required_verified_doctor),
):
    return create_prescription(data, doctor, session)


@router.get("/me", response_model=list[PrescriptionOut])
def my_prescriptions(
    session: Session = Depends(get_session),
    patient: Patients = Depends(required_verified_patient),
):
    return list_my_prescriptions(patient, session)


@router.get("/{prescription_id}", response_model=PrescriptionDetailOut)
def get_prescription(
    prescription_id: int,
    session: Session = Depends(get_session),
    current_user: Users = Depends(get_current_user),
):
    return get_prescription_detail(
        prescription_id, session, current_user.id, current_user.role.value
    )
