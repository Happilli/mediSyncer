from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlmodel import Session, select

from models.appointments import Appointments, AppointmentStatus
from models.consultations import Consultations
from models.doctors import Doctors
from models.medications import Medications
from models.patients import Patients
from models.prescriptions import Prescriptions
from schemas.prescription import (
    MedicationOut,
    PrescriptionCreate,
    PrescriptionDetailOut,
)


def _to_detail(
    prescription: Prescriptions, medications: list[Medications]
) -> PrescriptionDetailOut:
    return PrescriptionDetailOut(
        id=prescription.id,
        doctor_id=prescription.doctor_id,
        appointment_id=prescription.appointment_id,
        patient_id=prescription.patient_id,
        diagnosis=prescription.diagnosis,
        instructions=prescription.instructions,
        created_at=prescription.created_at,
        follow_up_date=prescription.follow_up_date,
        medications=[MedicationOut.model_validate(m) for m in medications],
    )


def create_prescription(data: PrescriptionCreate, doctor: Doctors, session: Session):
    appt = session.get(Appointments, data.appointment_id)
    if appt is None:
        raise HTTPException(status_code=404, detail="Appointment not found..")
    if appt.doctor_id != doctor.id:
        raise HTTPException(status_code=403, detail="Not your appointment..")
    if appt.status != AppointmentStatus.confirmed:
        raise HTTPException(
            status_code=400,
            detail="Appointment must be confirmed before prescribing anything.",
        )
    consult = session.exec(
        select(Consultations).where(Consultations.appointment_id == data.appointment_id)
    ).first()
    if consult is None:
        raise HTTPException(
            status_code=400,
            detail="A Consultations must be recorded before prescribing anything.",
        )
    existing_pres = session.exec(
        select(Prescriptions).where(Prescriptions.appointment_id == data.appointment_id)
    ).first()

    if existing_pres is not None:
        raise HTTPException(
            status_code=400,
            detail="A Prescription already exists btw.",
        )

    follow_up = data.follow_up_date or (datetime.now(timezone.utc) + timedelta(days=7))

    prescription = Prescriptions(
        doctor_id=doctor.id,
        appointment_id=data.appointment_id,
        patient_id=appt.patient_id,
        diagnosis=data.diagnosis,
        instructions=data.instructions,
        follow_up_date=follow_up,
    )
    appt.status = AppointmentStatus.completed
    session.add(appt)
    session.add(prescription)
    session.commit()
    session.refresh(prescription)

    if prescription.id is None:
        raise HTTPException(status_code=500, detail="Prescription id generation failed")

    medications = []
    for med in data.medications:
        medication = Medications(
            prescription_id=prescription.id,
            patient_id=appt.patient_id,
            name=med.name,
            dosage=med.dosage,
            dosage_time=med.dosage_time,
            instruction=med.instruction,
            frequency_per_day=med.frequency_per_day,
            duration_days=med.duration_days,
        )
        session.add(medication)
        medications.append(medication)

    session.commit()
    for m in medications:
        session.refresh(m)
    return _to_detail(prescription, medications)


def list_my_prescriptions(patient: Patients, session: Session):
    return session.exec(
        select(Prescriptions)
        .where(Prescriptions.patient_id == patient.id)
        .order_by(Prescriptions.created_at.desc())
    ).all()


def get_prescription_detail(
    prescription_id: int, session: Session, current_user_id: int, current_role: str
):
    prescription = session.get(Prescriptions, prescription_id)
    if prescription is None:
        raise HTTPException(status_code=404, detail="Prescription not found..")

    if current_role == "patient":
        patient = session.exec(
            select(Patients).where(Patients.user_id == current_user_id)
        ).first()
        if patient is None or prescription.patient_id != patient.id:
            raise HTTPException(status_code=403, detail="Not your prescription.")
    elif current_role == "doctor":
        doctor = session.exec(
            select(Doctors).where(Doctors.user_id == current_user_id)
        ).first()
        if doctor is None or prescription.doctor_id != doctor.id:
            raise HTTPException(status_code=403, detail="Not your prescription.")
    else:
        raise HTTPException(status_code=403, detail="Not authorized.")

    medications = session.exec(
        select(Medications).where(Medications.prescription_id == prescription_id)
    ).all()
    return _to_detail(prescription, medications)
