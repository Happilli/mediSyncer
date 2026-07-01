from fastapi import HTTPException
from sqlmodel import Session, select

from models.appointments import Appointments, AppointmentStatus
from models.consultations import Consultations
from models.doctors import Doctors
from models.medical_history import Medical_History
from schemas.consultation import ConsultationCreate


def create_consultation(data: ConsultationCreate, doctor: Doctors, session: Session):
    appt = session.get(Appointments, data.appointment_id)
    if appt is None:
        raise HTTPException(status_code=404, detail="Appointment not found..")
    if appt.doctor_id != doctor.id:
        raise HTTPException(status_code=403, detail="Not your appointment")
    if appt.status != AppointmentStatus.confirmed:
        raise HTTPException(
            status_code=400,
            detail="Appointment must be confirmed before starting  a consultations.",
        )

    existing = session.exec(
        select(Consultations.appointment_id == data.appointment_id)
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Consultations already exists for this appointment..",
        )

    consultation = Consultations(
        appointment_id=data.appointment_id,
        doctor_id=doctor.id,
        hospital_id=appt.hospital_id,
        complaint=data.complaint,
        symptoms=data.symptoms,
        diagnosis=data.diagnosis,
        notes=data.diagnosis,
        blood_pressure=data.blood_pressure,
        heart_rate=data.heart_rate,
        temperature=data.temperature,
        weight=data.weight,
    )
    session.add(consultation)
    session.commit()
    session.refresh(consultation)

    ## latching
    desp = [f"Complaint:{data.complaint}", f"Symptoms: {data.symptoms}"]
    if data.notes:
        desp.append(f"Notes:{data.notes}")

    history_entry = Medical_History(
        doctor_id=doctor.id,
        patient_id=appt.patient_id,
        title=data.diagnosis,
        description="|".join(desp),
    )
    session.add(history_entry)
    session.commit()

    return consultation


def get_consultation_by_appointment(
    appointment_id: int, doctor: Doctors, session: Session
):
    consultation = session.exec(
        select(Consultations).where(Consultations.appointment_id == appointment_id)
    ).first()
    if consultation is None:
        raise HTTPException(status_code=404, detail="Consultation not found..")
    if consultation.doctor_id != doctor.id:
        raise HTTPException(status_code=403, detail="Not your consultation.")
    return consultation
