## ADDED Requirements

### Requirement: Integration tests SHALL verify model-database mapping
Integration tests SHALL verify SQLAlchemy models correctly map to database tables.

#### Scenario: Model creates database record
- **WHEN** test creates a model instance and saves to database
- **THEN** record is persisted in database table
- **AND** record can be retrieved with correct values

#### Scenario: Model relationships work correctly
- **WHEN** test creates related model instances
- **THEN** relationship fields return correct related objects
- **AND** foreign key constraints are enforced

### Requirement: Integration tests SHALL verify service layer with database
Integration tests SHALL verify service methods correctly interact with database.

#### Scenario: Service creates record
- **WHEN** service method creates a record
- **THEN** record is persisted in database
- **AND** returned data matches persisted data

#### Scenario: Service queries records
- **WHEN** service method queries records
- **THEN** correct records are returned from database
- **AND** filtering and ordering work correctly

### Requirement: Integration tests SHALL use transaction rollback
Integration tests SHALL use transaction rollback to ensure test isolation.

#### Scenario: Test data is cleaned after test
- **WHEN** integration test completes
- **THEN** database transaction is rolled back
- **AND** test data does not persist in database
- **AND** next test starts with clean state

### Requirement: Integration tests SHALL be marked with pytest marker
Integration tests SHALL use `@pytest.mark.integration` marker for selective execution.

#### Scenario: Run only integration tests
- **WHEN** developer runs `pytest -m integration`
- **THEN** only tests marked with integration marker are executed
- **AND** unit tests are skipped

#### Scenario: Run all tests including integration
- **WHEN** developer runs `pytest`
- **THEN** both unit tests and integration tests are executed