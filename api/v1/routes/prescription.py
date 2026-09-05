from datetime import date

from fastapi import APIRouter, Depends
from sqlmodel import Session

from database import get_session
from models.doctors import Doctors
from models.hospitals import Hospitals
from models.patients import Patients
from models.prescriptions import DispenseStatus
from models.users import Users
from schemas.prescription import (
    DispenseQueueItemOut,
    PrescriptionCreate,
    PrescriptionDetailOut,
    PrescriptionOut,
)
from services.prescription_service import (
    confirm_collection,
    create_prescription,
    get_dispense_queue,
    get_prescription_detail,
    list_my_prescriptions,
    mark_prescription_ready,
)
from utils.dependencies import (
    get_current_user,
    get_own_hospital_profile,
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
    doctor_id: int | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    session: Session = Depends(get_session),
    patient: Patients = Depends(required_verified_patient),
):
    return list_my_prescriptions(patient, session, doctor_id, from_date, to_date)


@router.get("/dispense-queue", response_model=list[DispenseQueueItemOut])
def dispense_queue(
    status: DispenseStatus = DispenseStatus.pending,
    session: Session = Depends(get_session),
    hospital: Hospitals = Depends(get_own_hospital_profile),
):
    return get_dispense_queue(hospital.id, session, status)


@router.patch("/{prescription_id}/mark-ready", response_model=PrescriptionOut)
def mark_ready(
    prescription_id: int,
    session: Session = Depends(get_session),
    hospital: Hospitals = Depends(get_own_hospital_profile),
):
    return mark_prescription_ready(prescription_id, hospital.id, session)


@router.patch("/{prescription_id}/collect", response_model=PrescriptionOut)
def collect(
    prescription_id: int,
    session: Session = Depends(get_session),
    hospital: Hospitals = Depends(get_own_hospital_profile),
):
    return confirm_collection(prescription_id, hospital, session)


@router.get("/{prescription_id}", response_model=PrescriptionDetailOut)
def get_prescription(
    prescription_id: int,
    session: Session = Depends(get_session),
    current_user: Users = Depends(get_current_user),
):
    return get_prescription_detail(
        prescription_id, session, current_user.id, current_user.role.value
    )
