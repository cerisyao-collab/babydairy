## ADDED Requirements

### Requirement: Daily storage file structure
The system SHALL store records in daily JSON files named by date (YYYY-MM-DD.json).

#### Scenario: New record creation creates daily file if needed
- **WHEN** a record is created for a date that has no existing file
- **THEN** the system creates a new JSON file named YYYY-MM-DD.json

#### Scenario: Multiple records on same day stored together
- **WHEN** multiple records are created for the same date
- **THEN** all records are stored in the same daily file

### Requirement: Daily file data format
Each daily file SHALL contain an array of record objects with all record fields preserved.

#### Scenario: File contains valid JSON array
- **WHEN** a daily file is read
- **THEN** it parses as a valid JSON array of record objects
