"""Worker process for consuming and processing messages."""
import asyncio
import json
import logging
import signal
from redis import asyncio as aioredis
from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import async_session_maker
from app.services.redis_service import get_redis, publish_response
from app.agents.registry import get_or_create_agent
from app.models import Message, Tenant

logger = logging.getLogger(__name__)
settings = get_settings()

CONSUMER_GROUP = "message_workers"
CONSUMER_NAME = "worker_1"


class MessageWorker:
    def __init__(self):
        self.running = False
        self.redis: aioredis.Redis | None = None

    async def start(self):
        """Start the worker process."""
        self.running = True
        self.redis = await get_redis()

        # Get all tenant streams to consume
        async with async_session_maker() as session:
            result = await session.execute(select(Tenant.id))
            tenant_ids = [row[0] for row in result.fetchall()]

        if not tenant_ids:
            logger.warning("No tenants found, worker waiting...")
            tenant_ids = [1]  # Default

        streams = {f"messages:{tid}": ">" for tid in tenant_ids}

        # Create consumer groups if they don't exist
        for stream_key in streams.keys():
            try:
                await self.redis.xgroup_create(
                    stream_key, CONSUMER_GROUP, id="0", mkstream=True
                )
                logger.info(f"Created consumer group for {stream_key}")
            except Exception as e:
                if "BUSYGROUP" not in str(e):
                    logger.error(f"Error creating consumer group: {e}")

        logger.info(f"Worker started, consuming from streams: {list(streams.keys())}")

        while self.running:
            try:
                # Read from streams
                messages = await self.redis.xreadgroup(
                    CONSUMER_GROUP,
                    CONSUMER_NAME,
                    streams=streams,
                    count=1,
                    block=5000,  # 5 second timeout
                )

                if messages:
                    for stream_key, stream_messages in messages:
                        for message_id, message_data in stream_messages:
                            await self.process_message(
                                stream_key, message_id, message_data
                            )
                            # Acknowledge message
                            await self.redis.xack(
                                stream_key, CONSUMER_GROUP, message_id
                            )

            except asyncio.CancelledError:
                logger.info("Worker cancelled, shutting down...")
                break
            except Exception as e:
                logger.error(f"Worker error: {e}")
                await asyncio.sleep(1)

        logger.info("Worker stopped")

    async def stop(self):
        """Stop the worker gracefully."""
        self.running = False

    async def process_message(
        self, stream_key: str, message_id: str, message_data: dict
    ):
        """Process a single message from the queue."""
        logger.info(f"Processing message {message_id} from {stream_key}")

        try:
            tenant_id = int(message_data["tenant_id"])
            user_id = int(message_data["user_id"])
            session_id = message_data["session_id"]
            content = message_data["content"]
            user_info = json.loads(message_data["user_info"])

            async with async_session_maker() as session:
                # Save user message to database
                user_message = Message(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    session_id=session_id,
                    role="user",
                    content=content,
                )
                session.add(user_message)
                await session.flush()

                # Get or create agent for tenant
                agent = await get_or_create_agent(tenant_id, session)

                # Process message through agent
                llm_response = await agent.process_message(
                    session, user_id, user_info, session_id, content
                )

                # Execute any actions
                if llm_response.actions:
                    await agent.execute_actions(session, user_id, llm_response.actions)

                # Save assistant message to database
                assistant_message = Message(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    session_id=session_id,
                    role="assistant",
                    content=llm_response.response,
                )
                session.add(assistant_message)
                await session.commit()

                # Publish response to user's channel
                response_channel = f"response:{tenant_id}:{user_id}:{session_id}"
                await publish_response(
                    response_channel,
                    {
                        "type": "message",
                        "content": llm_response.response,
                        "session_id": session_id,
                        "actions_taken": len(llm_response.actions),
                    },
                )

                logger.info(
                    f"Processed message {message_id}, actions: {len(llm_response.actions)}"
                )

        except Exception as e:
            logger.error(f"Error processing message {message_id}: {e}")
            # Publish error to user
            try:
                response_channel = f"response:{message_data.get('tenant_id')}:{message_data.get('user_id')}:{message_data.get('session_id')}"
                await publish_response(
                    response_channel,
                    {
                        "type": "error",
                        "content": "Sorry, I encountered an error processing your message.",
                        "session_id": message_data.get("session_id"),
                    },
                )
            except Exception:
                pass


async def run_worker():
    """Run the message worker."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    worker = MessageWorker()

    # Handle shutdown signals
    loop = asyncio.get_event_loop()

    def shutdown_handler():
        logger.info("Received shutdown signal")
        asyncio.create_task(worker.stop())

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, shutdown_handler)
        except NotImplementedError:
            # Windows doesn't support add_signal_handler
            pass

    await worker.start()


if __name__ == "__main__":
    asyncio.run(run_worker())
