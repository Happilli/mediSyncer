from fastapi import HTTPException
from sqlmodel import Session, select

from models.doctor_hospital import Doctor_Hospital
from models.doctors import Doctors
from models.hospitals import Hospitals
from models.users import UserRole, Users
from schemas.doctor import DoctorRegister
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
