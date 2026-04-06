## ADDED Requirements

### Requirement: System SHALL encrypt sensitive database fields
Personally Identifiable Information (PII) fields SHALL be encrypted at rest using AES-256-GCM.

#### Scenario: Encrypt PII on write
- **WHEN** user saves baby configuration with name or birth date
- **THEN** system generates data key via KMS
- **AND** encrypts field value with AES-256-GCM
- **AND** stores ciphertext, IV, and encrypted data key

#### Scenario: Decrypt PII on read
- **WHEN** user retrieves baby configuration
- **THEN** system decrypts data key via KMS
- **AND** decrypts field value with AES-256-GCM
- **AND** returns plaintext to authorized user

### Requirement: System SHALL use unique IV for each encryption
Each encryption operation SHALL use a unique initialization vector (IV).

#### Scenario: Generate unique IV
- **WHEN** encrypting a field value
- **THEN** system generates random 12-byte IV
- **AND** stores IV with ciphertext
- **AND** never reuses IV for same key

### Requirement: System SHALL support encrypted field search
Encrypted fields SHALL support equality search without decryption.

#### Scenario: Search by encrypted field
- **WHEN** searching for record by baby name
- **THEN** system uses blinded index (HMAC of value)
- **AND** stores blinded index alongside ciphertext
- **AND** searches using blinded index

### Requirement: System SHALL migrate existing plaintext data
Existing plaintext PII data SHALL be encrypted in-place.

#### Scenario: Migrate plaintext to ciphertext
- **WHEN** migration job runs
- **THEN** system reads plaintext value
- **AND** encrypts value with new data key
- **AND** updates record with ciphertext
- **AND** logs migration progress