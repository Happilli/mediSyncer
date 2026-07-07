from fastapi import HTTPException, UploadFile
from sqlmodel import Session, select

from models.appointments import Appointments, AppointmentStatus
from models.patients import Patients
from schemas.patient import PatientUpdate
from utils.file_storage import (
    delete_file_by_url,
    delete_user_folder,
    save_verification_doc,
)


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
    return {"message": f"{patient.name} has been verified.."}


def update_patient_profile(patient: Patients, data: PatientUpdate, session: Session):
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(patient, key, value)
    session.add(patient)
    session.commit()
    session.refresh(patient)
    return patient


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
    return patients


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


def delete_patient(patient_id: int, session: Session):
    from models.users import Users

    patient = session.get(Patients, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient is not found..")

    user_id = patient.user_id
    user = session.get(Users, user_id)
    if user is not None:
        session.delete(user)
    session.commit()

    delete_user_folder(user_id)

    return {
        "message": f"{patient.name} and all associated records have been nuked from the mediSync platform.."
    }
