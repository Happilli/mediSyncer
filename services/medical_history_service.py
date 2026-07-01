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

    treated = session.exec(
        select(Appointments).where(
            Appointments.doctor_id == doctor.id,
            Appointments.patient_id == patient_id,
            Appointments.status == AppointmentStatus.completed,
        )
    ).first()
    if treated is None:
        raise HTTPException(
            status_code=403,
            detail="You can only access the patient, you have treated so far..",
        )
    return session.exec(
        select(Medical_History)
        .where(Medical_History.patient_id == patient_id)
        .order_by(Medical_History.date.desc())
    ).all()
