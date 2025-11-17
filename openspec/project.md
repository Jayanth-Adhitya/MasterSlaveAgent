# Project Context

## Purpose  
The project is a prototype proof-of-concept intended to validate a multi-tenant conversational assistant platform where a single core LLM serves many users/teams/tenants. The goal is to demonstrate that one model can handle different user contexts (e.g., restaurant employees, property tenants) with personalized memory, role-based workflows, and notifications. Ultimately this will inform feasibility, architecture, and cost for a full production version.

## Tech Stack  
- Backend: Python (FastAPI) for the API server + worker processes  
- Message broker / queue: Redis Streams (or RabbitMQ)  
- Data storage: PostgreSQL (relational) + pgvector (vector embeddings)  
- LLM orchestration: A master agent service calling an LLM (local or cloud)  
- Mobile app: React Native (or Ionic) with WebSocket for realtime + push notifications  
- Frontend/admin UI: React + Shadcn/UI (for prototype)  
- Authentication: JWT with refresh tokens, simple role-based access  
- Deployment: Prototype on a Linux VPS, use PM2 or systemd for process management

## Project Conventions

### Code Style  
- Use **snake_case** for Python variables and functions; **PascalCase** for Python class names  
- Type hints on Python functions  
- Use **black** (line length 88) and **flake8** for linting  
- For mobile/React code: PascalCase for components, camelCase for props/hooks  
- Commit messages: `scope: short description` (e.g. `worker: initial queue listener`)  
- This is a prototype: minimal documentation for now, increase in future phases

### Architecture Patterns  
- **Multi-tenant routing**: messages routed by tenant_id → user/team → queue  
- **Agent model**: slave agents (scoped to user/team/tenant) + master agent (LLM orchestration)  
- **RAG (Retrieval-Augmented Generation)**: vector store pulls context per tenant/scope; feed into prompts  
- **Action pattern**: LLM returns structured JSON actions (notify, create_task), which slave agents validate & execute  
- **Event/queue system**: all messages from mobile go into queue; workers process asynchronously  
- **Simplified model for prototype**: lesser error-handling, fewer abstractions; focus on flow

### Testing Strategy  
- Unit tests using pytest for core logic (routing, memory retrieval)  
- Integration test: “message → queue → worker → stub LLM → action flow”  
- End-to-end test: mobile sends message, other user receives notification (can be manual for prototype)  
- For prototype: minimal coverage target (e.g., 50-60%) with view to increase later  
- Load testing optional at prototype stage

### Git Workflow  
- `main` branch as baseline (prototype production)  
- Feature branches: `feature/<short-desc>`  
- Pull requests for major features (at least one reviewer)  
- Squash merges to keep history clean  
- Lightweight branching: no formal release/hotfix flow yet, unless moving toward production

## Domain Context  
- Tenants = organisations (e.g., restaurant, property owner)  
- Users/teams: Each tenant may have users with roles (employee, manager, resident)  
- Properties: For property-management use case these are entities with address, schedules, services  
- Memory: conversations, tasks, schedules, service logs form context  
- Business logic: e.g., “delivery arriving tomorrow”, “cleaning scheduled”, “tenant raised a request” → system identifies correct recipient, creates notification/task  
- Prototype assumption: simple rules, limited complexity; future versions may enrich logic

## Important Constraints  
- Data isolation: each tenant’s data must not leak to others, even in prototype  
- Responsiveness: notifications should work in near-real-time (push + websocket)  
- Scalability: prototype may handle limited tenants/users (e.g., one tenant, few users)  
- Privacy/security: basic protections (authentication, tenant isolation) required for prototype; full enterprise-grade security reserved for later  
- Offline/online: mobile app should handle intermittent connectivity (basic retry)  
- Role/approval: critical actions may need manual approval in prototype (rather than fully autonomous automation)

## External Dependencies  
- LLM service or local model instance  
- Vector store: pgvector or similar  
- Push notification service: FCM/APNs  
- Redis (or equivalent) message broker  
- Authentication (custom or simple OAuth/JWT)  
- Basic analytics or monitoring service (optional for prototype)  
