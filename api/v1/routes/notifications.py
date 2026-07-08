from fastapi import APIRouter, Depends
from sqlmodel import Session

from database import get_session
from models.users import Users
from schemas.notification import NotificationOut
from services.notification_service import (
    list_my_notifications,
    mark_all_read,
    mark_as_read,
    unread_count,
)
from utils.dependencies import get_current_user

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/me", response_model=list[NotificationOut])
def my_notifications(
    unread_only: bool = False,
    session: Session = Depends(get_session),
    current_user: Users = Depends(get_current_user),
):
    return list_my_notifications(session, current_user.id, unread_only)


@router.get("/unread-count")
def my_unread_count(
    session: Session = Depends(get_session),
    current_user: Users = Depends(get_current_user),
):
    return {"unread_count": unread_count(session, current_user.id)}


@router.patch("/{notification_id}/read", response_model=NotificationOut)
def read_notification(
    notification_id: int,
    session: Session = Depends(get_session),
    current_user: Users = Depends(get_current_user),
):
    return mark_as_read(session, notification_id, current_user.id)


@router.patch("/read-all")
def read_all_notifications(
    session: Session = Depends(get_session),
    current_user: Users = Depends(get_current_user),
):
    count = mark_all_read(session, current_user.id)
    return {"message": f"{count} notifications marked as read."}
