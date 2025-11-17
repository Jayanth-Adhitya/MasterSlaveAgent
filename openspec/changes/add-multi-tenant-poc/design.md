## Context
This is a greenfield proof-of-concept to validate multi-tenant conversational AI with Slave Agent architecture. Each tenant (e.g., restaurant, property) has its own Slave Agent that holds business context and can coordinate actions between users. The PoC must demonstrate tenant data isolation, business context awareness via RAG, per-user memory, LLM-driven actions (like notifications), and cross-user coordination. Target: 2 tenants (restaurant + property), 2-3 users per tenant, conversation with actions.

## Goals / Non-Goals
- Goals:
  - Demonstrate tenant isolation (Tenant A cannot see Tenant B's data)
  - Slave Agent per tenant with loaded business context
  - RAG retrieval of tenant-specific knowledge (schedules, roster, rules)
  - Route messages to correct Slave Agent based on tenant_id
  - Maintain conversation history per user session
  - LLM returns structured actions (notify other users, log events)
  - Cross-user notifications within same tenant
  - Integrate LangChain with Gemini for LLM responses
  - Provide web UI for testing conversations and viewing notifications

- Non-Goals:
  - Production-grade security (basic JWT only)
  - Mobile app (web UI simulates mobile experience)
  - Push notifications (inbox-style notifications sufficient)
  - High availability / horizontal scaling
  - Complex approval workflows

## Decisions

### 1. Multi-Tenant Data Isolation
- **Decision**: Shared database, shared schema with tenant_id column
- **Why**: Simplest for PoC, sufficient isolation with proper filtering, easy to implement
- **Alternative considered**: Separate schemas per tenant - more complex migrations, overkill for PoC

### 2. Message Queue
- **Decision**: Redis Streams with consumer groups
- **Why**: Native async support, message persistence, scales with `aioredis`, already in tech stack
- **Alternative considered**: RabbitMQ - more setup overhead, Redis simpler for PoC

### 3. LLM Integration
- **Decision**: LangChain with ChatGoogleGenerativeAI (Gemini)
- **Why**: User requirement, good Python integration, free tier available, built-in memory management
- **Alternative considered**: Direct Gemini API - less features, no memory abstraction

### 4. Conversation Memory
- **Decision**: In-memory dictionary keyed by `{tenant_id}:{user_id}:{session_id}`
- **Why**: Simplest for PoC, zero external dependencies for memory storage
- **Alternative considered**: RedisChatMessageHistory - more setup, defer to production

### 5. Slave Agent Architecture
- **Decision**: On-demand instantiation, stored in in-memory dictionary keyed by tenant_id
- **Why**: Simplest for PoC, no persistent process management, scales with tenants
- **Alternative considered**: Persistent processes per tenant - complex lifecycle management, overkill for PoC

### 6. Tenant Context (RAG)
- **Decision**: pgvector for embedding tenant knowledge (schedules, roster, rules), retrieved per message
- **Why**: User requirement, enables context-aware responses, built into PostgreSQL
- **Alternative considered**: In-memory JSON - doesn't scale, no semantic search

### 7. Action System
- **Decision**: LLM returns structured JSON with action type and parameters, Slave Agent executes
- **Why**: Predictable, parseable, easy to validate and execute
- **Alternative considered**: Free-form text parsing - error-prone, harder to execute

### 8. Authentication
- **Decision**: JWT with tenant_id and user_id in claims, extracted via FastAPI dependency
- **Why**: Stateless, standard pattern, carries tenant context
- **Alternative considered**: Session-based - requires server state, more complex

### 9. Worker Pattern
- **Decision**: Single async worker process consuming Redis Streams
- **Why**: Sufficient for PoC load, demonstrates async pattern
- **Alternative considered**: Celery - heavyweight, unnecessary complexity

## Architecture Flow

```
[Browser UI - simulates mobile]
    ↓ (REST + WebSocket)
[FastAPI API]
    ↓ (JWT auth extracts tenant_id, user_id)
[Redis Streams Queue]
    ↓ (keyed by tenant_id)
[Async Worker]
    ↓ (routes message to Slave Agent)
[Slave Agent (per tenant)]
    ├─ Loads tenant context via RAG (pgvector)
    ├─ Maintains user conversation memory
    └─ Calls LLM with full context
         ↓
    [LangChain + Gemini]
         ↓
    Returns: {response: "...", actions: [{type: "notify", user_id: X, message: "..."}]}
         ↓
[Slave Agent executes actions]
    ├─ Store notification in DB
    ├─ Log event
    └─ Other actions...
         ↓
[PostgreSQL] (stores messages + notifications)
         ↓
[Response back to user via WebSocket]
[Target user sees notification in their inbox]
```

## Database Schema

```sql
-- Tenants (restaurant, property, etc.)
tenants (id, name, type, created_at)

-- Users (belongs to tenant)
users (id, tenant_id, email, password_hash, role, name, created_at)

-- Messages (conversation history)
messages (id, tenant_id, user_id, session_id, role, content, created_at)

-- Notifications (cross-user alerts)
notifications (id, tenant_id, from_user_id, to_user_id, message, read, created_at)

-- Tenant Knowledge (for RAG)
tenant_knowledge (id, tenant_id, content, embedding vector(1536), category, created_at)
```

## Risks / Trade-offs
- **In-memory storage loss on restart** → Acceptable for PoC, persist to DB for recovery
- **Single worker bottleneck** → Sufficient for PoC scale (10-20 concurrent users)
- **No rate limiting** → Add if Gemini API limits become issue
- **Basic JWT security** → No refresh tokens, short expiry acceptable for PoC

## Migration Plan
Not applicable - greenfield project.

## Open Questions
- Gemini API key provisioning: use environment variable or config file?
- WebSocket vs SSE for real-time updates: WebSocket preferred for bidirectional
- Session expiry: how long to keep conversation memory active?
