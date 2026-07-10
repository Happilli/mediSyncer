from fastapi import APIRouter, Depends
from sqlmodel import Session

from database import get_session
from models.users import Users
from schemas.admin import VerificationFunnelOut
from services.admin_stats_service import get_verification_funnel
from utils.dependencies import require_admin

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats/verification-funnel", response_model=VerificationFunnelOut)
def verification_funnel(
    session: Session = Depends(get_session),
    _: Users = Depends(require_admin),
):
    return get_verification_funnel(session)
