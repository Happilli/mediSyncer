from datetime import datetime, timezone

from annotated_types import doc
from fastapi import HTTPException, UploadFile
from sqlmodel import Session, select

from models.appointments import Appointments
from models.doctor_hospital import Doctor_Hospital
from models.doctors import Doctors
from models.hospitals import Hospitals
from models.timeslots import Timeslots
from models.users import UserRole, Users
from schemas.doctor import DoctorRegister, DoctorUpdate, TimeSlotCreate
from utils.file_storage import create_user_folder, save_verification_doc
from utils.security import hash_password


async def register_doctor(
    data: DoctorRegister,
    license_photo: UploadFile,
    session: Session,
    current_hospital: Users,
):
    existing = session.exec(select(Users).where(Users.email == data.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="email already registered")

    existing_rez = session.exec(
        select(Doctors).where(Doctors.license_number == data.license_number)
    ).first()
    if existing_rez:
        raise HTTPException(
            status_code=400, detail="Doctor license_number already taken..."
        )

    hospital = session.exec(
        select(Hospitals).where(Hospitals.user_id == current_hospital.id)
    ).first()
    if hospital is None or hospital.id is None:
        raise HTTPException(status_code=404, detail="hospital profile not found..")

    user = Users(
        email=data.email,
        password_hash=hash_password(data.password),
        role=UserRole.doctor,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    if user.id is None:
        raise HTTPException(status_code=500, detail="User ID generation failed")

    create_user_folder(user.id)
    license_photo_url = await save_verification_doc(
        license_photo, user.id, "license_photos"
    )

    doctor = Doctors(
        user_id=user.id,
        hospital_id=hospital.id,
        name=data.name,
        phone=data.phone,
        department=data.department,
        speciality=data.speciality,
        bio=data.bio,
        address=data.address,
        license_number=data.license_number,
        license_photo_url=license_photo_url,
        years_experience=data.years_experience,
    )
    session.add(doctor)
    session.commit()
    session.refresh(doctor)

    if doctor.id is None:
        raise HTTPException(status_code=500, detail="Doctor ID generation failed")

    cond = Doctor_Hospital(hospital_id=hospital.id, doctor_id=doctor.id)
    session.add(cond)
    session.commit()

    return {"message": f"{doctor.name} has been registered!"}


def list_doctors(
    session: Session,
    hospital_id: int | None = None,
    department: str | None = None,
    speciality: str | None = None,
    search: str | None = None,
):
    query = select(Doctors).where(Doctors.is_verified == True)
    if hospital_id is not None:
        query = query.where(Doctors.hospital_id == hospital_id)
    if department:
        query = query.where(Doctors.department == department)
    if speciality:
        query = query.where(Doctors.speciality == speciality)
    if search:
        query = query.where(Doctors.name.like(f"%{search}%"))
    return session.exec(query).all()


def get_doctor(doctor_id: int, session: Session):
    doctor = session.exec(
        select(Doctors).where(Doctors.id == doctor_id, Doctors.is_verified == True)
    ).first()
    if doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found..")
    return doctor


def list_unverified_doctors(session: Session):
    return session.exec(select(Doctors).where(Doctors.is_verified == False)).all()


def verify_doctor(doctor_id: int, session: Session):
    doctor = session.get(Doctors, doctor_id)
    if doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found")
    doctor.is_verified = True
    session.add(doctor)
    session.commit()
    session.refresh(doctor)
    return {"message": f"{doctor.name} has been verified!"}


def create_timeslot(data: TimeSlotCreate, doctor: Doctors, session: Session):
    existing = session.exec(
        select(Timeslots).where(
            Timeslots.doctor_id == doctor.id,
            Timeslots.appointment_at == data.appointment_at,
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=400, detail="Timeslot already exists for this time"
        )

    if doctor.id is None:
        raise HTTPException(status_code=500, detail="Doctor id cant be generated")

    slot = Timeslots(
        doctor_id=doctor.id,
        hospital_id=doctor.hospital_id,
        appointment_at=data.appointment_at,
        is_available=True,
    )
    session.add(slot)
    session.commit()
    session.refresh(slot)

    return slot


def list_doctor_timeslots(
    doctor_id: int, session: Session, available_only: bool = True
):
    query = select(Timeslots).where(Timeslots.doctor_id == doctor_id)

    if available_only:
        query = query.where(Timeslots.is_available == True)

    query = query.order_by(Timeslots.appointment_at)
    return session.exec(query).all()


def get_my_profile(doctor: Doctors, session: Session):
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    total_patients = session.exec(
        select(Appointments.patient_id)
        .where(Appointments.doctor_id == doctor.id)
        .distinct()
    ).all()

    patients_this_month = session.exec(
        select(Appointments.patient_id)
        .where(
            Appointments.doctor_id == doctor.id,
            Appointments.appointment_at >= month_start,
        )
        .distinct()
    ).all()

    return {
        **doctor.model_dump(),
        "patients_this_month": len(patients_this_month),
        "total_patients": len(total_patients),
    }


def update_doctor_profile(doctor: Doctors, data: DoctorUpdate, session: Session):
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(doctor, key, value)
    session.add(doctor)
    session.commit()
    session.refresh(doctor)
    return doctor
