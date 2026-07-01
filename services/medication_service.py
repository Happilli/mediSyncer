from datetime import datetime, timezone

from fastapi import HTTPException
from sqlmodel import Session, select

from models.medications import Medications
from models.patients import Patients


def list_my_medications(patient: Patients, session: Session):
    return session.exec(
        select(Medications).where(Medications.patient_id == patient.id)
    ).all()


def mark_medication_taken(medication_id: int, patient: Patients, session: Session):
    medication = session.get(Medications, medication_id)
    if medication is None:
        raise HTTPException(status_code=404, detail="Medication not found..")
    if medication.patient_id != patient.id:
        raise HTTPException(status_code=403, detail="Not your medication..")

    medication.is_taken = True
    medication.taken_at = datetime.now(timezone.utc)
    session.add(medication)
    session.commit()
    session.refresh(medication)
    return medication
