## ADDED Requirements

### Requirement: System SHALL remove PII before sending to LLM
User data sent to LLM SHALL have personally identifiable information removed or anonymized.

#### Scenario: Anonymize baby name
- **WHEN** preparing data for LLM analysis
- **THEN** system replaces baby name with "宝宝"
- **AND** original name is not included in LLM request

#### Scenario: Convert date to relative time
- **WHEN** preparing birth date for LLM
- **THEN** system converts date to relative time (e.g., "15天")
- **AND** exact date is not sent to LLM

#### Scenario: Remove contact information
- **WHEN** user data contains phone or address
- **THEN** system removes these fields entirely
- **AND** LLM never receives contact information

### Requirement: System SHALL log all LLM calls
Every LLM API call SHALL be logged with caller identity and data summary.

#### Scenario: Log LLM request
- **WHEN** system calls LLM API
- **THEN** log entry includes user ID, timestamp, request type
- **AND** log includes data categories sent (not raw data)
- **AND** log is retained for 90 days

#### Scenario: Log LLM response
- **WHEN** LLM API returns response
- **THEN** log entry includes response status
- **AND** log includes token usage
- **AND** log includes response time

### Requirement: System SHALL validate LLM output
LLM responses SHALL be validated to prevent data leakage or inappropriate content.

#### Scenario: Validate response contains no PII
- **WHEN** LLM returns response
- **THEN** system scans response for PII patterns
- **AND** removes any detected PII before returning to user
- **AND** logs PII detection incident

#### Scenario: Validate response format
- **WHEN** LLM returns analysis response
- **THEN** system validates response structure
- **AND** rejects malformed responses
- **AND** falls back to rule-based analysis on error

### Requirement: System SHALL filter LLM input for prompt injection
User input to LLM SHALL be filtered to prevent prompt injection attacks.

#### Scenario: Detect prompt injection attempt
- **WHEN** user input contains suspicious patterns (e.g., "ignore previous instructions")
- **THEN** system removes or neutralizes the pattern
- **AND** logs potential injection attempt
- **AND** continues with sanitized input