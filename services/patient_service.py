from fastapi import HTTPException
from sqlmodel import Session, select

from models.appointments import Appointments, AppointmentStatus
from models.patients import Patients
from schemas.patient import PatientUpdate


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
