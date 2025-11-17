"""Message endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.auth import TokenData
from app.schemas.message import MessageCreate, MessageResponse
from app.services.redis_service import enqueue_message
from app.models import Message

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def send_message(
    message: MessageCreate,
    current_user: TokenData = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Send a message to be processed by the agent."""
    user_info = {
        "id": current_user.user_id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
    }

    # Enqueue message for processing
    message_id = await enqueue_message(
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
        session_id=message.session_id,
        content=message.content,
        user_info=user_info,
    )

    return {
        "status": "queued",
        "message_id": message_id,
        "session_id": message.session_id,
    }


@router.get("", response_model=list[MessageResponse])
async def get_messages(
    session_id: str,
    current_user: TokenData = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Get conversation history for a session."""
    result = await session.execute(
        select(Message)
        .where(
            Message.tenant_id == current_user.tenant_id,
            Message.user_id == current_user.user_id,
            Message.session_id == session_id,
        )
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()
    return messages
