from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlmodel import Session

from database import get_session
from models.doctors import Doctors
from models.patients import Patients
from models.users import Users
from schemas.patient import (
    PatientListItemOut,
    PatientOut,
    PatientPublicOut,
    PatientSecurityAnswerUpdate,
    PatientUpdate,
)
from services.patient_service import (
    delete_patient,
    get_patient_admin,
    get_patient_for_doctor,
    list_all_my_patients,
    list_all_patients,
    list_treated_patients,
    patient_to_out,
    request_patient_verification,
    update_patient_profile,
    update_patient_profile_pic,
    update_patient_security_answer,
    verify_patient,
)
from utils.dependencies import (
    get_current_user,
    get_own_patient_profile,
    require_admin,
    required_verified_doctor,
)

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("/me", response_model=PatientOut)
def my_patient_profile(patient: Patients = Depends(get_own_patient_profile)):
    return patient_to_out(patient)


@router.patch("/me", response_model=PatientOut)
def update_my_patient_profile(
    data: PatientUpdate,
    session: Session = Depends(get_session),
    patient: Patients = Depends(get_own_patient_profile),
):
    return update_patient_profile(patient, data, session)


@router.get("/", response_model=list[PatientListItemOut])
def get_all_patients(
    session: Session = Depends(get_session), _: Users = Depends(require_admin)
):
    return list_all_patients(session)


@router.post("/{patient_id}/verify", status_code=200)
def verify_patient_route(
    patient_id: int,
    session: Session = Depends(get_session),
    _: Users = Depends(require_admin),
):
    return verify_patient(patient_id, session)


@router.get("/doctor", response_model=list[PatientPublicOut])
def my_doctor_patients(
    session: Session = Depends(get_session),
    doctor: Doctors = Depends(required_verified_doctor),
):
    if doctor.id is None:
        raise HTTPException(status_code=500, detail="Doctor id missing")
    return list_all_my_patients(doctor.id, session)


@router.get("/doctor/{patient_id}", response_model=PatientPublicOut)
def my_doctor_patient_detail(
    patient_id: int,
    session: Session = Depends(get_session),
    doctor: Doctors = Depends(required_verified_doctor),
):
    if doctor.id is None:
        raise HTTPException(status_code=500, detail="Doctor id missing")
    return get_patient_for_doctor(patient_id, doctor.id, session)


@router.get("/treated", response_model=list[PatientPublicOut])
def my_treated_patients(
    search: str | None = None,
    session: Session = Depends(get_session),
    doctor: Doctors = Depends(required_verified_doctor),
):
    if doctor.id is None:
        raise HTTPException(status_code=500, detail="Doctor id missing")
    return list_treated_patients(doctor.id, session, search)


@router.get("/{patient_id}", response_model=PatientOut)
def get_patient_detail(
    patient_id: int,
    session: Session = Depends(get_session),
    _: Users = Depends(require_admin),
):
    return get_patient_admin(patient_id, session)


@router.post("/request-verification", response_model=PatientOut)
async def request_verification(
    citizenship_number: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    patient: Patients = Depends(get_own_patient_profile),
):
    return await request_patient_verification(
        citizenship_number, file, patient, session
    )


@router.patch("/me/profile-pic", response_model=PatientOut)
async def update_my_patient_profile_pic(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    patient: Patients = Depends(get_own_patient_profile),
):
    return await update_patient_profile_pic(patient, file, session)


@router.delete("/{patient_id}")
def delete_patient_route(
    patient_id: int,
    session: Session = Depends(get_session),
    _: Users = Depends(require_admin),
):
    return delete_patient(patient_id, session)


@router.patch("/me/security-answer")
def update_my_security_answer(
    data: PatientSecurityAnswerUpdate,
    session: Session = Depends(get_session),
    patient: Patients = Depends(get_own_patient_profile),
    current_user: Users = Depends(get_current_user),
):
    return update_patient_security_answer(patient, current_user, data, session)
