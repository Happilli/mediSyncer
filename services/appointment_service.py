from datetime import date, datetime, time, timezone

from fastapi import HTTPException
from sqlmodel import Session, select

from models.appointments import Appointments, AppointmentStatus
from models.doctors import Doctors
from models.notifications import NotificationType
from models.patients import Patients
from models.timeslots import Timeslots
from schemas.appointment import (
    AppointmentCreate,
    AppointmentDoctorOut,
    AppointmentPatientOut,
    HospitalAppointmentOut,
)
from services.notification_service import create_notification, notify_hospital


def _expire_stale_pending(session: Session):
    now = datetime.now(timezone.utc)
    stale = session.exec(
        select(Appointments).where(
            Appointments.status == AppointmentStatus.pending,
            Appointments.appointment_at < now,
        )
    ).all()
    for appt in stale:
        appt.status = AppointmentStatus.cancelled
        session.add(appt)
        slot = session.exec(
            select(Timeslots).where(
                Timeslots.doctor_id == appt.doctor_id,
                Timeslots.appointment_at == appt.appointment_at,
            )
        ).first()
        if slot:
            slot.is_available = True
            session.add(slot)
    if stale:
        session.commit()


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

    doctor = session.get(Doctors, appointment.doctor_id)
    if doctor is not None:
        create_notification(
            session,
            doctor.user_id,
            NotificationType.appointment_booked,
            "New appointment booked",
            f"{patient.name} booked an appointment with you.",
            related_id=appointment.id,
            related_type="appointment",
        )

    notify_hospital(
        session,
        appointment.hospital_id,
        NotificationType.appointment_booked,
        "New appointment booked",
        f"{patient.name} booked an appointment with Dr. {doctor.name if doctor else 'a doctor'} at your hospital.",
        related_id=appointment.id,
        related_type="appointment",
    )

    return appointment


def list_my_appointment(
    session: Session,
    patient_id: int | None,
    doctor_id: int | None,
    filter_date: date | None = None,
    status: AppointmentStatus | None = None,
):

    _expire_stale_pending(session)
    query = select(Appointments)
    if patient_id is not None:
        query = query.where(Appointments.patient_id == patient_id)

    if doctor_id is not None:
        query = query.where(Appointments.doctor_id == doctor_id)

    if filter_date is not None:
        day_start = datetime.combine(filter_date, time.min, tzinfo=timezone.utc)
        day_end = datetime.combine(filter_date, time.max, tzinfo=timezone.utc)
        query = query.where(
            Appointments.appointment_at >= day_start,
            Appointments.appointment_at <= day_end,
        )
    if status is not None:
        query = query.where(Appointments.status == status)

    query = query.order_by(Appointments.appointment_at.desc())
    return session.exec(query).all()


def list_hospital_appointments(
    session: Session,
    hospital_id: int,
    filter_date: date | None = None,
    status: AppointmentStatus | None = None,
):
    _expire_stale_pending(session)

    query = (
        select(Appointments, Doctors, Patients)
        .join(Doctors, Doctors.id == Appointments.doctor_id)
        .join(Patients, Patients.id == Appointments.patient_id)
        .where(Appointments.hospital_id == hospital_id)
    )

    if filter_date is not None:
        day_start = datetime.combine(filter_date, time.min, tzinfo=timezone.utc)
        day_end = datetime.combine(filter_date, time.max, tzinfo=timezone.utc)
        query = query.where(
            Appointments.appointment_at >= day_start,
            Appointments.appointment_at <= day_end,
        )

    if status is not None:
        query = query.where(Appointments.status == status)

    query = query.order_by(Appointments.appointment_at.desc())

    results = session.exec(query).all()

    return [
        HospitalAppointmentOut(
            id=appointment.id,
            patient=AppointmentPatientOut(
                id=patient.id, name=patient.name, phone=patient.phone
            ),
            doctor=AppointmentDoctorOut(
                id=doctor.id,
                name=doctor.name,
                department=doctor.department,
                speciality=doctor.speciality,
            ),
            hospital_id=appointment.hospital_id,
            appointment_at=appointment.appointment_at,
            status=appointment.status,
            notes=appointment.notes,
        )
        for appointment, doctor, patient in results
    ]


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
    if appt.status in (AppointmentStatus.cancelled, AppointmentStatus.completed):
        raise HTTPException(
            status_code=400,
            detail=f"This appointment has been {appt.status.value} and cannot be modified.",
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

    doctor = session.get(Doctors, appt.doctor_id)
    patient = session.get(Patients, appt.patient_id)

    if current_doctor is not None and patient is not None:
        type_map = {
            AppointmentStatus.confirmed: NotificationType.appointment_confirmed,
            AppointmentStatus.cancelled: NotificationType.appointment_cancelled,
            AppointmentStatus.completed: NotificationType.appointment_completed,
        }
        notif_type = type_map.get(new_status)
        if notif_type is not None:
            create_notification(
                session,
                patient.user_id,
                notif_type,
                f"Appointment {new_status.value}",
                f"Your appointment status changed to {new_status.value}",
                related_id=appt.id,
                related_type="appointment",
            )
            notify_hospital(
                session,
                appt.hospital_id,
                notif_type,
                f"Appointment {new_status.value}",
                f"Appointment between Dr. {doctor.name if doctor else 'a doctor'} and {patient.name} is now {new_status.value}.",
                related_id=appt.id,
                related_type="appointment",
            )
    elif current_patient is not None and doctor is not None:
        create_notification(
            session,
            doctor.user_id,
            NotificationType.appointment_cancelled,
            "Appointment cancelled!",
            f"{current_patient.name} cancelled their appointnment.",
            related_id=appt.id,
            related_type="appointment",
        )
        notify_hospital(
            session,
            appt.hospital_id,
            NotificationType.appointment_cancelled,
            "Appointment cancelled!",
            f"{current_patient.name} cancelled their appointment with Dr. {doctor.name}.",
            related_id=appt.id,
            related_type="appointment",
        )
    return appt
