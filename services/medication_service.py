from datetime import date, datetime, timedelta, timezone

from fastapi import HTTPException
from sqlmodel import Session, select

from models.doctors import Doctors
from models.medication_logs import MedicationLogs
from models.medication_times import MedicationTimes
from models.medications import Medications
from models.patients import Patients
from models.prescriptions import Prescriptions


def _today_log(session: Session, schedule_id: int) -> MedicationLogs | None:
    today = date.today()
    return session.exec(
        select(MedicationLogs).where(
            MedicationLogs.medication_time_id == schedule_id,
            MedicationLogs.log_date == today,
        )
    ).first()


def _schedule_to_out(schedule: MedicationTimes, session: Session) -> dict:
    medication = session.get(Medications, schedule.medication_id)
    if medication is None:
        raise HTTPException(
            status_code=404, detail="Medication not found for schedule.."
        )

    log = _today_log(session, schedule.id)
    end_date = medication.start_date + timedelta(days=medication.duration_days - 1)
    today = date.today()

    prescription = session.get(Prescriptions, medication.prescription_id)
    doctor = session.get(Doctors, prescription.doctor_id) if prescription else None

    sibling_count = session.exec(
        select(MedicationTimes).where(MedicationTimes.medication_id == medication.id)
    ).all()

    return {
        "schedule_id": schedule.id,
        "medication_id": medication.id,
        "prescription_id": medication.prescription_id,
        "patient_id": medication.patient_id,
        "name": medication.name,
        "dosage": medication.dosage,
        "instruction": medication.instruction,
        "dosage_time": schedule.dosage_time,
        "label": schedule.label,
        "frequency_per_day": len(sibling_count),
        "duration_days": medication.duration_days,
        "start_date": medication.start_date,
        "end_date": end_date,
        "is_active": medication.start_date <= today <= end_date,
        "is_taken": log is not None and log.taken_at is not None,
        "taken_at": log.taken_at if log is not None else None,
        "doctor_id": doctor.id if doctor else 0,
        "doctor_name": doctor.name if doctor else "Unknown",
    }


def list_my_medications(patient: Patients, session: Session, active_only: bool = False):
    medications = session.exec(
        select(Medications).where(Medications.patient_id == patient.id)
    ).all()

    results = []
    for m in medications:
        schedules = session.exec(
            select(MedicationTimes).where(MedicationTimes.medication_id == m.id)
        ).all()
        for s in schedules:
            results.append(_schedule_to_out(s, session))

    if active_only:
        results = [r for r in results if r["is_active"]]
    return results


def mark_medication_taken(schedule_id: int, patient: Patients, session: Session):
    schedule = session.get(MedicationTimes, schedule_id)
    if schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found..")

    medication = session.get(Medications, schedule.medication_id)
    if medication is None or medication.patient_id != patient.id:
        raise HTTPException(status_code=403, detail="Not your medication..")

    log = _today_log(session, schedule_id)
    now = datetime.now(timezone.utc)

    if log is None:
        log = MedicationLogs(
            medication_time_id=schedule_id,
            patient_id=patient.id,
            log_date=date.today(),
            taken_at=now,
        )
    else:
        log.taken_at = now

    session.add(log)
    session.commit()
    session.refresh(schedule)

    return _schedule_to_out(schedule, session)
