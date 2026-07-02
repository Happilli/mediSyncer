from fastapi import HTTPException, UploadFile
from sqlmodel import Session, select

from models.appointments import Appointments, AppointmentStatus
from models.patients import Patients
from schemas.patient import PatientUpdate
from utils.file_storage import save_verification_doc


def list_unverified_patients(session: Session):
    return session.exec(select(Patients).where(Patients.is_verified == False)).all()


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
