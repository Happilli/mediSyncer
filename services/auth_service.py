from fastapi import HTTPException
from sqlmodel import Session, select

from models.hospitals import Hospitals
from models.patients import Patients
from models.users import UserRole, Users
from schemas.patient import PatientRegister
from utils.file_storage import create_user_folder
from utils.security import create_access_token, hash_password, verify_password

SECURITY_QUESTION = "What is your favorite medical term?"


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

    if user.id is None:
        raise HTTPException(status_code=500, detail="User ID generation failed")

    create_user_folder(user.id)
    patient = Patients(
        user_id=user.id,
        name=data.name,
        phone=data.phone,
        address=data.address,
        date_of_birth=data.date_of_birth,
        gender=data.gender,
        blood_group=data.blood_group,
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
        data={"sub": str(user.id), "role": user.role.value, "email": user.email}
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role,
        "email": user.email,
    }


def forgot_password_check(email: str, session: Session):
    user = session.exec(select(Users).where(Users.email == email)).first()
    if user is None or user.role != UserRole.hospital:
        raise HTTPException(
            status_code=404, detail="No hospital account found with this email."
        )

    hospital = session.exec(
        select(Hospitals).where(Hospitals.user_id == user.id)
    ).first()
    if hospital is None or hospital.security_answer_hash is None:
        raise HTTPException(
            status_code=400,
            detail="This account has no security answer set up. Contact support.",
        )

    return {"question": SECURITY_QUESTION}


def forgot_password_verify(
    email: str, security_answer: str, new_password: str, session: Session
):
    user = session.exec(select(Users).where(Users.email == email)).first()
    if user is None or user.role != UserRole.hospital:
        raise HTTPException(
            status_code=404, detail="No hospital account found with this email."
        )

    hospital = session.exec(
        select(Hospitals).where(Hospitals.user_id == user.id)
    ).first()
    if hospital is None or hospital.security_answer_hash is None:
        raise HTTPException(
            status_code=400,
            detail="This account has no security answer set up. Contact support.",
        )

    normalized_answer = security_answer.strip().lower()
    if not verify_password(normalized_answer, hospital.security_answer_hash):
        raise HTTPException(status_code=401, detail="That answer isn't correct.")

    user.password_hash = hash_password(new_password)
    session.add(user)
    session.commit()

    return {"message": "Password has been reset. You can now log in."}


def change_password(
    current_password: str, new_password: str, current_user: Users, session: Session
):
    if not verify_password(current_password, current_user.password_hash):
        raise HTTPException(status_code=401, detail="Current password is incorrect.")

    current_user.password_hash = hash_password(new_password)
    session.add(current_user)
    session.commit()

    return {"message": "Password has been changed."}
