from pydantic import BaseModel


class PatientVerificationFunnel(BaseModel):
    registered: int
    submitted_docs: int
    verified: int


class DoctorVerificationFunnel(BaseModel):
    registered: int
    verified: int


class VerificationFunnelOut(BaseModel):
    patients: PatientVerificationFunnel
    doctors: DoctorVerificationFunnel
