import os
import uuid

from fastapi import HTTPException, UploadFile

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024

STORAGE_ROOT = "serve"


async def save_upload_file(file: UploadFile, subfolder: str) -> dict:
    if file.filename is None:
        raise HTTPException(status_code=400, detail="No filename provided.")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Max 5MB.")

    filename = f"{uuid.uuid4().hex}{ext}"
    folder_path = os.path.join(STORAGE_ROOT, subfolder)
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, filename)

    with open(file_path, "wb") as f:
        f.write(contents)

    return {
        "filename": filename,
        "url": f"/api/v1/uploads/serve/{subfolder}/{filename}",
    }


def get_file_path(subfolder: str, filename: str) -> str:
    path = os.path.join(STORAGE_ROOT, subfolder, filename)
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="File not found.")
    return path
