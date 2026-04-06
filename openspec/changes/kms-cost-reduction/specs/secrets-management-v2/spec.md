## ADDED Requirements

### Requirement: System SHALL manage secrets via OSS encrypted storage with local envelope encryption
All sensitive credentials (database passwords, API keys, secrets) SHALL be encrypted using local envelope encryption with master key stored in OSS.

#### Scenario: Encrypt secret at deployment
- **WHEN** deploying infrastructure via Terraform
- **THEN** system creates OSS bucket with SSE-OSS encryption
- **AND** generates 256-bit master key
- **AND** uploads master key to OSS with restricted access
- **AND** encrypts all secrets with envelope encryption
- **AND** stores encrypted secrets in OSS bucket

#### Scenario: Decrypt secret at runtime
- **WHEN** FC function starts
- **THEN** system reads master key from OSS
- **AND** decrypts data key with master key
- **AND** decrypts secrets with data key
- **AND** caches decrypted secrets in memory
- **AND** never writes decrypted secrets to disk

### Requirement: System SHALL use AES-256-GCM for all encryption operations
All encryption operations SHALL use AES-256-GCM algorithm for authenticated encryption.

#### Scenario: Encrypt credential value
- **WHEN** encrypting a credential value
- **THEN** system generates random 256-bit data key
- **AND** encrypts credential with data key using AES-256-GCM
- **AND** encrypts data key with master key using AES-256-GCM
- **AND** stores IV, AuthTag, encrypted data key, and encrypted credential

#### Scenario: Decrypt credential value
- **WHEN** decrypting a credential value
- **THEN** system reads encrypted data key and encrypted credential
- **AND** decrypts data key with master key using AES-256-GCM
- **AND** decrypts credential with data key using AES-256-GCM
- **AND** verifies AuthTag before returning plaintext

### Requirement: System SHALL rotate master key every 90 days
Master key SHALL be rotated automatically to limit exposure from key compromise.

#### Scenario: Automatic key rotation trigger
- **WHEN** FC scheduled trigger runs (every 30 days)
- **AND** master key age exceeds 90 days
- **THEN** system generates new master key
- **AND** re-encrypts all data keys with new master key
- **AND** uploads new master key to OSS
- **AND** retains old master key backup for 7 days

#### Scenario: Key rotation failure handling
- **WHEN** key rotation fails
- **THEN** system keeps current master key active
- **AND** logs rotation failure with error details
- **AND** sends alert notification

### Requirement: System SHALL restrict OSS bucket access to FC execution role
Only FC execution role SHALL have permission to read master key and encrypted secrets from OSS.

#### Scenario: Authorized access granted
- **WHEN** FC execution role reads from secrets OSS bucket
- **THEN** request is granted
- **AND** master key and secrets are returned

#### Scenario: Unauthorized access denied
- **WHEN** non-FC role attempts to read from secrets OSS bucket
- **THEN** request is denied with access denied error
- **AND** unauthorized access attempt is logged

### Requirement: System SHALL backup master key with versioning
Master key SHALL be backed up through OSS versioning and optional local backup.

#### Scenario: OSS versioning backup
- **WHEN** new master key is uploaded to OSS
- **THEN** OSS retains previous version
- **AND** all versions are accessible for recovery

#### Scenario: Local backup creation
- **WHEN** master key is rotated
- **THEN** system downloads old master key
- **AND** encrypts old master key with backup password
- **AND** saves encrypted backup to local storage

## MODIFIED Requirements

### Requirement: System SHALL manage secrets via Alibaba Cloud KMS
All sensitive credentials (database passwords, API keys, secrets) SHALL be encrypted and stored using OSS encrypted storage with local envelope encryption.

#### Scenario: Encrypt secret at deployment
- **WHEN** deploying infrastructure via Terraform
- **THEN** system creates OSS bucket with SSE-OSS encryption
- **AND** generates and uploads master key to OSS
- **AND** encrypts all secrets with local envelope encryption
- **AND** stores encrypted secrets in OSS bucket

#### Scenario: Decrypt secret at runtime
- **WHEN** FC function starts
- **THEN** system reads master key from OSS
- **AND** performs local envelope decryption
- **AND** caches decrypted secrets in memory
- **AND** never writes decrypted secrets to disk