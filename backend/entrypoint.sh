#!/bin/bash
set -e

echo "Starting Agent Prototype Backend..."

# Wait for database to be ready
echo "Waiting for PostgreSQL..."
while ! python -c "
import asyncio
from sqlalchemy import text
from app.core.database import engine

async def check():
    async with engine.begin() as conn:
        await conn.execute(text('SELECT 1'))
        print('Database is ready!')

asyncio.run(check())
" 2>/dev/null; do
    echo "Database not ready, waiting..."
    sleep 2
done

# Run database migrations
echo "Running database migrations..."
alembic upgrade head || {
    echo "Migration failed, attempting to create tables directly..."
    python -c "
import asyncio
from app.core.database import engine, Base
async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
asyncio.run(init())
"
}

echo "Starting application server..."
exec "$@"
