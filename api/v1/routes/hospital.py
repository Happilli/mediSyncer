from fastapi import APIRouter, Depends
from sqlmodel import Session

from database import get_session
from schemas.hospital import HospitalRegister
from services.hospital_service import register_hospital
from utils.dependencies import require_admin

router = APIRouter(prefix="/hospitals", tags=["hospitals"])


@router.post("/register", status_code=201)
def register_hospita(
    data: HospitalRegister,
    session: Session = Depends(get_session),
    _: None = Depends(require_admin),
):
    return register_hospital(data, session)
