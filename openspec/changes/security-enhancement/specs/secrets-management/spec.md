## ADDED Requirements

### Requirement: System SHALL manage secrets via Alibaba Cloud KMS
All sensitive credentials (database passwords, API keys, secrets) SHALL be encrypted and stored using Alibaba Cloud KMS.

#### Scenario: Encrypt secret at deployment
- **WHEN** deploying infrastructure via Terraform
- **THEN** system creates KMS key
- **AND** encrypts all secrets with KMS key
- **AND** stores encrypted secrets in FC environment variables

#### Scenario: Decrypt secret at runtime
- **WHEN** FC function starts
- **THEN** system calls KMS Decrypt API
- **AND** caches decrypted secrets in memory
- **AND** never writes decrypted secrets to disk

### Requirement: System SHALL rotate KMS keys periodically
KMS keys SHALL be rotated automatically to limit exposure from key compromise.

#### Scenario: Automatic key rotation
- **WHEN** KMS key age exceeds rotation period (90 days)
- **THEN** system automatically creates new key version
- **AND** re-encrypts secrets with new key version

### Requirement: System SHALL log all KMS operations
All KMS operations (encrypt, decrypt, generate data key) SHALL be logged for audit purposes.

#### Scenario: Log decryption operation
- **WHEN** system calls KMS Decrypt
- **THEN** operation is logged with timestamp, caller identity, and key ID
- **AND** log is retained for at least 90 days

### Requirement: System SHALL restrict KMS access to authorized roles
Only FC execution role SHALL have permission to use KMS keys.

#### Scenario: Unauthorized access denied
- **WHEN** non-FC role attempts to use KMS key
- **THEN** request is denied with access denied error
- **AND** unauthorized access attempt is logged