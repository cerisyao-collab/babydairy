# Terraform Deployment Guide for Baby Diary API

## Overview

This guide explains how to deploy the Baby Diary API to Aliyun using Terraform.

## Prerequisites

1. **Aliyun Account** with AccessKey and SecretKey
2. **Terraform** installed (>= 1.0)
3. **Aliyun CLI** (optional, for verification)

## Cost Estimate

| Resource | Specification | Monthly Cost (Estimated) |
|----------|---------------|--------------------------|
| ECS | ecs.tiny-c1m1.small (1核1G) | ~40-60 CNY |
| RDS PostgreSQL | postgres.n4.small.1 (1核1G, 20GB) | ~50-80 CNY |
| **Total** | | **~90-140 CNY/month** |

*Note: Prices vary by region. Trial phase uses PostPaid (按量付费) for flexibility.*

## Quick Start

### 1. Set Environment Variables

```bash
# Aliyun credentials
export ALICLOUD_ACCESS_KEY="your-access-key"
export ALICLOUD_SECRET_KEY="your-secret-key"

# Sensitive configuration
export TF_VAR_db_password="your-db-password"
export TF_VAR_wechat_app_id="your-wechat-app-id"
export TF_VAR_wechat_app_secret="your-wechat-app-secret"
export TF_VAR_jwt_secret="your-jwt-secret"
```

### 2. Initialize Terraform

```bash
cd terraform
terraform init
```

### 3. Review Plan

```bash
terraform plan -out=tfplan
```

### 4. Apply Configuration

```bash
terraform apply tfplan
```

### 5. Get Outputs

```bash
terraform output
```

This will show:
- `ecs_public_ip`: SSH and API endpoint
- `rds_connection_string`: Database connection
- `database_url`: Full connection string for app config

## Deployment Steps

After Terraform creates resources, follow these steps:

### 1. SSH into ECS

```bash
ssh root@<ecs_public_ip>
```

### 2. Install Docker

```bash
curl -fsSL https://get.docker.com | sh
systemctl enable docker
systemctl start docker
```

### 3. Build Docker Image

```bash
# On your development machine
docker build -t baby-diary-api .
docker save baby-diary-api > baby-diary-api.tar

# Transfer to ECS
scp baby-diary-api.tar root@<ecs_public_ip>:/root/

# On ECS
docker load -i baby-diary-api.tar
```

### 4. Run Container

```bash
docker run -d \
  --name baby-diary \
  --restart unless-stopped \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://baby_diary:<password>@<rds-connection>:5432/baby_diary" \
  -e WECHAT_APP_ID="<your-app-id>" \
  -e WECHAT_APP_SECRET="<your-app-secret>" \
  -e JWT_SECRET="<your-jwt-secret>" \
  baby-diary-api
```

### 5. Run Database Migrations

```bash
docker exec baby-diary alembic upgrade head
```

### 6. Verify Deployment

```bash
curl http://<ecs_public_ip>:8000/api/health
```

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

**Warning**: This will delete ECS, RDS, and all data. Back up database before destroying.

## Troubleshooting

### ECS Connection Issues

- Check security group allows port 22 for SSH
- Verify `allocate_public_ip = true` in Terraform config

### RDS Connection Issues

- Check security group allows port 5432 from ECS subnet
- Verify `security_ips` includes ECS subnet (10.0.1.0/24)

### Application Errors

- Check Docker logs: `docker logs baby-diary`
- Verify environment variables are set correctly
- Ensure migrations ran: `docker exec baby-diary alembic current`

## Production Considerations

For production deployment:

1. **OSS Backend**: Use Aliyun OSS for Terraform state storage
2. **Domain & HTTPS**: Configure domain with SSL certificate
3. **Monitoring**: Add Aliyun CloudMonitor for alerts
4. **Backup**: Enable RDS automatic backup
5. **Security**: Restrict `allowed_ssh_cidr` to specific IPs
6. **Scale**: Upgrade instance types when needed

## File Structure

```
terraform/
├── providers.tf    # Aliyun provider configuration
├── variables.tf    # Input variables
├── main.tf         # Resource definitions
├── outputs.tf      # Output values
└── README.md       # This guide
```