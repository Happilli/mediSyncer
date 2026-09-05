from datetime import date, datetime, timezone

from fastapi import HTTPException
from sqlmodel import Session, select

from models.appointments import Appointments, AppointmentStatus
from models.consultations import Consultations
from models.doctors import Doctors
from models.hospitals import Hospitals
from models.medication_times import MedicationTimes
from models.medications import Medications
from models.notifications import NotificationType
from models.patients import Patients
from models.prescriptions import DispenseStatus, Prescriptions
from schemas.prescription import (
    DispenseQueueItemOut,
    MedicationOut,
    PrescriptionCreate,
    PrescriptionDetailOut,
)
from services.medication_service import _schedule_to_out
from services.notification_service import create_notification, notify_hospital


def _medication_to_out_list(
    medication: Medications, session: Session
) -> list[MedicationOut]:
    schedules = session.exec(
        select(MedicationTimes).where(MedicationTimes.medication_id == medication.id)
    ).all()
    return [MedicationOut(**_schedule_to_out(s, session)) for s in schedules]


def _to_detail(
    prescription: Prescriptions, medications: list[Medications], session: Session
) -> PrescriptionDetailOut:
    all_meds: list[MedicationOut] = []
    for m in medications:
        all_meds.extend(_medication_to_out_list(m, session))

    return PrescriptionDetailOut(
        id=prescription.id,
        doctor_id=prescription.doctor_id,
        appointment_id=prescription.appointment_id,
        patient_id=prescription.patient_id,
        hospital_id=prescription.hospital_id,
        diagnosis=prescription.diagnosis,
        instructions=prescription.instructions,
        dispense_status=prescription.dispense_status,
        created_at=prescription.created_at,
        follow_up_date=prescription.follow_up_date,
        medications=all_meds,
    )


def create_prescription(data: PrescriptionCreate, doctor: Doctors, session: Session):
    appt = session.get(Appointments, data.appointment_id)
    if appt is None:
        raise HTTPException(status_code=404, detail="Appointment not found..")
    if appt.doctor_id != doctor.id:
        raise HTTPException(status_code=403, detail="Not your appointment..")
    if appt.status != AppointmentStatus.completed:
        raise HTTPException(
            status_code=400,
            detail="A consultation must be recorded before prescribing anything.",
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

    dispense_status = (
        DispenseStatus.pending if data.medications else DispenseStatus.not_required
    )

    prescription = Prescriptions(
        doctor_id=doctor.id,
        appointment_id=data.appointment_id,
        patient_id=appt.patient_id,
        hospital_id=appt.hospital_id,
        diagnosis=data.diagnosis,
        instructions=data.instructions,
        follow_up_date=data.follow_up_date,
        dispense_status=dispense_status,
    )

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
            instruction=med.instruction,
            duration_days=med.duration_days,
        )
        session.add(medication)
        session.commit()
        session.refresh(medication)

        for t in med.dosage_times:
            schedule = MedicationTimes(
                medication_id=medication.id,
                dosage_time=t.dosage_time,
                label=t.label,
            )
            session.add(schedule)

        medications.append(medication)

    session.commit()

    patient = session.get(Patients, appt.patient_id)
    if patient is not None:
        create_notification(
            session,
            patient.user_id,
            NotificationType.prescription_created,
            "New prescription",
            f"Dr. {doctor.name} issued you a new prescription.",
            related_id=prescription.id,
            related_type="prescription",
        )

    if dispense_status == DispenseStatus.pending:
        med_names = ", ".join(m.name for m in medications)
        notify_hospital(
            session,
            appt.hospital_id,
            NotificationType.prescription_pending_dispense,
            "New medicines to prepare",
            f"{patient.name if patient else 'A patient'} needs: {med_names}",
            related_id=prescription.id,
            related_type="prescription",
        )

    return _to_detail(prescription, medications, session)


def list_my_prescriptions(
    patient, session, doctor_id=None, from_date=None, to_date=None
):
    query = select(Prescriptions).where(Prescriptions.patient_id == patient.id)
    if doctor_id is not None:
        query = query.where(Prescriptions.doctor_id == doctor_id)
    if from_date is not None:
        query = query.where(Prescriptions.created_at >= from_date)
    if to_date is not None:
        query = query.where(Prescriptions.created_at <= to_date)
    return session.exec(query.order_by(Prescriptions.created_at.desc())).all()


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
    elif current_role == "hospital":
        hospital = session.exec(
            select(Hospitals).where(Hospitals.user_id == current_user_id)
        ).first()
        if hospital is None or prescription.hospital_id != hospital.id:
            raise HTTPException(status_code=403, detail="Not your prescription.")
    else:
        raise HTTPException(status_code=403, detail="Not authorized.")

    medications = session.exec(
        select(Medications).where(Medications.prescription_id == prescription_id)
    ).all()
    return _to_detail(prescription, medications, session)


def get_dispense_queue(
    hospital_id: int, session: Session
) -> list[DispenseQueueItemOut]:
    results = session.exec(
        select(Prescriptions, Patients)
        .join(Patients, Patients.id == Prescriptions.patient_id)
        .where(
            Prescriptions.hospital_id == hospital_id,
            Prescriptions.dispense_status == DispenseStatus.pending,
        )
        .order_by(Prescriptions.created_at)
    ).all()

    items = []
    for prescription, patient in results:
        meds = session.exec(
            select(Medications).where(Medications.prescription_id == prescription.id)
        ).all()
        items.append(
            DispenseQueueItemOut(
                prescription_id=prescription.id,
                patient_name=patient.name,
                medicine_names=[m.name for m in meds],
                created_at=prescription.created_at,
            )
        )
    return items


def mark_prescription_ready(prescription_id: int, hospital_id: int, session: Session):
    prescription = session.get(Prescriptions, prescription_id)
    if prescription is None:
        raise HTTPException(status_code=404, detail="Prescription not found..")
    if prescription.hospital_id != hospital_id:
        raise HTTPException(status_code=403, detail="Not your prescription.")
    if prescription.dispense_status != DispenseStatus.pending:
        raise HTTPException(
            status_code=400,
            detail=f"Prescription is {prescription.dispense_status.value}, cannot mark ready.",
        )

    prescription.dispense_status = DispenseStatus.ready
    session.add(prescription)
    session.commit()
    session.refresh(prescription)

    patient = session.get(Patients, prescription.patient_id)
    if patient is not None:
        create_notification(
            session,
            patient.user_id,
            NotificationType.prescription_ready,
            "Prescription ready",
            "Your medicines are ready for collection.",
            related_id=prescription.id,
            related_type="prescription",
        )

    return prescription


def confirm_collection(prescription_id: int, patient: Patients, session: Session):
    prescription = session.get(Prescriptions, prescription_id)
    if prescription is None:
        raise HTTPException(status_code=404, detail="Prescription not found..")
    if prescription.patient_id != patient.id:
        raise HTTPException(status_code=403, detail="Not your prescription.")
    if prescription.dispense_status != DispenseStatus.ready:
        raise HTTPException(
            status_code=400, detail="Prescription is not ready for collection yet."
        )

    prescription.dispense_status = DispenseStatus.collected
    session.add(prescription)

    medications = session.exec(
        select(Medications).where(Medications.prescription_id == prescription_id)
    ).all()
    today = date.today()
    for med in medications:
        med.start_date = today
        session.add(med)

    session.commit()
    session.refresh(prescription)

    notify_hospital(
        session,
        prescription.hospital_id,
        NotificationType.prescription_collected,
        "Prescription collected",
        f"{patient.name} collected their prescription.",
        related_id=prescription.id,
        related_type="prescription",
    )

    return prescription
