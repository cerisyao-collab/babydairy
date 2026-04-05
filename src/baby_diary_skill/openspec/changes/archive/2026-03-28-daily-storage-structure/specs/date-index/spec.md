## ADDED Requirements

### Requirement: Date index file
The system SHALL maintain an index.json file that tracks all daily files.

#### Scenario: Index updated when new daily file created
- **WHEN** a new daily file is created
- **THEN** the index.json is updated with the new date entry

#### Scenario: Index contains file metadata
- **WHEN** the index is read
- **THEN** it contains file name, record count, size in bytes, and record types for each date

### Requirement: Index query support
The system SHALL support querying the index for date ranges without loading daily files.

#### Scenario: Query returns dates in range
- **WHEN** a date range query is made
- **THEN** the system returns all dates within the range that have records
