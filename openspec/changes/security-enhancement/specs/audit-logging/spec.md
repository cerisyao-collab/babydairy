## ADDED Requirements

### Requirement: System SHALL log authentication events
All authentication-related events SHALL be logged for security audit.

#### Scenario: Log successful login
- **WHEN** user successfully logs in
- **THEN** system logs event with user ID, device info, timestamp
- **AND** logs IP address (from FC headers)
- **AND** log level is INFO

#### Scenario: Log failed login
- **WHEN** login attempt fails
- **THEN** system logs event with reason, timestamp
- **AND** logs device info if available
- **AND** log level is WARN

#### Scenario: Log logout
- **WHEN** user logs out
- **THEN** system logs event with user ID, timestamp
- **AND** invalidates session

### Requirement: System SHALL log sensitive data access
Access to encrypted fields SHALL be logged.

#### Scenario: Log PII decryption
- **WHEN** system decrypts encrypted field
- **THEN** system logs user ID, field name, timestamp
- **AND** does not log decrypted value
- **AND** includes request ID for correlation

### Requirement: System SHALL log administrative actions
All administrative operations SHALL be logged.

#### Scenario: Log configuration change
- **WHEN** system configuration is modified
- **THEN** system logs who made change, what changed, when
- **AND** logs previous and new values for non-sensitive fields
- **AND** masks sensitive values in log

### Requirement: System SHALL retain audit logs
Audit logs SHALL be retained for compliance requirements.

#### Scenario: Retain logs
- **WHEN** audit log is written
- **THEN** log is stored in persistent storage
- **AND** log is retained for at least 90 days
- **AND** logs are immutable (append-only)

#### Scenario: Query audit logs
- **WHEN** administrator queries audit logs
- **THEN** system supports filtering by user, date range, event type
- **AND** returns paginated results
- **AND** logs query operation itself