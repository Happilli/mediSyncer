from datetime import date

from fastapi import HTTPException
from sqlmodel import Session, select

from models.appointments import Appointments
from models.doctors import Doctors
from models.medical_history import Medical_History
from models.patients import Patients


def list_my_history(
    patient: Patients,
    session: Session,
    doctor_id: int | None = None,
    from_date: date | None = None,
):
    query = select(Medical_History).where(Medical_History.patient_id == patient.id)

    if doctor_id is not None:
        query = query.where(Medical_History.doctor_id == doctor_id)

    if from_date is not None:
        query = query.where(Medical_History.date >= from_date)

    query = query.order_by(Medical_History.date.desc())
    return session.exec(query).all()


def list_patient_history_for_doctor(patient_id: int, doctor: Doctors, session: Session):
    if doctor.id is None:
        raise HTTPException(status_code=500, detail="Doctor id is missing..")

    has_relationship = session.exec(
        select(Appointments).where(
            Appointments.doctor_id == doctor.id,
            Appointments.patient_id == patient_id,
        )
    ).first()
    if has_relationship is None:
        raise HTTPException(
            status_code=403,
            detail="You can only view history for patients who have booked an appointment with you.",
        )
    return session.exec(
        select(Medical_History)
        .where(Medical_History.patient_id == patient_id)
        .order_by(Medical_History.date.desc())
    ).all()
