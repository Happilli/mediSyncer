from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlmodel import Session

from database import get_session
from models.doctors import Doctors
from models.hospitals import Hospitals
from models.users import Users
from schemas.doctor import (
    DoctorOut,
    DoctorProfileOut,
    DoctorRegister,
    DoctorSecurityAnswerUpdate,
    DoctorUpdate,
    TimeSlotCreate,
    TimeSlotOut,
)
from services.doctor_service import (
    create_timeslot,
    get_doctor,
    get_my_profile,
    list_doctor_timeslots,
    list_doctors,
    list_doctors_for_own_hospital,
    register_doctor,
    update_doctor_profile,
    update_doctor_profile_pic,
    update_doctor_security_answer,
)
from utils.dependencies import (
    get_current_user,
    get_own_doctor_profile,
    get_own_hospital_profile,
    require_hospital,
    required_verified_doctor,
)

router = APIRouter(prefix="/doctors", tags=["doctors"])


# @router.post("/register", status_code=201)
# def register_hospital_doctor(
#     data: DoctorRegister,
#     session: Session = Depends(get_session),
#     current_hospital: Users = Depends(require_hospital),
# ):
#     return register_doctor(data, session, current_hospital)


@router.post("/register", status_code=201)
async def register_hospital_doctor(
    email: str = Form(...),
    password: str = Form(...),
    name: str = Form(...),
    phone: str = Form(...),
    department: str = Form(...),
    speciality: str = Form(...),
    bio: str = Form(...),
    address: str = Form(...),
    license_number: str = Form(...),
    years_experience: int = Form(...),
    license_photo: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_hospital: Users = Depends(require_hospital),
):
    data = DoctorRegister(
        email=email,
        password=password,
        name=name,
        phone=phone,
        department=department,
        speciality=speciality,
        bio=bio,
        address=address,
        license_number=license_number,
        years_experience=years_experience,
    )
    return await register_doctor(data, license_photo, session, current_hospital)


@router.get("/", response_model=list[DoctorOut])
def get_doctors(
    hospital_id: int | None = None,
    department: str | None = None,
    speciality: str | None = None,
    search: str | None = None,
    session: Session = Depends(get_session),
):
    return list_doctors(session, hospital_id, department, speciality, search)


@router.get("/me", response_model=DoctorProfileOut)
def my_doctor_profile(
    doctor: Doctors = Depends(get_own_doctor_profile),
    session: Session = Depends(get_session),
):
    return get_my_profile(doctor, session)


@router.patch("/me", response_model=DoctorOut)
def update_my_doctor_profile(
    data: DoctorUpdate,
    session: Session = Depends(get_session),
    doctor: Doctors = Depends(get_own_doctor_profile),
):
    return update_doctor_profile(doctor, data, session)


@router.post("/me/timeslots", status_code=201, response_model=TimeSlotOut)
def add_timeslot(
    data: TimeSlotCreate,
    session: Session = Depends(get_session),
    doctor: Doctors = Depends(required_verified_doctor),
):
    return create_timeslot(data, doctor, session)


@router.get("/mine", response_model=list[DoctorOut])
def get_my_hospital_doctors(
    hospital: Hospitals = Depends(get_own_hospital_profile),
    session: Session = Depends(get_session),
):
    return list_doctors_for_own_hospital(hospital, session)


@router.get("/{doctor_id}", response_model=DoctorOut)
def get_doctor_detail(doctor_id: int, session: Session = Depends(get_session)):
    return get_doctor(doctor_id, session)


@router.get("/{doctor_id}/timeslots", response_model=list[TimeSlotOut])
def get_doctor_timeslots(
    doctor_id: int, available_only: bool = True, session: Session = Depends(get_session)
):
    return list_doctor_timeslots(doctor_id, session, available_only)


@router.patch("/me/profile-pic", response_model=DoctorOut)
async def update_my_doctor_profile_pic(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    doctor: Doctors = Depends(get_own_doctor_profile),
):
    return await update_doctor_profile_pic(doctor, file, session)


@router.patch("/me/security-answer")
def update_my_security_answer(
    data: DoctorSecurityAnswerUpdate,
    session: Session = Depends(get_session),
    doctor: Doctors = Depends(get_own_doctor_profile),
    current_user: Users = Depends(get_current_user),
):
    return update_doctor_security_answer(doctor, current_user, data, session)
