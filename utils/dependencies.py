import os

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlmodel import Session, select

from database import get_session
from models.users import UserRole, Users

bearer = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    session: Session = Depends(get_session),
) -> Users:
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            os.getenv("SECRET_KEY"),  # type: ignore
            algorithms=[os.getenv("ALGORITHM")],  # type: ignore
        )
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        try:
            user_id_int = int(user_id)
        except (TypeError, ValueError):
            raise HTTPException(status_code=401, detail="Invalid token")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = session.exec(select(Users).where(Users.id == user_id_int)).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found...")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is not active...")

    return user


def require_admin(current_user: Users = Depends(get_current_user)) -> Users:
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admin access required..")
    return current_user


def require_doctor(current_user: Users = Depends(get_current_user)) -> Users:
    if current_user.role != UserRole.doctor:
        raise HTTPException(status_code=403, detail="Doctor access required..")
    return current_user


def require_patient(current_user: Users = Depends(get_current_user)) -> Users:
    if current_user.role != UserRole.patient:
        raise HTTPException(status_code=403, detail="Patient access required..")
    return current_user


def require_hospital(current_user: Users = Depends(get_current_user)) -> Users:
    if current_user.role != UserRole.hospital:
        raise HTTPException(status_code=403, detail="hospital access required..")
    return current_user
