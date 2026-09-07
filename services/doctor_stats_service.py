from datetime import datetime, timedelta, timezone

from sqlmodel import Session, col, select

from models.appointments import Appointments, AppointmentStatus
from models.consultations import Consultations
from models.doctors import Doctors
from models.prescriptions import Prescriptions
from schemas.doctor_stats import DoctorStatsOut, MonthlyAppointmentCount


def get_doctor_stats(doctor: Doctors, session: Session) -> DoctorStatsOut:
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    appointments = session.exec(
        select(Appointments).where(Appointments.doctor_id == doctor.id)
    ).all()

    total_appointments = len(appointments)

    status_counts: dict[str, int] = {}
    for a in appointments:
        key = a.status.value.capitalize()
        status_counts[key] = status_counts.get(key, 0) + 1

    upcoming_appointments = len(
        [
            a
            for a in appointments
            if a.status in (AppointmentStatus.pending, AppointmentStatus.confirmed)
            and a.appointment_at >= now
        ]
    )

    six_months_ago = (month_start - timedelta(days=180)).replace(day=1)
    monthly_counts: dict[str, int] = {}
    cursor = six_months_ago
    for _ in range(6):
        monthly_counts[cursor.strftime("%Y-%m")] = 0
        if cursor.month == 12:
            cursor = cursor.replace(year=cursor.year + 1, month=1)
        else:
            cursor = cursor.replace(month=cursor.month + 1)

    for a in appointments:
        key = a.appointment_at.strftime("%Y-%m")
        if key in monthly_counts:
            monthly_counts[key] += 1

    appointments_last_6_months = [
        MonthlyAppointmentCount(month=k, count=v) for k, v in monthly_counts.items()
    ]

    real_patient_statuses = [AppointmentStatus.confirmed, AppointmentStatus.completed]

    total_patients = len(
        set(a.patient_id for a in appointments if a.status in real_patient_statuses)
    )

    patients_this_month = len(
        set(
            a.patient_id
            for a in appointments
            if a.status in real_patient_statuses and a.appointment_at >= month_start
        )
    )

    total_prescriptions = session.exec(
        select(Prescriptions).where(Prescriptions.doctor_id == doctor.id)
    ).all()

    total_consultations = session.exec(
        select(Consultations).where(Consultations.doctor_id == doctor.id)
    ).all()

    upcoming_followups = session.exec(
        select(Prescriptions).where(
            Prescriptions.doctor_id == doctor.id,
            col(Prescriptions.follow_up_date).is_not(None),
            col(Prescriptions.follow_up_date) >= now,
        )
    ).all()

    return DoctorStatsOut(
        total_appointments=total_appointments,
        appointments_by_status=status_counts,
        appointments_last_6_months=appointments_last_6_months,
        upcoming_appointments=upcoming_appointments,
        total_patients=total_patients,
        patients_this_month=patients_this_month,
        total_prescriptions=len(total_prescriptions),
        total_consultations=len(total_consultations),
        upcoming_followups=len(upcoming_followups),
    )
