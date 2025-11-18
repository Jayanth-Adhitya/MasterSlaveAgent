"""WebSocket endpoint for real-time updates."""
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from redis import asyncio as aioredis

from app.core.security import decode_access_token
from app.services.redis_service import get_redis

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    """WebSocket endpoint for real-time message updates."""
    try:
        # Authenticate token
        token_data = decode_access_token(token)
        if not token_data:
            logger.warning(f"Invalid token in WebSocket connection")
            await websocket.close(code=4001, reason="Invalid token")
            return

        await websocket.accept()
        logger.info(
            f"WebSocket connected for user {token_data.user_id} tenant {token_data.tenant_id}"
        )
    except Exception as e:
        logger.error(f"Error during WebSocket handshake: {e}")
        await websocket.close(code=4002, reason=str(e))
        return

    redis = await get_redis()
    pubsub = redis.pubsub()

    # Subscribe to user's response channels
    # We'll use a pattern to catch all sessions for this user
    channel_pattern = f"response:{token_data.tenant_id}:{token_data.user_id}:*"

    try:
        await pubsub.psubscribe(channel_pattern)
        logger.info(f"Subscribed to pattern {channel_pattern}")

        # Send initial connection success
        await websocket.send_json(
            {
                "type": "connected",
                "user_id": token_data.user_id,
                "tenant_id": token_data.tenant_id,
            }
        )

        # Listen for messages
        async for message in pubsub.listen():
            if message["type"] == "pmessage":
                data = json.loads(message["data"])
                await websocket.send_json(data)
                logger.debug(f"Sent message to user {token_data.user_id}")

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user {token_data.user_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await pubsub.punsubscribe(channel_pattern)
        await pubsub.close()
