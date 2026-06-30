from fastapi import HTTPException
from sqlmodel import Session, select

from models.appointments import Appointments, AppointmentStatus
from models.doctors import Doctors
from models.patients import Patients
from models.timeslots import Timeslots
from schemas.appointment import AppointmentCreate


def book_appointment(data: AppointmentCreate, patient: Patients, session: Session):
    slot = session.get(Timeslots, data.timeslot_id, with_for_update=True)

    if slot is None:
        raise HTTPException(status_code=404, detail="Timeslot not found.")
    if not slot.is_available:
        raise HTTPException(status_code=400, detail="Timeslot is no longer available..")

    if patient.id is None:
        raise HTTPException(status_code=500, detail="Patient id is midding.")

    appointment = Appointments(
        doctor_id=slot.doctor_id,
        patient_id=patient.id,
        hospital_id=slot.hospital_id,
        appointment_at=slot.appointment_at,
        status=AppointmentStatus.pending,
        notes=data.notes,
    )
    slot.is_available = False

    session.add(appointment)
    session.add(slot)
    session.commit()
    session.refresh(appointment)

    return appointment


def list_my_appointment(
    session: Session, patient_id: int | None, doctor_id: int | None
):
    query = select(Appointments)
    if patient_id is not None:
        query = query.where(Appointments.patient_id == patient_id)

    if doctor_id is not None:
        query = query.where(Appointments.doctor_id == doctor_id)
    query = query.order_by(Appointments.appointment_at.desc())
    return session.exec(query).all()


def get_appointments(
    appointment_id: int, session: Session, current_user_id: int, current_role: str
):
    appt = session.get(Appointments, appointment_id)
    if appt is None:
        raise HTTPException(status_code=404, detail="Appointment not found..")
    if current_role == "patient":
        patient = session.exec(
            select(Patients).where(Patients.user_id == current_user_id)
        ).first()
        if patient is None or appt.patient_id != patient.id:
            raise HTTPException(status_code=403, detail="Not your appointment.")
    elif current_role == "doctor":
        doctor = session.exec(
            select(Doctors).where(Doctors.user_id == current_user_id)
        ).first()
        if doctor is None or appt.doctor_id != doctor.id:
            raise HTTPException(status_code=403, detail="Not your appointment.")
    else:
        raise HTTPException(status_code=403, detail="Not autho")
    return appt


def update_appointment_status(
    appointment_id: int,
    new_status: AppointmentStatus,
    session: Session,
    current_doctor=None,
    current_patient=None,
):
    appt = session.get(Appointments, appointment_id)
    if appt is None:
        raise HTTPException(status_code=404, detail="Appointment not found..")
    if appt.status == AppointmentStatus.cancelled:
        raise HTTPException(
            status_code=400,
            detail="This appointment has been cancelled and cannot be modified.",
        )
    if current_doctor is not None:
        if appt.doctor_id != current_doctor.id:
            raise HTTPException(status_code=403, detail="Not your appointment.")
    elif current_patient is not None:
        if appt.patient_id != current_patient.id:
            raise HTTPException(status_code=403, detail="Not your appointment.")
        if new_status != AppointmentStatus.cancelled:
            raise HTTPException(
                status_code=403, detail="Patients can only cancel appointments."
            )
        if appt.status != AppointmentStatus.pending:
            raise HTTPException(
                status_code=400, detail="Only pending appointments can be cancelled."
            )

    appt.status = new_status
    session.add(appt)

    if new_status == AppointmentStatus.cancelled:
        slot = session.exec(
            select(Timeslots).where(
                Timeslots.doctor_id == appt.doctor_id,
                Timeslots.appointment_at == appt.appointment_at,
            )
        ).first()
        if slot:
            slot.is_available = True
            session.add(slot)

    session.commit()
    session.refresh(appt)
    return appt
