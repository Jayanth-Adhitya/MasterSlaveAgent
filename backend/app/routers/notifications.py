"""Notification endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.auth import TokenData
from app.schemas.notification import NotificationResponse
from app.models import Notification, User

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationResponse])
async def get_notifications(
    current_user: TokenData = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Get all notifications for current user."""
    result = await session.execute(
        select(Notification, User.name.label("from_user_name"))
        .join(User, Notification.from_user_id == User.id)
        .where(
            Notification.tenant_id == current_user.tenant_id,
            Notification.to_user_id == current_user.user_id,
        )
        .order_by(Notification.created_at.desc())
    )
    rows = result.all()

    notifications = []
    for notification, from_user_name in rows:
        notif_dict = {
            "id": notification.id,
            "tenant_id": notification.tenant_id,
            "from_user_id": notification.from_user_id,
            "from_user_name": from_user_name,
            "to_user_id": notification.to_user_id,
            "message": notification.message,
            "read": notification.read,
            "created_at": notification.created_at,
        }
        notifications.append(NotificationResponse(**notif_dict))

    return notifications


@router.get("/unread/count")
async def get_unread_count(
    current_user: TokenData = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Get count of unread notifications."""
    from sqlalchemy import func

    result = await session.execute(
        select(func.count(Notification.id)).where(
            Notification.tenant_id == current_user.tenant_id,
            Notification.to_user_id == current_user.user_id,
            Notification.read == False,
        )
    )
    count = result.scalar()
    return {"unread_count": count}


@router.patch("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user: TokenData = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Mark a notification as read."""
    # Verify notification belongs to user
    notification = await session.get(Notification, notification_id)

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found"
        )

    if (
        notification.to_user_id != current_user.user_id
        or notification.tenant_id != current_user.tenant_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this notification",
        )

    notification.read = True
    await session.commit()

    return {"status": "ok", "id": notification_id}
