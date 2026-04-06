## ADDED Requirements

### Requirement: API client handles authentication
The system SHALL automatically include JWT token in all API requests.

#### Scenario: Request with valid token
- **WHEN** making an API request
- **THEN** system reads token from storage
- **AND** system adds Authorization: Bearer <token> header

#### Scenario: Request without token
- **WHEN** making an API request without stored token
- **THEN** system redirects to login page
- **AND** request is not sent

### Requirement: API client handles errors uniformly
The system SHALL provide consistent error handling for all API requests.

#### Scenario: Network error
- **WHEN** API request fails due to network issue
- **THEN** system shows "网络连接失败，请重试" toast
- **AND** request promise rejects with error

#### Scenario: Server error (5xx)
- **WHEN** API returns 500 error
- **THEN** system shows "服务器错误，请稍后重试" toast
- **AND** error is logged to console

#### Scenario: Unauthorized error (401)
- **WHEN** API returns 401 error
- **THEN** system clears stored token
- **AND** system redirects to login page

#### Scenario: Validation error (400)
- **WHEN** API returns 400 error with message
- **THEN** system shows the error message from response
- **AND** form validation errors are displayed

### Requirement: API client provides convenient methods
The system SHALL provide wrapper methods for common API operations.

#### Scenario: Create record
- **WHEN** calling api.createRecord(type, details)
- **THEN** system sends POST /api/records/ with proper body
- **AND** returns created record data

#### Scenario: Get daily records
- **WHEN** calling api.getDailyRecords(date)
- **THEN** system sends GET /api/records/daily?date=<date>
- **AND** returns array of records

#### Scenario: Get baby config
- **WHEN** calling api.getBabyConfig()
- **THEN** system sends GET /api/config/baby
- **AND** returns baby configuration object

#### Scenario: Update baby config
- **WHEN** calling api.updateBabyConfig(data)
- **THEN** system sends PUT /api/config/baby with data
- **AND** returns updated configuration

#### Scenario: Get AI analysis
- **WHEN** calling api.getAIAnalysis(date)
- **THEN** system sends POST /api/ai/analyze with date
- **AND** returns analysis result

### Requirement: API base URL is configurable
The system SHALL support different API base URLs for different environments.

#### Scenario: Production environment
- **WHEN** app is built for production
- **THEN** API requests go to production URL

#### Scenario: Development environment
- **WHEN** app is in development mode
- **THEN** API requests go to development URL