from fastapi import HTTPException
from sqlmodel import Session

from models.appointments import Appointments
from models.patients import Patients
from models.timeslots import Timeslots
from schemas.appointment import AppointmentCreate


def book_appointment(data: AppointmentCreate, patient: Patients, session: Session):
    slot = session.get(Timeslots, data.timeslot_id)
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
        status="pending",
        notes=data.notes,
    )
    slot.is_available = False

    session.add(appointment)
    session.add(slot)
    session.commit()
    session.refresh(appointment)

    return appointment
