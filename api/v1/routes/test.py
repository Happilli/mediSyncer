from fastapi import APIRouter, Depends

from models.users import Users
from utils.dependencies import (
    get_current_user,
    require_admin,
    require_hospital,
    require_patient,
    required_verified_doctor,
)

router = APIRouter(prefix="/test", tags=["test"])


@router.get("/me")
def whoami(current_user: Users = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active,
    }


@router.get("/patient")
def patient_only(current_user: Users = Depends(require_patient)):
    return {"message": "patient access ok", "user": current_user.email}


@router.get("/doctor")
def doctor_only(current_user: Users = Depends(required_verified_doctor)):
    return {"message": "doctor access ok", "user": current_user.email}


@router.get("/hospital")
def hospital_only(current_user: Users = Depends(require_hospital)):
    return {"message": "hospital access ok", "user": current_user.email}


@router.get("/admin")
def admin_only(current_user: Users = Depends(require_admin)):
    return {"message": "admin access ok", "user": current_user.email}
