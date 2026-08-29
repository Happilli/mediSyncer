from datetime import date, datetime, timedelta, timezone

from fastapi import HTTPException
from sqlmodel import Session, select

from models.doctors import Doctors
from models.medication_logs import MedicationLogs
from models.medications import Medications
from models.patients import Patients
from models.prescriptions import Prescriptions


def _today_log(session: Session, medication_id: int) -> MedicationLogs | None:
    today = date.today()
    return session.exec(
        select(MedicationLogs).where(
            MedicationLogs.medication_id == medication_id,
            MedicationLogs.log_date == today,
        )
    ).first()


def _to_out(medication: Medications, session: Session) -> dict:
    log = _today_log(session, medication.id)
    end_date = medication.start_date + timedelta(days=medication.duration_days - 1)
    today = date.today()

    prescription = session.get(Prescriptions, medication.prescription_id)
    doctor = session.get(Doctors, prescription.doctor_id) if prescription else None

    return {
        **medication.model_dump(),
        "end_date": end_date,
        "is_active": medication.start_date <= today <= end_date,
        "is_taken": log is not None and log.taken_at is not None,
        "taken_at": log.taken_at if log is not None else None,
        "doctor_id": doctor.id if doctor else 0,
        "doctor_name": doctor.name if doctor else "Unknown",
    }


def list_my_medications(patient: Patients, session: Session):
    medications = session.exec(
        select(Medications).where(Medications.patient_id == patient.id)
    ).all()
    return [_to_out(m, session) for m in medications]


def mark_medication_taken(medication_id: int, patient: Patients, session: Session):
    medication = session.get(Medications, medication_id)
    if medication is None:
        raise HTTPException(status_code=404, detail="Medication not found..")
    if medication.patient_id != patient.id:
        raise HTTPException(status_code=403, detail="Not your medication..")

    log = _today_log(session, medication_id)
    now = datetime.now(timezone.utc)

    if log is None:
        log = MedicationLogs(
            medication_id=medication_id,
            patient_id=patient.id,
            log_date=date.today(),
            taken_at=now,
        )
    else:
        log.taken_at = now

    session.add(log)
    session.commit()
    session.refresh(medication)

    return _to_out(medication, session)
