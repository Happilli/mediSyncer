from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from models.users import UserRole, Users
from utils.dependencies import get_current_user
from utils.file_storage import get_file_path

router = APIRouter(prefix="/medias", tags=["medias"])


@router.get("/{user_id}/{subfolder}/{filename}")
def serve_file(
    user_id: int,
    subfolder: str,
    filename: str,
    current_user: Users = Depends(get_current_user),
):

    if subfolder == ("profile_pics", "hospital_images"):
        pass

    elif current_user.role != UserRole.admin and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authenticated")

    path = get_file_path(user_id, subfolder, filename)
    return FileResponse(path)
