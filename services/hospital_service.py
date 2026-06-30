from fastapi import HTTPException
from sqlmodel import Session, select

from models.hospitals import Hospitals
from models.users import UserRole, Users
from schemas.hospital import HospitalRegister
from utils.security import hash_password


def register_hospital(data: HospitalRegister, session: Session):
    existing = session.exec(select(Users).where(Users.email == data.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="email already registered")

    existing_rez = session.exec(
        select(Hospitals).where(
            Hospitals.registration_number == data.registration_number
        )
    ).first()
    if existing_rez:
        raise HTTPException(
            status_code=400, detail="hospital registration number already registered"
        )
    user = Users(
        email=data.email,
        password_hash=hash_password(data.password),
        role=UserRole.hospital,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    if user.id is None:
        raise HTTPException(status_code=500, detail="User ID generation failed")

    hospital = Hospitals(
        user_id=user.id,
        name=data.name,
        address=data.address,
        phone=data.phone,
        registration_number=data.registration_number,
        website=data.website,
        description=data.description,
        is_active=True,
    )
    session.add(hospital)
    session.commit()
    session.refresh(hospital)

    return {
        "message": f"{hospital.name} registered!!",
    }


def list_hospitals(session: Session, search: str | None = None):
    query = select(Hospitals).where(Hospitals.is_active == True)
    if search:
        query = query.where(Hospitals.name.like(f"%{search}%"))
    return session.exec(query).all()


def get_hospital(hospital_id: int, session: Session):
    hospital = session.get(Hospitals, hospital_id)
    if hospital is None:
        raise HTTPException(status_code=404, detail="Hospital not found..")
    return hospital
