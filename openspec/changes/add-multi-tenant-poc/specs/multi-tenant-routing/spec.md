## ADDED Requirements

### Requirement: Tenant Data Isolation
The system SHALL enforce tenant data isolation by including tenant_id in all database queries and validating tenant context from JWT claims.

#### Scenario: User queries only see own tenant data
- **WHEN** a user with tenant_id=1 requests messages
- **THEN** only messages with tenant_id=1 are returned
- **AND** messages from tenant_id=2 are not visible

#### Scenario: Invalid tenant context rejected
- **WHEN** a request contains a JWT with missing or invalid tenant_id
- **THEN** the system returns 401 Unauthorized
- **AND** no data access is permitted

### Requirement: Tenant-Aware Message Routing
The system SHALL route messages to tenant-specific queues in Redis Streams using the pattern `messages:{tenant_id}`.

#### Scenario: Message routed to correct tenant queue
- **WHEN** a user from tenant_id=1 sends a message
- **THEN** the message is published to Redis Stream `messages:1`
- **AND** workers processing tenant_id=2 do not receive the message

#### Scenario: Message contains tenant and user context
- **WHEN** a message is enqueued
- **THEN** the message payload includes tenant_id, user_id, session_id, and content
- **AND** all fields are validated before queuing

### Requirement: JWT Authentication with Tenant Claims
The system SHALL authenticate users via JWT tokens containing tenant_id and user_id claims.

#### Scenario: Successful login returns JWT with tenant context
- **WHEN** a user provides valid email and password
- **THEN** the system returns a JWT token
- **AND** the token contains tenant_id, user_id, and email claims

#### Scenario: Protected endpoints require valid JWT
- **WHEN** a request to a protected endpoint lacks a valid JWT
- **THEN** the system returns 401 Unauthorized

### Requirement: User-Tenant Association
The system SHALL ensure each user belongs to exactly one tenant, enforced at the database level.

#### Scenario: User creation requires tenant assignment
- **WHEN** a new user is created
- **THEN** the user record includes a valid tenant_id foreign key

#### Scenario: User cannot access other tenants
- **WHEN** a user attempts to query data with a different tenant_id
- **THEN** the query returns no results or is rejected
