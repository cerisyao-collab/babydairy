## ADDED Requirements

### Requirement: Terraform configuration structure

The system SHALL provide Terraform configuration for deploying to Aliyun.

#### Scenario: Terraform files structure
- **WHEN** Terraform configuration is examined
- **THEN** files exist: `main.tf`, `variables.tf`, `outputs.tf`, `providers.tf`

### Requirement: Aliyun ECS instance

The system SHALL provision a minimal ECS instance for running the application.

#### Scenario: ECS instance provisioning
- **WHEN** Terraform apply is executed
- **THEN** ECS instance is created with specification: 1 core, 1GB memory, ecs.tiny-c1m1.small or equivalent minimal instance type

#### Scenario: ECS public IP
- **WHEN** ECS instance is provisioned
- **THEN** instance has public IP address accessible for API requests

### Requirement: Aliyun RDS PostgreSQL

The system SHALL provision a minimal RDS PostgreSQL instance.

#### Scenario: RDS PostgreSQL provisioning
- **WHEN** Terraform apply is executed
- **THEN** RDS PostgreSQL instance is created with specification: 1 core, 1GB memory, rds.pg.tiny.ha or equivalent minimal instance type

#### Scenario: RDS private network
- **WHEN** RDS instance is provisioned
- **THEN** RDS is accessible only from ECS via internal VPC network

### Requirement: VPC and security groups

The system SHALL configure VPC and security groups for network security.

#### Scenario: VPC creation
- **WHEN** Terraform apply is executed
- **THEN** VPC is created with CIDR block for ECS and RDS

#### Scenario: ECS security group
- **WHEN** security group is configured
- **THEN** ECS allows inbound traffic only on port 80 (HTTP) and 443 (HTTPS)

#### Scenario: RDS security group
- **WHEN** RDS security group is configured
- **THEN** RDS allows inbound PostgreSQL traffic (port 5432) only from ECS security group

### Requirement: Environment variables management

The system SHALL support environment variables for sensitive configuration.

#### Scenario: WeChat secrets configuration
- **WHEN** application is deployed
- **THEN** WeChat AppID and AppSecret are provided via environment variables

#### Scenario: Database credentials
- **WHEN** application connects to RDS
- **THEN** database credentials are provided via environment variables from Terraform outputs

### Requirement: Docker containerization

The system SHALL provide Docker configuration for application deployment.

#### Scenario: Dockerfile presence
- **WHEN** project structure is examined
- **THEN** Dockerfile exists for building application container

#### Scenario: Docker image deployment
- **WHEN** ECS instance is provisioned
- **THEN** system can deploy Docker container running the FastAPI application

### Requirement: Terraform output variables

The system SHALL provide useful outputs from Terraform configuration.

#### Scenario: Output ECS public IP
- **WHEN** Terraform apply completes
- **THEN** output variable `ecs_public_ip` is available for API endpoint configuration

#### Scenario: Output RDS connection string
- **WHEN** Terraform apply completes
- **THEN** output variable `rds_connection_string` is available for application configuration

### Requirement: Cost minimization

The system SHALL use minimal resource specifications to minimize cost during trial phase.

#### Scenario: Minimal ECS specification
- **WHEN** ECS instance type is configured
- **THEN** instance uses smallest available specification suitable for running FastAPI application

#### Scenario: Minimal RDS specification
- **WHEN** RDS instance type is configured
- **THEN** instance uses smallest available specification suitable for single-user trial phase

### Requirement: Infrastructure destroy capability

The system SHALL support complete infrastructure teardown via Terraform.

#### Scenario: Infrastructure cleanup
- **WHEN** Terraform destroy is executed
- **THEN** all provisioned resources (ECS, RDS, VPC, security groups) are removed