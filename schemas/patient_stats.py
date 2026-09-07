from datetime import datetime

from pydantic import BaseModel


class MonthlyAppointmentCount(BaseModel):
    month: str
    count: int


class VitalPoint(BaseModel):
    date: datetime
    value: str


class VitalsTrendOut(BaseModel):
    blood_pressure: list[VitalPoint]
    heart_rate: list[VitalPoint]
    temperature: list[VitalPoint]
    weight: list[VitalPoint]


class PatientStatsOut(BaseModel):
    total_appointments: int
    appointments_by_status: dict[str, int]
    appointments_last_6_months: list[MonthlyAppointmentCount]
    upcoming_appointments: int
    medication_adherence_percent: float
    doses_taken: int
    doses_expected: int
    total_prescriptions: int
    total_consultations: int
    vitals_trend: VitalsTrendOut
