## ADDED Requirements

### Requirement: Record creation API

The system SHALL provide RESTful API endpoint for creating baby diary records.

#### Scenario: Create feeding record
- **WHEN** authenticated user sends POST request to `/api/records` with record type `feeding` and details including `feeding_type`, `duration_minutes`, `amount_ml`
- **THEN** system creates record with UUID, stores in database, and returns record object with `id`, `timestamp`, `type`, `details`

#### Scenario: Create record with images
- **WHEN** authenticated user sends POST request to `/api/records` with record details and image URLs
- **THEN** system creates record with image references stored in `images` field

#### Scenario: Duplicate record detection
- **WHEN** authenticated user creates record with same type within 5 minutes of existing record
- **THEN** system returns warning with list of similar records and asks for confirmation

### Requirement: Record query API

The system SHALL provide API endpoints for querying records by date range and type.

#### Scenario: Query records by date range
- **WHEN** authenticated user sends GET request to `/api/records?start_date=2026-01-01&end_date=2026-01-31`
- **THEN** system returns all records for that user within the specified date range

#### Scenario: Query records by type
- **WHEN** authenticated user sends GET request to `/api/records?type=feeding`
- **THEN** system returns only feeding records for that user

#### Scenario: List daily records
- **WHEN** authenticated user sends GET request to `/api/records/daily?date=2026-01-15`
- **THEN** system returns all records for that user on that date

### Requirement: Single record retrieval API

The system SHALL provide API endpoint to retrieve a single record by ID.

#### Scenario: Get record by ID
- **WHEN** authenticated user sends GET request to `/api/records/{record_id}`
- **THEN** system returns the record if it belongs to the user

#### Scenario: Get non-existent record
- **WHEN** authenticated user sends GET request to `/api/records/{invalid_id}`
- **THEN** system returns 404 error with message "Record not found"

### Requirement: Record update API

The system SHALL provide API endpoint for updating existing records.

#### Scenario: Update record details
- **WHEN** authenticated user sends PUT request to `/api/records/{record_id}` with updated `details`
- **THEN** system updates record and returns updated record object

#### Scenario: Update record timestamp
- **WHEN** authenticated user updates record timestamp to a different date
- **THEN** system moves record to appropriate date storage

### Requirement: Record deletion API

The system SHALL provide API endpoint for deleting records.

#### Scenario: Delete existing record
- **WHEN** authenticated user sends DELETE request to `/api/records/{record_id}`
- **THEN** system removes record from database and returns 204 status

#### Scenario: Delete record with images
- **WHEN** authenticated user deletes record with associated images
- **THEN** system removes record and cleans up image references

### Requirement: Daily summary API

The system SHALL provide API endpoint for generating daily summary reports.

#### Scenario: Get daily summary
- **WHEN** authenticated user sends GET request to `/api/summary/daily?date=2026-01-15`
- **THEN** system returns formatted summary including feeding count, milk volume, urine/bowel count, and growth comparisons

#### Scenario: Summary with birth date comparison
- **WHEN** authenticated user has configured baby birth date and requests daily summary
- **THEN** system includes growth standard comparisons based on baby's age in days

### Requirement: Baby configuration API

The system SHALL provide API endpoints for managing baby configuration.

#### Scenario: Get baby config
- **WHEN** authenticated user sends GET request to `/api/config/baby`
- **THEN** system returns baby's `birth_date`, `baby_name`, and other configuration

#### Scenario: Set baby birth date
- **WHEN** authenticated user sends PUT request to `/api/config/baby` with `birth_date` in YYYY-MM-DD format
- **THEN** system updates baby config and returns updated configuration

#### Scenario: Invalid birth date format
- **WHEN** user provides birth date in invalid format
- **THEN** system returns 400 error with message "Invalid date format, use YYYY-MM-DD"

### Requirement: API authentication

All API endpoints SHALL require JWT authentication except the login endpoint.

#### Scenario: Missing authorization header
- **WHEN** request to protected endpoint lacks Authorization header
- **THEN** system returns 401 error with message "Missing authorization token"

#### Scenario: Invalid JWT token
- **WHEN** request includes expired or invalid JWT token
- **THEN** system returns 401 error with message "Invalid or expired token"

### Requirement: API documentation

The system SHALL provide OpenAPI documentation for all endpoints.

#### Scenario: Access OpenAPI spec
- **WHEN** user sends GET request to `/api/docs` or `/api/openapi.json`
- **THEN** system returns OpenAPI specification document

### Requirement: Error response format

The system SHALL return consistent error response format for all API errors.

#### Scenario: API error response
- **WHEN** any API error occurs
- **THEN** system returns JSON response with `error` field containing `code`, `message`, and optional `details`