from fastapi import APIRouter, Depends
from sqlmodel import Session

from database import get_session
from models.users import Users
from schemas.doctor import DoctorOut, DoctorRegister
from services.doctor_service import (
    get_doctor,
    list_doctors,
    list_unverified_doctors,
    register_doctor,
    verify_doctor,
)
from utils.dependencies import require_admin, require_hospital

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.post("/register", status_code=201)
def register_hospital_doctor(
    data: DoctorRegister,
    session: Session = Depends(get_session),
    current_hospital: Users = Depends(require_hospital),
):
    return register_doctor(data, session, current_hospital)


@router.get("/", response_model=list[DoctorOut])
def get_doctors(
    hospital_id: int | None = None,
    department: str | None = None,
    speciality: str | None = None,
    search: str | None = None,
    session: Session = Depends(get_session),
):
    return list_doctors(session, hospital_id, department, speciality, search)


@router.get("/{doctor_id}", response_model=DoctorOut)
def get_doctor_detail(doctor_id: int, session: Session = Depends(get_session)):
    return get_doctor(doctor_id, session)


@router.get("/pending", response_model=list[DoctorOut])
def get_pending_doctors(
    session: Session = Depends(get_session), _: Users = Depends(require_admin)
):
    return list_unverified_doctors(session)


@router.patch("/{doctor_id}/verify")
def verify_doctor_route(
    doctor_id: int,
    session: Session = Depends(get_session),
    _: Users = Depends(require_admin),
):
    return verify_doctor(doctor_id, session)
