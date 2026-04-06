## ADDED Requirements

### Requirement: PostgreSQL database setup

The system SHALL use PostgreSQL as the primary data storage backend.

#### Scenario: Database connection
- **WHEN** application starts
- **THEN** system connects to PostgreSQL database using configured connection string

#### Scenario: Connection pool management
- **WHEN** multiple API requests arrive
- **THEN** system uses connection pool to efficiently manage database connections

### Requirement: User table schema

The system SHALL maintain a users table for storing user information.

#### Scenario: User table structure
- **WHEN** database is initialized
- **THEN** users table exists with columns: `id` (UUID, primary key), `openid` (VARCHAR, unique), `nickname`, `avatar_url`, `created_at`, `updated_at`

#### Scenario: User creation
- **WHEN** new user logs in via WeChat
- **THEN** system inserts new row into users table with generated UUID and WeChat openid

### Requirement: Records table schema

The system SHALL maintain a records table for storing baby diary records.

#### Scenario: Records table structure
- **WHEN** database is initialized
- **THEN** records table exists with columns: `id` (UUID, primary key), `user_id` (UUID, foreign key), `type` (VARCHAR), `timestamp` (TIMESTAMP), `date` (DATE), `details` (JSONB), `images` (TEXT array), `created_at`, `updated_at`

#### Scenario: User-records relationship
- **WHEN** record is created
- **THEN** record's `user_id` references the creating user's `id`

#### Scenario: Index on user_id and date
- **WHEN** database is initialized
- **THEN** index exists on records table for `user_id` and `date` columns to optimize query performance

### Requirement: Baby configs table schema

The system SHALL maintain a baby_configs table for storing baby configuration per user.

#### Scenario: Baby configs table structure
- **WHEN** database is initialized
- **THEN** baby_configs table exists with columns: `id` (UUID, primary key), `user_id` (UUID, foreign key, unique), `baby_name`, `birth_date` (DATE), `created_at`, `updated_at`

#### Scenario: One config per user
- **WHEN** user sets baby config
- **THEN** system ensures only one baby_config row exists per user via unique constraint on `user_id`

### Requirement: Data migration support

The system SHALL provide migration scripts to transition from file-based storage to database storage.

#### Scenario: Alembic migration setup
- **WHEN** database schema changes are needed
- **THEN** system uses Alembic migration tool to manage schema versions

#### Scenario: Initial migration
- **WHEN** first deployment occurs
- **THEN** system applies initial migration creating all required tables

### Requirement: Data isolation enforcement

The system SHALL enforce data isolation at the database query level.

#### Scenario: Query with user filter
- **WHEN** any record query is executed
- **THEN** system automatically includes `user_id` filter based on authenticated user

### Requirement: JSONB details storage

The system SHALL store record details as JSONB for flexible schema support.

#### Scenario: Store feeding details
- **WHEN** feeding record is created with details
- **THEN** system stores details as JSONB allowing flexible field structure

#### Scenario: Query JSONB fields
- **WHEN** system queries records by JSONB field value
- **THEN** system uses PostgreSQL JSONB query operators for efficient retrieval