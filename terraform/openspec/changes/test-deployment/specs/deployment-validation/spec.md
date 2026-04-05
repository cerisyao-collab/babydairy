## ADDED Requirements

### Requirement: OIDC Authentication
GitHub Actions SHALL authenticate with Alibaba Cloud using OIDC temporary credentials.

#### Scenario: OIDC token exchange succeeds
- **WHEN** GitHub Actions workflow runs with OIDC configuration
- **THEN** workflow successfully assumes RAM role via STS AssumeRole

#### Scenario: Unauthorized repository is rejected
- **WHEN** workflow from unauthorized repository attempts to assume role
- **THEN** STS denies the request with authentication error

### Requirement: FC Function Deployment
FC function SHALL deploy successfully via Serverless Devs with OIDC credentials.

#### Scenario: FC function deploys with VPC configuration
- **WHEN** deploy workflow runs with valid OIDC credentials
- **THEN** FC function is created/updated with correct VPC, vswitch, security group

#### Scenario: FC function can access OSS secrets bucket
- **WHEN** FC function executes
- **THEN** function can read secrets from configured OSS bucket

### Requirement: Database Connection
FC function SHALL connect to RDS PostgreSQL instance.

#### Scenario: FC function connects to RDS
- **WHEN** FC function attempts database connection
- **THEN** connection succeeds using credentials from OSS secrets

#### Scenario: Database queries work
- **WHEN** FC function executes SQL query
- **THEN** query returns expected results

### Requirement: API Health Check
API endpoints SHALL respond correctly after deployment.

#### Scenario: Health endpoint returns success
- **WHEN** HTTP request sent to API health endpoint
- **THEN** response status is 200 with success message