from fastapi import HTTPException
from sqlmodel import Session, select

from models.patients import BloodGroup, Gender, Patients
from models.users import UserRole, Users
from schemas.patient import PatientRegister
from utils.security import create_access_token, hash_password, verify_password


def register_patient(data: PatientRegister, session: Session):
    existing = session.exec(select(Users).where(Users.email == data.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="email already registered..")

    user = Users(
        email=data.email,
        password_hash=hash_password(data.password),
        role=UserRole.patient,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    assert user.id is not None

    patient = Patients(
        user_id=user.id,
        name=data.name,
        phone=data.phone,
        address=data.address,
        date_of_birth=data.date_of_birth,
        gender=Gender(data.gender.lower()),
        blood_group=BloodGroup(data.blood_group.upper()),
        emergency_contact=data.emergency_contact,
    )
    session.add(patient)
    session.commit()
    session.refresh(patient)
    return {
        "message": f"{patient.name} registered",
        "remarks": "You will be able to fully use after verfying this id through citizenship",
    }


def login_user(email: str, password: str, session: Session):
    user = session.exec(select(Users).where(Users.email == email)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is not active")

    token = create_access_token(
        data={"sub": str(user.id), "role": user.role, "email": user.email}
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role,
        "email": user.email,
    }
