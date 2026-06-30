from fastapi import HTTPException
from sqlmodel import Session, select

from models.patients import Patients


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
