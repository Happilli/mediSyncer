from fastapi import HTTPException
from sqlmodel import Session, select

from models.appointments import Appointments, AppointmentStatus
from models.doctors import Doctors
from models.medical_history import Medical_History
from models.patients import Patients


def list_my_history(patient: Patients, session: Session):
    return session.exec(
        select(Medical_History)
        .where(Medical_History.patient_id == patient.id)
        .order_by(Medical_History.date.desc())
    ).all()


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
