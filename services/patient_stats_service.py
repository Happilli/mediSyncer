from datetime import date, datetime, timezone

from sqlmodel import Session, select

from models.appointments import Appointments, AppointmentStatus
from models.consultations import Consultations
from models.medication_logs import MedicationLogs
from models.medication_times import MedicationTimes
from models.medications import Medications
from models.patients import Patients
from models.prescriptions import Prescriptions
from schemas.patient_stats import (
    MonthlyAppointmentCount,
    PatientStatsOut,
    VitalPoint,
    VitalsTrendOut,
)


def _as_aware(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def _month_key(dt: datetime) -> str:
    return f"{dt.year:04d}-{dt.month:02d}"


def _last_n_months_keys(n: int) -> list[str]:
    now = datetime.now(timezone.utc)
    keys = []
    y, m = now.year, now.month
    for _ in range(n):
        keys.append(f"{y:04d}-{m:02d}")
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    return list(reversed(keys))


def _appointments_by_status(session: Session, patient_id: int):
    appts = session.exec(
        select(Appointments).where(Appointments.patient_id == patient_id)
    ).all()
    counts: dict[str, int] = {}
    for a in appts:
        counts[a.status.value] = counts.get(a.status.value, 0) + 1
    return appts, counts


def _medication_adherence(session: Session, patient_id: int):
    medications = session.exec(
        select(Medications).where(Medications.patient_id == patient_id)
    ).all()

    today = date.today()
    expected = 0
    taken = 0

    for med in medications:
        if med.start_date is None:
            continue

        days_elapsed = (today - med.start_date).days + 1
        if days_elapsed <= 0:
            continue
        days_elapsed = min(days_elapsed, med.duration_days)

        schedules = session.exec(
            select(MedicationTimes).where(MedicationTimes.medication_id == med.id)
        ).all()
        if not schedules:
            continue

        expected += days_elapsed * len(schedules)

        schedule_ids = [s.id for s in schedules]
        logs = session.exec(
            select(MedicationLogs).where(
                MedicationLogs.medication_time_id.in_(schedule_ids),
                MedicationLogs.log_date >= med.start_date,
                MedicationLogs.log_date <= today,
            )
        ).all()
        taken += sum(1 for log in logs if log.taken_at is not None)

    percent = round((taken / expected) * 100, 1) if expected > 0 else 0.0
    return percent, taken, expected


def _vitals_trend(session: Session, patient_id: int, limit: int = 10) -> VitalsTrendOut:
    results = session.exec(
        select(Consultations)
        .join(Appointments, Appointments.id == Consultations.appointment_id)
        .where(Appointments.patient_id == patient_id)
        .order_by(Consultations.created_at.asc())
    ).all()

    def pick(field: str) -> list[VitalPoint]:
        points = [
            VitalPoint(date=_as_aware(c.created_at), value=getattr(c, field))
            for c in results
            if getattr(c, field)
        ]
        return points[-limit:]

    return VitalsTrendOut(
        blood_pressure=pick("blood_pressure"),
        heart_rate=pick("heart_rate"),
        temperature=pick("temperature"),
        weight=pick("weight"),
    )


def get_patient_stats(patient: Patients, session: Session) -> PatientStatsOut:
    appts, status_counts = _appointments_by_status(session, patient.id)

    month_keys = _last_n_months_keys(6)
    month_counts = {k: 0 for k in month_keys}
    for a in appts:
        key = _month_key(_as_aware(a.appointment_at))
        if key in month_counts:
            month_counts[key] += 1

    now = datetime.now(timezone.utc)
    upcoming = sum(
        1
        for a in appts
        if _as_aware(a.appointment_at) >= now
        and a.status in (AppointmentStatus.pending, AppointmentStatus.confirmed)
    )

    adherence_percent, doses_taken, doses_expected = _medication_adherence(
        session, patient.id
    )

    total_prescriptions = len(
        session.exec(
            select(Prescriptions).where(Prescriptions.patient_id == patient.id)
        ).all()
    )

    total_consultations = len(
        session.exec(
            select(Consultations)
            .join(Appointments, Appointments.id == Consultations.appointment_id)
            .where(Appointments.patient_id == patient.id)
        ).all()
    )

    vitals = _vitals_trend(session, patient.id)

    return PatientStatsOut(
        total_appointments=len(appts),
        appointments_by_status=status_counts,
        appointments_last_6_months=[
            MonthlyAppointmentCount(month=k, count=month_counts[k]) for k in month_keys
        ],
        upcoming_appointments=upcoming,
        medication_adherence_percent=adherence_percent,
        doses_taken=doses_taken,
        doses_expected=doses_expected,
        total_prescriptions=total_prescriptions,
        total_consultations=total_consultations,
        vitals_trend=vitals,
    )
