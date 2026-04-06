## ADDED Requirements

### Requirement: Automatic index refresh
The system SHALL automatically refresh the index when reading data.

#### Scenario: Query triggers index refresh
- **WHEN** a query function is called
- **THEN** the system SHALL check and reload the index if modified

#### Scenario: Fresh index after record creation
- **WHEN** a new record is created
- **THEN** subsequent queries in any session SHALL see the new record

### Requirement: Manual refresh API
The system SHALL provide a `refresh_index()` function for explicit cache invalidation.

#### Scenario: User calls refresh
- **WHEN** `refresh_index()` is called
- **THEN** the index SHALL be reloaded from disk
