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

# Enable pgvector extension (required for vector type)
echo "Enabling pgvector extension..."
python -c "
import asyncio
from sqlalchemy import text
from app.core.database import engine

async def enable_vector():
    async with engine.begin() as conn:
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS vector'))
    print('pgvector extension enabled')

asyncio.run(enable_vector())
"

# Create tables if they don't exist (always run this for safety)
echo "Ensuring database tables exist..."
python -c "
import asyncio
from app.core.database import engine, Base
# Import all models to register them
from app.models import Tenant, User, Message, Notification, TenantKnowledge

async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print('Tables created/verified successfully')

asyncio.run(init())
"

# Try to run Alembic migrations (may fail if no migrations exist, that's OK)
echo "Running database migrations..."
alembic upgrade head || echo "No migrations to apply (or Alembic not configured)"

echo "Starting application server..."
exec "$@"
