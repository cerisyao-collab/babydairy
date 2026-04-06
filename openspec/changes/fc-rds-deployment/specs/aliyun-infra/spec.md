## MODIFIED Requirements

### Requirement: Aliyun RDS PostgreSQL

The system SHALL provision a minimal RDS PostgreSQL instance.

#### Scenario: RDS PostgreSQL provisioning
- **WHEN** Terraform apply is executed
- **THEN** RDS PostgreSQL Serverless instance is created with minimal specification

#### Scenario: RDS private network
- **WHEN** RDS instance is provisioned
- **THEN** RDS is accessible only from FC functions via internal VPC network

### Requirement: VPC and security groups

The system SHALL configure VPC and security groups for network security.

#### Scenario: VPC creation
- **WHEN** Terraform apply is executed
- **THEN** VPC is created with CIDR block for FC and RDS

#### Scenario: RDS security group
- **WHEN** RDS security group is configured
- **THEN** RDS allows inbound PostgreSQL traffic (port 5432) only from FC function's VPC

## REMOVED Requirements

### Requirement: Aliyun ECS instance

**Reason**: Replaced by Function Compute for serverless deployment
**Migration**: Use FC deployment with `s deploy` instead of ECS with Docker

### Requirement: ECS security group

**Reason**: ECS is removed; FC handles its own security through VPC configuration
**Migration**: FC security is managed through function-level VPC configuration in s.yaml

### Requirement: Docker containerization

**Reason**: FC handles containerization automatically
**Migration**: No Dockerfile needed; FC builds from source code directly

### Requirement: ECS public IP

**Reason**: FC provides built-in HTTP endpoint
**Migration**: Use FC HTTP trigger URL as API endpoint