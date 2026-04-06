## ADDED Requirements

### Requirement: Cache invalidation on data access
The system SHALL check for index file modification time before using cached index data.

#### Scenario: Index file changed externally
- **WHEN** the index file has been modified since last load
- **THEN** the system SHALL reload the index from disk

#### Scenario: Index file unchanged
- **WHEN** the index file modification time is older than the cached load time
- **THEN** the system MAY use the cached index data

### Requirement: Fixed data directory path
The system SHALL use `~/Documents/baby-diary/records/` as the primary data directory.

#### Scenario: Documents directory exists
- **WHEN** the Documents directory exists
- **THEN** the system SHALL use it as the data directory

#### Scenario: Documents directory does not exist
- **WHEN** the Documents directory does not exist
- **THEN** the system SHALL create it before writing data
