import os

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from jose import JWTError, jwt
from sqlmodel import Session, select

from database import get_session
from models.users import UserRole, Users
from utils.file_storage import get_file_path

router = APIRouter(prefix="/medias", tags=["medias"])

PUBLIC_SUBFOLDERS = ("profile_pics", "hospital_images")


@router.get("/{user_id}/{subfolder}/{filename}")
def serve_file(
    user_id: int,
    subfolder: str,
    filename: str,
    request: Request,
    session: Session = Depends(get_session),
):

    if subfolder in PUBLIC_SUBFOLDERS:
        path = get_file_path(user_id, subfolder, filename)
        return FileResponse(path)

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="You are not the one who you think you are..."
        )

    token = auth_header.split(" ", 1)[1]
    try:
        payload = jwt.decode(
            token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")]
        )
        user_id_int = int(payload.get("sub"))
    except (JWTError, TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired token..")

    current_user = session.exec(select(Users).where(Users.id == user_id_int)).first()
    if current_user is None or not current_user.is_active:
        raise HTTPException(
            status_code=401, detail="user is not found or is InActive.."
        )

    elif current_user.role != UserRole.admin and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authenticated")

    path = get_file_path(user_id, subfolder, filename)
    return FileResponse(path)
