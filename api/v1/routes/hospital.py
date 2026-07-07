from fastapi import APIRouter, Depends, File, UploadFile
from sqlmodel import Session

from database import get_session
from models.hospitals import Hospitals
from models.users import Users
from schemas.doctor import DoctorAdminOut, DoctorListItemOut
from schemas.hospital import (
    HospitalDashboardOut,
    HospitalOut,
    HospitalRegister,
    HospitalUpdate,
)
from services.doctor_service import (
    get_doctor_admin,
    list_all_doctors_by_hospital,
    verify_doctor,
)
from services.hospital_service import (
    delete_hospital,
    get_hospital,
    get_hospital_dashboard,
    list_hospitals,
    register_hospital,
    update_hospital_image,
    update_hospital_profile,
)
from utils.dependencies import get_own_hospital_profile, require_admin

router = APIRouter(prefix="/hospitals", tags=["hospitals"])


@router.post("/register", status_code=201)
def register_new_hospital(
    data: HospitalRegister,
    session: Session = Depends(get_session),
    _: None = Depends(require_admin),
):
    return register_hospital(data, session)


@router.delete("/{hospital_id}")
def delete_hospital_route(
    hospital_id: int,
    session: Session = Depends(get_session),
    _: Users = Depends(require_admin),
):
    return delete_hospital(hospital_id, session)


@router.get("/{hospital_id}/doctors", response_model=list[DoctorListItemOut])
def get_all_doctors_for_hospital(
    hospital_id: int,
    session: Session = Depends(get_session),
    _: Users = Depends(require_admin),
):
    return list_all_doctors_by_hospital(hospital_id, session)


@router.get("/{hospital_id}/doctors/{doctor_id}", response_model=DoctorAdminOut)
def get_doctor_detail_for_hospital(
    hospital_id: int,
    doctor_id: int,
    session: Session = Depends(get_session),
    _: Users = Depends(require_admin),
):
    return get_doctor_admin(hospital_id, doctor_id, session)


@router.patch("/{hospital_id}/doctors/{doctor_id}/verify", status_code=200)
def verify_doctor_for_hospital(
    hospital_id: int,
    doctor_id: int,
    session: Session = Depends(get_session),
    _: Users = Depends(require_admin),
):
    return verify_doctor(hospital_id, doctor_id, session)


@router.get("/me", response_model=HospitalDashboardOut)
def my_hospital_profile(
    hospital: Hospitals = Depends(get_own_hospital_profile),
    session: Session = Depends(get_session),
):
    return get_hospital_dashboard(hospital, session)


@router.patch("/me", response_model=HospitalOut)
def update_my_hospital_profile(
    data: HospitalUpdate,
    session: Session = Depends(get_session),
    hospital: Hospitals = Depends(get_own_hospital_profile),
):
    return update_hospital_profile(hospital, data, session)


@router.patch("/me/image", response_model=HospitalOut)
async def update_my_hospital_image(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    hospital: Hospitals = Depends(get_own_hospital_profile),
):
    return await update_hospital_image(hospital, file, session)


@router.get("/", response_model=list[HospitalOut])
def get_hospitals(search: str | None = None, session: Session = Depends(get_session)):
    return list_hospitals(session, search)


@router.get("/{hospital_id}", response_model=HospitalOut)
def get_hospital_detail(hospital_id: int, session: Session = Depends(get_session)):
    return get_hospital(hospital_id, session)
