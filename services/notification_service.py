from fastapi import HTTPException
from sqlmodel import Session, select

from models.hospitals import Hospitals
from models.notifications import Notifications, NotificationType
from models.users import UserRole, Users
from utils.ws_manager import manager


def _broadcast(notification: Notifications):
    payload = {
        "id": notification.id,
        "type": notification.type.value,
        "title": notification.title,
        "message": notification.message,
        "related_id": notification.related_id,
        "related_type": notification.related_type,
        "is_read": notification.is_read,
        "created_at": notification.created_at.isoformat(),
    }
    manager.schedule_send(notification.user_id, payload)


def create_notification(
    session: Session,
    user_id: int,
    type: NotificationType,
    title: str,
    message: str,
    related_id: int | None = None,
    related_type: str | None = None,
):
    notification = Notifications(
        user_id=user_id,
        type=type,
        title=title,
        message=message,
        related_id=related_id,
        related_type=related_type,
    )
    session.add(notification)
    session.commit()
    session.refresh(notification)

    _broadcast(notification)

    return notification


def notify_hospital(
    session: Session,
    hospital_id: int | None,
    type: NotificationType,
    title: str,
    message: str,
    related_id: int | None = None,
    related_type: str | None = None,
):
    if hospital_id is None:
        return None
    hospital = session.get(Hospitals, hospital_id)
    if hospital is None:
        return None
    return create_notification(
        session,
        hospital.user_id,
        type,
        title,
        message,
        related_id=related_id,
        related_type=related_type,
    )


def notify_role(
    session: Session,
    role: UserRole,
    type: NotificationType,
    title: str,
    message: str,
    related_id: int | None = None,
    related_type: str | None = None,
) -> list[Notifications]:
    users = session.exec(
        select(Users).where(Users.role == role, Users.is_active == True)
    ).all()
    notifications = []

    for user in users:
        if user.id is None:
            continue
        notification = Notifications(
            user_id=user.id,
            type=type,
            title=title,
            message=message,
            related_id=related_id,
            related_type=related_type,
        )
        session.add(notification)
        notifications.append(notification)

    session.commit()
    for n in notifications:
        session.refresh(n)
        _broadcast(n)

    return notifications


def list_my_notifications(session: Session, user_id: int, unread_only: bool = False):
    query = select(Notifications).where(Notifications.user_id == user_id)
    if unread_only:
        query = query.where(Notifications.is_read == False)
    query = query.order_by(Notifications.created_at.desc())
    return session.exec(query).all()


def unread_count(session: Session, user_id: int) -> int:
    results = session.exec(
        select(Notifications).where(
            Notifications.user_id == user_id, Notifications.is_read == False
        )
    ).all()

    sigma = len(results)
    return sigma


def mark_as_read(session: Session, notification_id: int, user_id: int) -> Notifications:
    notification = session.get(Notifications, notification_id)
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found..")
    if notification.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not your notification.")

    notification.is_read = True
    session.add(notification)
    session.commit()
    session.refresh(notification)

    return notification


def mark_all_read(session: Session, user_id: int) -> int:
    notifications = session.exec(
        select(Notifications).where(
            Notifications.user_id == user_id, Notifications.is_read == False
        )
    ).all()

    for n in notifications:
        n.is_read = True
        session.add(n)

    session.commit()
    return len(notifications)
