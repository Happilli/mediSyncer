from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from database import get_session
from models.doctors import Doctors
from models.patients import Patients
from models.users import UserRole, Users
from utils.dependencies import get_current_user
from utils.file_storage import get_file_path, save_upload_file

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("/profile-pic")
async def upload_profile_pic(
    file: UploadFile = File(...),
    current_user: Users = Depends(get_current_user),
):
    return await save_upload_file(file, "profile_pics")


@router.post("/license-photo")
async def upload_license_photo(
    file: UploadFile = File(...),
    current_user: Users = Depends(get_current_user),
):
    return await save_upload_file(file, "license_photos")


@router.post("/citizenship-photo")
async def upload_citizenship_photo(
    file: UploadFile = File(...),
    current_user: Users = Depends(get_current_user),
):
    return await save_upload_file(file, "citizenship_photos")


@router.get("/serve/{subfolder}/{filename}")
def serve_file(
    subfolder: str,
    filename: str,
    session: Session = Depends(get_session),
    current_user: Users = Depends(get_current_user),
):
    url_suffix = f"/api/v1/uploads/serve/{subfolder}/{filename}"

    if subfolder == "profile_pics":
        pass

    elif subfolder == "citizenship_photos":
        if current_user.role == UserRole.admin:
            pass
        else:
            patient = session.exec(
                select(Patients).where(
                    Patients.user_id == current_user.id,
                    Patients.citizenship_photo_url == url_suffix,
                )
            ).first()
            if patient is None:
                raise HTTPException(status_code=403, detail="Not authorized.")
    elif subfolder == "license_photos":
        if current_user.role == UserRole.admin:
            pass
        else:
            doctor = session.exec(
                select(Doctors).where(
                    Doctors.user_id == current_user.id,
                    Doctors.license_photo_url == url_suffix,
                )
            ).first()
            if doctor is None:
                raise HTTPException(status_code=403, detail="Not authorized.")
    else:
        raise HTTPException(status_code=404, detail="Unknown resource type.")

    path = get_file_path(subfolder, filename)
    return FileResponse(path)
