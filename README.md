# Multi-Tenant Agent Prototype

A proof-of-concept for a multi-tenant conversational AI platform where one LLM (Gemini) serves multiple tenants with isolated contexts, per-user memory, and cross-user notifications.

## Architecture

- **FastAPI Backend** with async SQLAlchemy
- **Redis Streams** for message queue
- **PostgreSQL + pgvector** for data and embeddings
- **LangChain + Gemini** for LLM orchestration
- **Slave Agent** per tenant with business context
- **React Web UI** for chat interface

## Quick Start

### 1. Prerequisites

- Python 3.10+
- Node.js 18+
- Docker & Docker Compose
- Google Gemini API Key

### 2. Setup Environment

```bash
# Copy environment file
cp .env.example .env

# Edit .env and add your Gemini API key
# GOOGLE_API_KEY=your-key-here
```

### 3. Start Infrastructure

```bash
# Start PostgreSQL and Redis
docker-compose up -d
```

### 4. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -e .

# Wait for database to be ready, then seed data
cd ..
python scripts/seed_data.py
```

### 5. Start Backend Services

Terminal 1 - API Server:
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 - Worker Process:
```bash
cd backend
python -m app.services.worker
```

### 6. Setup Frontend

```bash
cd frontend
npm install
npm run dev
```

### 7. Access the Application

- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs

## Test Accounts

**Restaurant Tenant (Mario's Pizza):**
- mario@pizza.com (manager)
- luigi@pizza.com (employee)
- peach@pizza.com (employee)

**Property Tenant (Oak Street Property):**
- john@oakst.com (tenant)
- jane@oakst.com (tenant)
- bob@oakst.com (tenant)

Password for all: `password123`

## Demo Scenarios

### Restaurant - Cross-User Notification

1. Login as `luigi@pizza.com`
2. Send: "There's a delivery arriving tomorrow at 10am, but I'm off work"
3. The LLM will identify who is working and notify them
4. Login as `peach@pizza.com` (or whoever was notified)
5. Check the notifications panel

### Property - RAG Context Query

1. Login as `john@oakst.com`
2. Send: "When is the next cleaning scheduled?"
3. The LLM retrieves from tenant knowledge base and responds with schedule

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── agents/          # Slave Agent implementation
│   │   ├── core/            # Config, database, security
│   │   ├── models/          # SQLAlchemy models
│   │   ├── routers/         # API endpoints
│   │   ├── schemas/         # Pydantic schemas
│   │   └── services/        # Redis, worker
│   └── alembic/             # Database migrations
├── frontend/
│   └── src/
│       ├── components/      # React components
│       ├── hooks/           # Custom hooks
│       └── services/        # API client
├── openspec/                # Specifications
├── scripts/                 # Setup scripts
└── docker-compose.yml       # Infrastructure
```

## Key Features

- **Tenant Isolation**: Each tenant's data is completely isolated
- **Slave Agent Architecture**: Per-tenant agent with business context
- **RAG Context Loading**: Agent knows business schedules, roster, rules
- **Structured Actions**: LLM returns JSON with actions (notify_user, etc.)
- **Real-time Updates**: WebSocket for instant message delivery
- **Notification System**: Cross-user notifications within tenant

## Known Limitations (PoC)

- In-memory conversation storage (lost on restart)
- No pgvector embeddings (using simple text retrieval)
- Basic JWT auth (no refresh tokens)
- Single worker process
- No rate limiting

## Next Steps

- Add pgvector embeddings for semantic search
- Implement persistent conversation memory
- Add more action types (create_task, log_event)
- Mobile app with push notifications
- Production security enhancements
