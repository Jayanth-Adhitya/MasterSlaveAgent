"""Redis service for message queue operations."""
import json
import logging
from redis import asyncio as aioredis
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Global Redis connection
_redis_client: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    """Get or create Redis connection."""
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            settings.redis_url, encoding="utf-8", decode_responses=True
        )
    return _redis_client


async def close_redis():
    """Close Redis connection."""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None


async def enqueue_message(
    tenant_id: int,
    user_id: int,
    session_id: str,
    content: str,
    user_info: dict,
) -> str:
    """Add message to Redis stream for processing."""
    redis = await get_redis()
    stream_key = f"messages:{tenant_id}"

    message_data = {
        "tenant_id": str(tenant_id),
        "user_id": str(user_id),
        "session_id": session_id,
        "content": content,
        "user_info": json.dumps(user_info),
    }

    message_id = await redis.xadd(stream_key, message_data)
    logger.info(f"Enqueued message {message_id} to stream {stream_key}")
    return message_id


async def publish_response(channel: str, data: dict):
    """Publish response to Redis pub/sub channel."""
    redis = await get_redis()
    await redis.publish(channel, json.dumps(data))
    logger.debug(f"Published response to channel {channel}")
