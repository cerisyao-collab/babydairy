## ADDED Requirements

### Requirement: Test database SHALL be PostgreSQL running in Docker container
Test database SHALL use PostgreSQL 14 in Docker container for local development and testing.

#### Scenario: Start test database container
- **WHEN** developer runs test database startup command
- **THEN** Docker container starts with PostgreSQL 14
- **AND** database is accessible on port 5433
- **AND** database name is baby_diary_test

#### Scenario: Stop test database container
- **WHEN** developer runs test database stop command
- **THEN** Docker container stops
- **AND** all test data is removed (tmpfs storage)

### Requirement: Test database SHALL use memory storage for performance
Test database SHALL use tmpfs (memory filesystem) for faster test execution.

#### Scenario: Database uses memory storage
- **WHEN** test database container starts
- **THEN** PostgreSQL data directory is mounted as tmpfs
- **AND** database operations are faster than disk-based storage

### Requirement: Test database SHALL have isolated credentials
Test database SHALL use separate credentials from production database.

#### Scenario: Test database credentials
- **WHEN** test database starts
- **THEN** database user is "test"
- **AND** database password is "test"
- **AND** these credentials differ from production credentials

### Requirement: Test database SHALL be accessible from test code
Test code SHALL be able to connect to test database using configuration.

#### Scenario: Connect to test database
- **WHEN** test code requests database connection
- **THEN** connection uses test database configuration
- **AND** connection succeeds to baby_diary_test database
- **AND** SQLAlchemy session is created