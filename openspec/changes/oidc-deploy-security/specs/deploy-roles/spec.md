## ADDED Requirements

### Requirement: Deploy roles SHALL follow principle of least privilege
RAM roles used for deployment SHALL have only the minimum permissions required for their specific function.

#### Scenario: Terraform deploy role has limited permissions
- **WHEN** terraform-deploy role is used
- **THEN** role can only create/modify/delete VPC, RDS, OSS, FC, RAM resources
- **AND** role cannot access existing data in RDS or OSS
- **AND** role cannot modify resources outside project naming convention

#### Scenario: FC deploy role has limited permissions
- **WHEN** fc-deploy role is used
- **THEN** role can only update FC functions in baby-diary-* services
- **AND** role can only read from secrets OSS bucket
- **AND** role cannot modify infrastructure resources

### Requirement: Infrastructure and application deployment roles SHALL be separate
Separate RAM roles SHALL be used for infrastructure deployment (Terraform) and application deployment (FC functions).

#### Scenario: Terraform role cannot deploy functions
- **WHEN** terraform-deploy role is used
- **THEN** role cannot invoke FC functions
- **AND** role cannot read application secrets

#### Scenario: FC deploy role cannot modify infrastructure
- **WHEN** fc-deploy role is used
- **THEN** role cannot create/delete RDS instances
- **AND** role cannot create/delete VPC resources
- **AND** role cannot modify IAM roles

### Requirement: FC execution role SHALL be separate from deploy roles
FC function execution role (runtime) SHALL be distinct from deployment roles.

#### Scenario: FC execution role assumed by FC service
- **WHEN** FC function executes
- **THEN** function assumes fc-execution role
- **AND** role is trusted only by fc.aliyuncs.com service
- **AND** role has permissions for OSS, RDS access only

#### Scenario: Deploy role cannot be used at runtime
- **WHEN** FC function attempts to use deploy role
- **THEN** assume role request is denied
- **AND** fc-execution role is used instead

### Requirement: Resource permissions SHALL be scoped by naming convention
IAM policies SHALL limit permissions to resources matching project naming convention (baby-diary-*).

#### Scenario: Can only create project-named resources
- **WHEN** create request is made for resource named "other-project-db"
- **THEN** request is denied

#### Scenario: Can create baby-diary named resources
- **WHEN** create request is made for resource named "baby-diary-db"
- **THEN** request is allowed

### Requirement: Local development SHALL use temporary credentials
Developers SHALL use temporary credentials via AssumeRole or browser-based login, not long-lived AccessKeys.

#### Scenario: Developer assumes role with MFA
- **WHEN** developer runs `aliyun sts AssumeRole`
- **THEN** developer must have authenticated with MFA
- **AND** temporary credentials are issued
- **AND** credentials expire within 12 hours

#### Scenario: Long-lived AccessKey is denied
- **WHEN** developer attempts to use long-lived AccessKey
- **AND** policy requires MFA for sensitive operations
- **THEN** request is denied without MFA context