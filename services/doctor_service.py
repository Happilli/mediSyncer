from fastapi import HTTPException
from sqlmodel import Session, select

from models.doctor_hospital import Doctor_Hospital
from models.doctors import Doctors
from models.hospitals import Hospitals
from models.timeslots import Timeslots
from models.users import UserRole, Users
from schemas.doctor import DoctorRegister, TimeSlotCreate
from utils.security import hash_password


def register_doctor(data: DoctorRegister, session: Session, current_hospital: Users):
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
        license_photo_url=data.license_photo_url,
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
