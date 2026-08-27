from fastapi import HTTPException, UploadFile
from sqlmodel import Session, select

from models.appointments import Appointments, AppointmentStatus
from models.notifications import NotificationType
from models.patients import Patients
from models.users import UserRole, Users
from schemas.patient import PatientSecurityAnswerUpdate, PatientUpdate
from services.notification_service import create_notification, notify_role
from utils.file_storage import (
    delete_file_by_url,
    delete_user_folder,
    save_verification_doc,
)
from utils.security import hash_password, verify_password


def patient_to_out(patient: Patients) -> dict:
    return {
        **patient.model_dump(),
        "has_security_answer": patient.security_answer_hash is not None,
    }


def list_all_patients(session: Session):
    return session.exec(select(Patients)).all()


def get_patient_admin(patient_id: int, session: Session):
    patient = session.get(Patients, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient is not found..")
    return patient


def verify_patient(patient_id: int, session: Session):
    patient = session.get(Patients, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient is not found..")

    patient.is_verified = True
    session.add(patient)
    session.commit()
    session.refresh(patient)

    create_notification(
        session,
        patient.user_id,
        NotificationType.patient_verified,
        "You're verified!",
        "Your identity has been verified. You can fully access mediSyncer now.",
        related_id=patient.id,
        related_type="patient",
    )
    return {"message": f"{patient.name} has been verified.."}


def update_patient_profile(patient: Patients, data: PatientUpdate, session: Session):
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(patient, key, value)
    session.add(patient)
    session.commit()
    session.refresh(patient)
    return patient


def list_all_my_patients(doctor_id: int, session: Session):
    patients = session.exec(
        select(Patients)
        .join(Appointments, Appointments.patient_id == Patients.id)
        .where(Appointments.doctor_id == doctor_id)
        .distinct()
    ).all()
    result = []
    for p in patients:
        user = session.get(Users, p.user_id)
        result.append({**p.model_dump(), "email": user.email if user else ""})
    return result


def get_patient_for_doctor(patient_id: int, doctor_id: int, session: Session):
    has_appt = session.exec(
        select(Appointments).where(
            Appointments.doctor_id == doctor_id,
            Appointments.patient_id == patient_id,
        )
    ).first()
    if has_appt is None:
        raise HTTPException(status_code=403, detail="Not your patient.")

    patient = session.get(Patients, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient is not found..")

    user = session.get(Users, patient.user_id)
    return {**patient.model_dump(), "email": user.email if user else ""}


def list_treated_patients(doctor_id: int, session: Session):
    patients = session.exec(
        select(Patients)
        .join(Appointments, Appointments.patient_id == Patients.id)
        .where(
            Appointments.doctor_id == doctor_id,
            Appointments.status == AppointmentStatus.completed,
        )
        .distinct()
    ).all()

    result = []
    for p in patients:
        user = session.get(Users, p.user_id)
        result.append(
            {
                **p.model_dump(),
                "email": user.email if user else "",
            }
        )
    return result


async def request_patient_verification(
    citizenship_number: str,
    file: UploadFile,
    patient: Patients,
    session: Session,
):
    if (
        patient.citizenship_number is not None
        or patient.citizenship_photo_url is not None
    ):
        raise HTTPException(
            status_code=400,
            detail="Verification already requested. Contact support to resubmit.",
        )

    photo_url = await save_verification_doc(file, patient.user_id, "citizenship_photos")

    patient.citizenship_number = citizenship_number
    patient.citizenship_photo_url = photo_url
    session.add(patient)
    session.commit()
    session.refresh(patient)

    notify_role(
        session,
        UserRole.admin,
        NotificationType.patient_verification_requested,
        "New patient verification request",
        f"{patient.name} submitted citizenship documents for verification.",
        related_id=patient.id,
        related_type="patient",
    )
    return patient


async def update_patient_profile_pic(
    patient: Patients, file: UploadFile, session: Session
):
    old_url = patient.profile_pic_url
    image_url = await save_verification_doc(file, patient.user_id, "profile_pics")

    patient.profile_pic_url = image_url
    session.add(patient)
    session.commit()
    session.refresh(patient)

    delete_file_by_url(old_url)
    return patient


def update_patient_security_answer(
    patient: Patients, user: Users, data: PatientSecurityAnswerUpdate, session: Session
):
    if not verify_password(data.current_password, user.password_hash):
        raise HTTPException(status_code=401, detail="current password is incorrect.")

    patient.security_answer_hash = hash_password(data.security_answer.strip().lower())
    session.add(patient)
    session.commit()
    session.refresh(patient)

    return {"message": "Security answer has been updated.."}


def delete_patient(patient_id: int, session: Session):

    patient = session.get(Patients, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient is not found..")

    patient_name = patient.name
    user_id = patient.user_id
    user = session.get(Users, user_id)
    if user is not None:
        session.delete(user)
    session.commit()

    delete_user_folder(user_id)

    return {
        "message": f"{patient_name} and all associated records have been nuked from the mediSync platform.."
    }
