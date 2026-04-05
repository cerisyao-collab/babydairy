# Terraform outputs (FC + RDS)

# ==================== Infrastructure Outputs ====================

output "vpc_id" {
  description = "VPC ID for FC function configuration"
  value       = alicloud_vpc.main.id
}

output "vswitch_id" {
  description = "VSwitch ID for FC function configuration"
  value       = alicloud_vswitch.rds.id
}

output "security_group_id" {
  description = "Security Group ID for FC function configuration"
  value       = alicloud_security_group.rds.id
}

output "rds_connection_string" {
  description = "RDS PostgreSQL connection string"
  value       = alicloud_db_instance.postgres.connection_string
}

output "rds_port" {
  description = "RDS PostgreSQL port"
  value       = alicloud_db_instance.postgres.port
}

output "database_url" {
  description = "Full PostgreSQL connection URL (for s.yaml environment)"
  value       = "postgresql://${var.db_username}:${var.db_password}@${alicloud_db_instance.postgres.connection_string}:${alicloud_db_instance.postgres.port}/${var.db_name}"
  sensitive   = true
}

# ==================== OSS Outputs ====================

output "oss_secrets_bucket" {
  description = "OSS bucket name for secrets storage"
  value       = alicloud_oss_bucket.secrets.bucket
}

# ==================== RAM Role Outputs ====================

output "fc_execution_role_arn" {
  description = "ARN of the FC execution role"
  value       = alicloud_ram_role.fc_execution.arn
}

output "developer_role_arn" {
  description = "ARN of the developer role"
  value       = alicloud_ram_role.developer.arn
}

# ==================== OIDC Outputs ====================

output "oidc_provider_arn" {
  description = "ARN of the GitHub OIDC Provider"
  value       = "acs:ram::1031059086324334:oidc-provider/github-actions"
}

output "terraform_deploy_role_arn" {
  description = "ARN of the Terraform deploy role (OIDC)"
  value       = "acs:ram::1031059086324334:role/baby-diary-terraform-deploy"
}

output "fc_deploy_role_arn" {
  description = "ARN of the FC deploy role (OIDC)"
  value       = "acs:ram::1031059086324334:role/baby-diary-fc-deploy"
}

# ==================== FC Config Summary ====================

output "fc_config" {
  description = "FC configuration for s.yaml"
  value = {
    vpcId            = alicloud_vpc.main.id
    vswitchId        = alicloud_vswitch.rds.id
    securityGroupId  = alicloud_security_group.rds.id
    ossSecretsBucket = alicloud_oss_bucket.secrets.bucket
  }
}

output "github_actions_secrets" {
  description = "Secrets configured in GitHub repository"
  value = {
    OIDC_PROVIDER_ARN         = "acs:ram::1031059086324334:oidc-provider/github-actions"
    TERRAFORM_DEPLOY_ROLE_ARN = "acs:ram::1031059086324334:role/baby-diary-terraform-deploy"
    FC_DEPLOY_ROLE_ARN        = "acs:ram::1031059086324334:role/baby-diary-fc-deploy"
    VPC_ID                    = alicloud_vpc.main.id
    VSWITCH_ID                = alicloud_vswitch.rds.id
    SECURITY_GROUP_ID         = alicloud_security_group.rds.id
    OSS_SECRETS_BUCKET        = alicloud_oss_bucket.secrets.bucket
  }
}

output "deployment_instructions" {
  description = "Instructions for deploying with OIDC"
  value       = <<-EOT
    ====== OIDC 部署已完成 ======

    所有基础设施已创建完成！

    GitHub Secrets 已配置:
    - OIDC_PROVIDER_ARN
    - TERRAFORM_DEPLOY_ROLE_ARN
    - FC_DEPLOY_ROLE_ARN
    - VPC_ID, VSWITCH_ID, SECURITY_GROUP_ID
    - OSS_SECRETS_BUCKET
    - DATABASE_URL

    下一步:
    1. 推送代码到 main 分支触发部署:
       git push origin main

    2. 查看 GitHub Actions 运行状态

    3. 确认部署成功后，禁用长期 AccessKey

    详细文档: docs/deploy-security.md
  EOT
}