from sqlmodel import Session, col, func, select

from models.doctors import Doctors
from models.patients import Patients
from schemas.admin import (
    DoctorVerificationFunnel,
    PatientVerificationFunnel,
    VerificationFunnelOut,
)


def get_verification_funnel(session: Session) -> VerificationFunnelOut:
    patients_registered = session.exec(select(func.count()).select_from(Patients)).one()

    patients_submitted = session.exec(
        select(func.count())
        .select_from(Patients)
        .where(col(Patients.citizenship_number).is_not(None))
    ).one()

    patients_verified = session.exec(
        select(func.count())
        .select_from(Patients)
        .where(col(Patients.is_verified) == True)
    ).one()

    doctors_registered = session.exec(select(func.count()).select_from(Doctors)).one()

    doctors_verified = session.exec(
        select(func.count())
        .select_from(Doctors)
        .where(col(Doctors.is_verified) == True)
    ).one()

    return VerificationFunnelOut(
        patients=PatientVerificationFunnel(
            registered=patients_registered,
            submitted_docs=patients_submitted,
            verified=patients_verified,
        ),
        doctors=DoctorVerificationFunnel(
            registered=doctors_registered,
            verified=doctors_verified,
        ),
    )
