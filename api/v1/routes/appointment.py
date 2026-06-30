from fastapi import APIRouter, Depends
from sqlmodel import Session

from database import get_session
from models.appointments import AppointmentStatus
from models.doctors import Doctors
from models.patients import Patients
from models.users import Users
from schemas.appointment import (
    AppointmentCreate,
    AppointmentOut,
    AppointmentStatusUpdate,
)
from services.appointment_service import (
    book_appointment,
    get_appointments,
    list_my_appointment,
    update_appointment_status,
)
from utils.dependencies import (
    get_current_user,
    required_verified_doctor,
    required_verified_patient,
)

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("/", status_code=201, response_model=AppointmentOut)
def create_appointment(
    data: AppointmentCreate,
    session: Session = Depends(get_session),
    patient: Patients = Depends(required_verified_patient),
):
    return book_appointment(data, patient, session)


@router.get("/me", response_model=list[AppointmentOut])
def my_appointments_as_patient(
    session: Session = Depends(get_session),
    patient: Patients = Depends(required_verified_patient),
):
    return list_my_appointment(session, patient_id=patient.id, doctor_id=None)


@router.get("/me/doctor", response_model=list[AppointmentOut])
def my_appointments_as_doctor(
    session: Session = Depends(get_session),
    doctor: Doctors = Depends(required_verified_doctor),
):
    return list_my_appointment(session, patient_id=None, doctor_id=doctor.id)


@router.get("/{appointment_id}", response_model=AppointmentOut)
def get_appointment_detail(
    appointment_id: int,
    session: Session = Depends(get_session),
    current_user: Users = Depends(get_current_user),
):
    return get_appointments(
        appointment_id, session, current_user.id, current_user.role.value
    )


@router.patch("/{appointment_id}/status", response_model=AppointmentOut)
def update_status_as_doctor(
    appointment_id: int,
    data: AppointmentStatusUpdate,
    session: Session = Depends(get_session),
    doctor: Doctors = Depends(required_verified_doctor),
):
    return update_appointment_status(
        appointment_id, data.status, session, current_doctor=doctor
    )


@router.patch("/{appointment_id}/cancel", response_model=AppointmentOut)
def cancel_as_patient(
    appointment_id: int,
    session: Session = Depends(get_session),
    patient: Patients = Depends(required_verified_patient),
):
    return update_appointment_status(
        appointment_id, AppointmentStatus.cancelled, session, current_patient=patient
    )
