## ADDED Requirements

### Requirement: GitHub Actions SHALL authenticate via OIDC without long-lived credentials
GitHub Actions workflows SHALL use OIDC (OpenID Connect) to authenticate with Alibaba Cloud, eliminating the need for long-lived AccessKey credentials.

#### Scenario: GitHub Actions obtains temporary credentials via OIDC
- **WHEN** GitHub Actions workflow runs
- **THEN** workflow requests OIDC token from GitHub
- **AND** workflow exchanges OIDC token for Alibaba Cloud STS temporary credentials
- **AND** temporary credentials expire within 12 hours
- **AND** no long-lived AccessKey is stored in GitHub Secrets

#### Scenario: OIDC token validation
- **WHEN** Alibaba Cloud STS receives AssumeRole request with OIDC token
- **THEN** STS validates token signature using GitHub public keys
- **AND** STS validates issuer is "https://token.actions.githubusercontent.com"
- **AND** STS validates audience is "github-actions"
- **AND** STS validates subject matches configured repository

### Requirement: OIDC authentication SHALL restrict access by repository and branch
OIDC role trust policy SHALL restrict which GitHub repositories and branches can assume the role.

#### Scenario: Restrict by repository
- **WHEN** OIDC token subject claims repository "your-org/babyjour"
- **AND** role trust policy allows repository "your-org/babyjour"
- **THEN** AssumeRole request is allowed

#### Scenario: Reject unauthorized repository
- **WHEN** OIDC token subject claims repository "other-org/other-repo"
- **AND** role trust policy only allows repository "your-org/babyjour"
- **THEN** AssumeRole request is denied

#### Scenario: Restrict production deployment to main branch
- **WHEN** production deploy role is assumed
- **AND** OIDC token subject indicates branch is not "main"
- **THEN** AssumeRole request is denied

### Requirement: Temporary credentials SHALL have limited lifetime
STS temporary credentials obtained via OIDC SHALL have maximum 12 hours validity.

#### Scenario: Credentials expire automatically
- **WHEN** temporary credentials are issued
- **THEN** credentials have expiration time
- **AND** expiration time is within 12 hours from issuance
- **AND** expired credentials cannot be used

### Requirement: All OIDC-based deployments SHALL be auditable
All deployments using OIDC authentication SHALL be traceable to specific GitHub actor, repository, and workflow.

#### Scenario: Audit log captures actor information
- **WHEN** AssumeRole request is made via OIDC
- **THEN** CloudTrail/ActionTrail logs the GitHub actor
- **AND** logs include repository name
- **AND** logs include workflow name
- **AND** logs include branch name