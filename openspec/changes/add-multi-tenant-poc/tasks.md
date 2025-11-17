## 1. Project Setup
- [ ] 1.1 Initialize Python project with pyproject.toml (FastAPI, LangChain, Redis, SQLAlchemy, pgvector)
- [ ] 1.2 Create project directory structure (backend/, frontend/, docker/)
- [ ] 1.3 Set up Docker Compose for Redis, PostgreSQL with pgvector extension
- [ ] 1.4 Create .env.example with required environment variables (GEMINI_API_KEY, DB_URL, etc.)

## 2. Database Layer
- [ ] 2.1 Define SQLAlchemy models (Tenant, User, Message, Notification, TenantKnowledge)
- [ ] 2.2 Create Alembic migrations for initial schema including pgvector
- [ ] 2.3 Add seed data script for 2 test tenants (restaurant, property) with users
- [ ] 2.4 Seed tenant knowledge (schedules, roster, rules) with embeddings
- [ ] 2.5 Implement tenant-aware query helpers

## 3. Authentication
- [ ] 3.1 Implement JWT token generation with tenant_id, user_id, role claims
- [ ] 3.2 Create FastAPI dependency for extracting tenant context from JWT
- [ ] 3.3 Add login endpoint (email/password → JWT)
- [ ] 3.4 Add basic password hashing with bcrypt

## 4. Message Queue
- [ ] 4.1 Set up Redis connection with aioredis
- [ ] 4.2 Create message producer (API → Redis Stream)
- [ ] 4.3 Implement stream key pattern: `messages:{tenant_id}`
- [ ] 4.4 Add message schema validation (Pydantic)

## 5. Slave Agent Implementation
- [ ] 5.1 Create SlaveAgent class with tenant_id and context
- [ ] 5.2 Implement agent registry (in-memory dict) for on-demand instantiation
- [ ] 5.3 Add RAG context loading via pgvector similarity search
- [ ] 5.4 Implement per-user conversation memory within agent
- [ ] 5.5 Create system prompt template with tenant context placeholder
- [ ] 5.6 Configure LangChain with ChatGoogleGenerativeAI (Gemini)

## 6. Action System
- [ ] 6.1 Define action schema (notify_user, log_event) with Pydantic
- [ ] 6.2 Implement LLM output parser for structured JSON actions
- [ ] 6.3 Create action executor in SlaveAgent (dispatch to handlers)
- [ ] 6.4 Implement notify_user action (insert into notifications table)
- [ ] 6.5 Handle LLM errors gracefully (timeouts, rate limits, malformed output)

## 7. Worker Process
- [ ] 7.1 Create async worker consuming Redis Streams with consumer group
- [ ] 7.2 Implement message routing to SlaveAgent based on tenant_id
- [ ] 7.3 Add graceful shutdown handling
- [ ] 7.4 Implement response publishing back to stream/WebSocket

## 8. API Endpoints
- [ ] 8.1 POST /auth/login - authenticate and return JWT
- [ ] 8.2 POST /messages - send message to queue
- [ ] 8.3 GET /messages - retrieve conversation history (tenant-filtered)
- [ ] 8.4 GET /notifications - retrieve user's notifications
- [ ] 8.5 PATCH /notifications/{id}/read - mark notification as read
- [ ] 8.6 WebSocket /ws - real-time message updates
- [ ] 8.7 GET /health - service health check

## 9. Web UI
- [ ] 9.1 Initialize React app with Vite
- [ ] 9.2 Create login form component
- [ ] 9.3 Build chat interface with message list and input
- [ ] 9.4 Add notification inbox/badge component
- [ ] 9.5 Implement WebSocket connection for real-time updates
- [ ] 9.6 Add tenant/user context display (name, role)
- [ ] 9.7 Style with basic CSS (no framework needed for PoC)

## 10. Integration Testing
- [ ] 10.1 Test tenant isolation: User from Tenant A cannot see Tenant B's data
- [ ] 10.2 Test message flow: UI → API → Queue → Worker → SlaveAgent → LLM → Response
- [ ] 10.3 Test RAG context: LLM response uses tenant knowledge (e.g., knows staff roster)
- [ ] 10.4 Test notification: User A mentions delivery → User B receives notification
- [ ] 10.5 Test conversation memory: LLM remembers previous messages in session

## 11. Demo Scenarios
- [ ] 11.1 Restaurant: Employee says "delivery tomorrow 10am, I'm off" → notifies morning shift
- [ ] 11.2 Property: Tenant asks "when is next cleaning?" → LLM retrieves schedule from RAG
