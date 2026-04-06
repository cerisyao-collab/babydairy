## ADDED Requirements

### Requirement: Mini-program SHALL sign all API requests
All requests from mini-program to backend SHALL include a signature to prevent tampering and replay attacks.

#### Scenario: Generate request signature
- **WHEN** mini-program sends API request
- **THEN** system generates timestamp and nonce
- **AND** computes HMAC-SHA256 signature over (method + url + body + timestamp + nonce)
- **AND** includes X-Timestamp, X-Nonce, X-Signature headers

#### Scenario: Validate signature at backend
- **WHEN** backend receives API request
- **THEN** system validates timestamp is within ±5 minutes
- **AND** validates nonce has not been used recently
- **AND** recomputes signature and compares with provided signature
- **AND** rejects request if any validation fails

### Requirement: System SHALL prevent replay attacks
Each request SHALL be uniquely identified and not accepted more than once.

#### Scenario: Reject replayed request
- **WHEN** backend receives request with previously used nonce
- **THEN** system rejects request with 401 error
- **AND** logs potential replay attack

#### Scenario: Expire old nonces
- **WHEN** nonce has been stored for more than 5 minutes
- **THEN** system removes nonce from cache
- **AND** allows reuse of expired nonce

### Requirement: System SHALL reject requests with expired timestamp
Requests with timestamps outside acceptable window SHALL be rejected.

#### Scenario: Reject expired timestamp
- **WHEN** backend receives request with timestamp older than 5 minutes
- **THEN** system rejects request with 401 error
- **AND** returns error message "Request expired"

#### Scenario: Reject future timestamp
- **WHEN** backend receives request with timestamp more than 5 minutes in future
- **THEN** system rejects request with 401 error
- **AND** logs potential clock synchronization issue