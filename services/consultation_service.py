from fastapi import HTTPException
from sqlmodel import Session, select

from models.appointments import Appointments, AppointmentStatus
from models.consultations import Consultations
from models.doctors import Doctors
from models.medical_history import Medical_History
from models.notifications import NotificationType
from models.patients import Patients
from schemas.consultation import ConsultationCreate
from services.notification_service import create_notification, notify_hospital


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
        select(Consultations).where(Consultations.appointment_id == data.appointment_id)
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Consultations already exists for this appointment..",
        )

    consultation = Consultations(
        appointment_id=data.appointment_id,
        doctor_id=doctor.id,
        hospital_id=appt.hospital_id,
        complaint=data.complaint,
        symptoms=data.symptoms,
        diagnosis=data.diagnosis,
        notes=data.notes,
        blood_pressure=data.blood_pressure,
        heart_rate=data.heart_rate,
        temperature=data.temperature,
        weight=data.weight,
    )
    session.add(consultation)

    appt.status = AppointmentStatus.completed
    session.add(appt)

    session.commit()
    session.refresh(consultation)

    ## latching
    desp = [f"Complaint:{data.complaint}", f"Symptoms: {data.symptoms}"]
    if data.notes:
        desp.append(f"Notes:{data.notes}")

    history_entry = Medical_History(
        doctor_id=doctor.id,
        patient_id=appt.patient_id,
        appointment_id=appt.id,
        title=data.diagnosis,
        description="|".join(desp),
    )
    session.add(history_entry)
    session.commit()

    patient = session.get(Patients, appt.patient_id)
    notify_hospital(
        session,
        consultation.hospital_id,
        NotificationType.consultation_created,
        "New consultation recorded",
        f"Dr. {doctor.name} recorded a consultation for {patient.name if patient else 'a patient'}.",
        related_id=consultation.id,
        related_type="consultation",
    )

    if patient is not None:
        create_notification(
            session,
            patient.user_id,
            NotificationType.appointment_completed,
            "Appointment completed",
            f"Dr. {doctor.name} has completed your consultation.",
            related_id=appt.id,
            related_type="appointment",
        )

    return consultation


def get_consultation_by_appointment(
    appointment_id: int,
    session: Session,
    current_user_id: int,
    current_role: str,
):
    consultation = session.exec(
        select(Consultations).where(Consultations.appointment_id == appointment_id)
    ).first()
    if consultation is None:
        raise HTTPException(status_code=404, detail="Consultation not found..")

    if current_role == "doctor":
        doctor = session.exec(
            select(Doctors).where(Doctors.user_id == current_user_id)
        ).first()
        if doctor is None or consultation.doctor_id != doctor.id:
            raise HTTPException(status_code=403, detail="Not your consultation.")
    elif current_role == "patient":
        appt = session.get(Appointments, consultation.appointment_id)
        patient = session.exec(
            select(Patients).where(Patients.user_id == current_user_id)
        ).first()
        if appt is None or patient is None or appt.patient_id != patient.id:
            raise HTTPException(status_code=403, detail="Not your consultation.")
    else:
        raise HTTPException(status_code=403, detail="Not authorized.")

    return consultation
