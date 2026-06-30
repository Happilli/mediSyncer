from fastapi import APIRouter, Depends
from sqlmodel import Session

from database import get_session
from schemas.hospital import HospitalOut, HospitalRegister
from services.hospital_service import get_hospital, list_hospitals, register_hospital
from utils.dependencies import require_admin

router = APIRouter(prefix="/hospitals", tags=["hospitals"])


@router.post("/register", status_code=201)
def register_new_hospital(
    data: HospitalRegister,
    session: Session = Depends(get_session),
    _: None = Depends(require_admin),
):
    return register_hospital(data, session)


@router.get("/", response_model=list[HospitalOut])
def get_hospitals(search: str | None = None, session: Session = Depends(get_session)):
    return list_hospitals(session, search)


@router.get("/{hospital_id}", response_model=HospitalOut)
def get_hospital_detail(hospital_id: int, session: Session = Depends(get_session)):
    return get_hospital(hospital_id, session)
