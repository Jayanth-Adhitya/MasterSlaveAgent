## ADDED Requirements

### Requirement: Slave Agent Per Tenant
The system SHALL instantiate one SlaveAgent instance per tenant, responsible for handling all messages from that tenant's users.

#### Scenario: Agent created on first message
- **WHEN** a message arrives for a tenant with no active agent
- **THEN** a new SlaveAgent is instantiated for that tenant_id
- **AND** the agent is stored in the registry for future requests

#### Scenario: Agent reused for subsequent messages
- **WHEN** a message arrives for a tenant with existing agent
- **THEN** the existing SlaveAgent instance is retrieved from registry
- **AND** no new agent is created

### Requirement: Tenant Context Loading via RAG
The system SHALL load tenant-specific knowledge (schedules, roster, rules) via pgvector similarity search when processing messages.

#### Scenario: Relevant context retrieved
- **WHEN** the SlaveAgent processes a user message
- **THEN** it performs semantic search on tenant_knowledge table
- **AND** retrieves top-k relevant documents for that tenant_id
- **AND** includes retrieved context in the LLM prompt

#### Scenario: Context filtered by tenant
- **WHEN** RAG retrieval is performed
- **THEN** only knowledge belonging to the same tenant_id is searched
- **AND** other tenants' knowledge is never retrieved

### Requirement: Per-User Conversation Memory
The system SHALL maintain separate conversation history for each user session within the SlaveAgent.

#### Scenario: Memory isolated per user
- **WHEN** two users from same tenant send messages
- **THEN** each user's conversation history is tracked separately
- **AND** User A's history does not affect User B's responses

#### Scenario: Memory keyed by session
- **WHEN** a user starts a new session
- **THEN** conversation memory starts fresh
- **AND** previous session history is not loaded

### Requirement: Structured Action Output
The system SHALL require the LLM to return responses in structured JSON format containing both response text and optional actions.

#### Scenario: LLM returns response with action
- **WHEN** the LLM generates a response
- **THEN** output is structured as `{"response": "...", "actions": [...]}`
- **AND** actions are parsed and validated against action schema

#### Scenario: LLM returns response without action
- **WHEN** the LLM generates a simple conversational response
- **THEN** output contains empty actions array `{"response": "...", "actions": []}`
- **AND** no actions are executed

### Requirement: Action Execution
The system SHALL execute validated actions returned by the LLM through the SlaveAgent.

#### Scenario: Notify user action executed
- **WHEN** LLM returns action `{"type": "notify_user", "user_id": 5, "message": "..."}`
- **THEN** SlaveAgent inserts notification into database
- **AND** notification is associated with correct tenant_id and from_user_id

#### Scenario: Invalid action rejected
- **WHEN** LLM returns malformed or unsupported action
- **THEN** the action is logged as error
- **AND** user receives response without that action being executed

### Requirement: Tenant-Aware System Prompt
The system SHALL inject tenant context into the LLM system prompt, including business type, user roster, and relevant rules.

#### Scenario: System prompt includes tenant info
- **WHEN** SlaveAgent constructs LLM prompt
- **THEN** system prompt includes tenant name, type, and user roster
- **AND** LLM understands the business context (restaurant vs property)

#### Scenario: System prompt instructs action format
- **WHEN** SlaveAgent constructs LLM prompt
- **THEN** system prompt includes instructions for returning structured JSON
- **AND** provides examples of valid action schemas
