from typing import Optional

from pydantic import BaseModel


class MonthlyAppointmentCount(BaseModel):
    month: str
    count: int


class DoctorStatsOut(BaseModel):
    total_appointments: int
    appointments_by_status: dict[str, int]
    appointments_last_6_months: list[MonthlyAppointmentCount]
    upcoming_appointments: int
    total_patients: int
    patients_this_month: int
    total_prescriptions: int
    total_consultations: int
    upcoming_followups: int
