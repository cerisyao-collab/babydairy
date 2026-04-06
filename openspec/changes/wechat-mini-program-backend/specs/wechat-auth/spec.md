## ADDED Requirements

### Requirement: WeChat mini-program login

The system SHALL support WeChat mini-program login using the official WeChat authentication flow.

#### Scenario: Successful login with valid code
- **WHEN** user sends POST request to `/api/auth/login` with valid WeChat `code`
- **THEN** system returns JWT token with user info including `openid`, `nickname`, and `avatar_url`

#### Scenario: Login with invalid code
- **WHEN** user sends POST request to `/api/auth/login` with invalid or expired `code`
- **THEN** system returns 401 error with message "Invalid WeChat code"

### Requirement: User profile retrieval

The system SHALL allow authenticated users to retrieve their profile information.

#### Scenario: Get user profile
- **WHEN** authenticated user sends GET request to `/api/auth/profile`
- **THEN** system returns user's `nickname`, `avatar_url`, and `created_at`

#### Scenario: Unauthorized profile access
- **WHEN** unauthenticated user sends GET request to `/api/auth/profile`
- **THEN** system returns 401 error with message "Unauthorized"

### Requirement: User profile update

The system SHALL allow authenticated users to update their profile information.

#### Scenario: Update user nickname
- **WHEN** authenticated user sends PUT request to `/api/auth/profile` with new `nickname`
- **THEN** system updates user's nickname and returns updated profile

### Requirement: User isolation

The system SHALL ensure all user data is isolated by user ID derived from WeChat openid.

#### Scenario: Data access isolation
- **WHEN** authenticated user requests their records
- **THEN** system SHALL only return records belonging to that user

#### Scenario: Cross-user access prevention
- **WHEN** authenticated user attempts to access another user's record by ID
- **THEN** system returns 404 error with message "Record not found"