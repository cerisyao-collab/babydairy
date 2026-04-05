# RAM Roles for deployment and runtime
# Follows principle of least privilege

# ==================== OIDC Provider ARN Variable ====================
# OIDC Provider 需要手动在阿里云控制台创建
# 创建后将 ARN 值填入 terraform.tfvars 的 oidc_provider_arn 变量
# 格式: acs:ram::ACCOUNT_ID:oidc-provider/github-actions

# ==================== FC Execution Role ====================

# Role assumed by FC function at runtime
# Trusted only by FC service, not by OIDC
resource "alicloud_ram_role" "fc_execution" {
  role_name                   = "baby-diary-fc-execution"
  description                 = "Role assumed by FC function at runtime"

  assume_role_policy_document = jsonencode({
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = ["fc.aliyuncs.com"]
      }
    }]
    Version = "1"
  })
}

# ==================== Developer Role ====================

# Role for local development
# Requires MFA for assumption
resource "alicloud_ram_role" "developer" {
  role_name                   = "baby-diary-developer"
  description                 = "Role for local development with MFA required"

  assume_role_policy_document = jsonencode({
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          RAM = ["acs:ram::1031059086324334:root"]
        }
        Condition = {
          Bool = {
            "acs:MFAPresent" = "true"
          }
        }
      }
    ]
    Version = "1"
  })
}

# ==================== OIDC Roles (需要先创建 OIDC Provider) ====================
# 以下角色依赖 OIDC Provider，需要先在阿里云控制台创建 OIDC Provider
# 然后取消注释并运行 terraform apply

# Role for infrastructure deployment via Terraform
# Can be assumed by GitHub Actions via OIDC
# resource "alicloud_ram_role" "terraform_deploy" {
#   role_name                   = "baby-diary-terraform-deploy"
#   description                 = "Role for Terraform to manage Baby Diary infrastructure"
#
#   assume_role_policy_document = jsonencode({
#     Statement = [{
#       Action = "sts:AssumeRole"
#       Effect = "Allow"
#       Principal = {
#         OIDC = [var.oidc_provider_arn]
#       }
#       Condition = {
#         StringEquals = {
#           "token.actions.githubusercontent.com:aud" = "github-actions"
#         }
#         StringLike = {
#           "token.actions.githubusercontent.com:sub" = "repo:${var.github_repository}:*"
#         }
#       }
#     }]
#     Version = "1"
#   })
# }

# Role for FC function deployment via Serverless Devs
# resource "alicloud_ram_role" "fc_deploy" {
#   role_name                   = "baby-diary-fc-deploy"
#   description                 = "Role for FC function deployment"
#
#   assume_role_policy_document = jsonencode({
#     Statement = [{
#       Action = "sts:AssumeRole"
#       Effect = "Allow"
#       Principal = {
#         OIDC = [var.oidc_provider_arn]
#       }
#       Condition = {
#         StringEquals = {
#           "token.actions.githubusercontent.com:aud" = "github-actions"
#         }
#         StringLike = {
#           "token.actions.githubusercontent.com:sub" = "repo:${var.github_repository}:*"
#         }
#       }
#     }]
#     Version = "1"
#   })
# }

# Production deploy role (main branch only)
# resource "alicloud_ram_role" "terraform_deploy_production" {
#   role_name                   = "baby-diary-terraform-deploy-prod"
#   description                 = "Role for production deployment (main branch only)"
#
#   assume_role_policy_document = jsonencode({
#     Statement = [{
#       Action = "sts:AssumeRole"
#       Effect = "Allow"
#       Principal = {
#         OIDC = [var.oidc_provider_arn]
#       }
#       Condition = {
#         StringEquals = {
#           "token.actions.githubusercontent.com:aud" = "github-actions"
#         }
#         StringLike = {
#           "token.actions.githubusercontent.com:sub" = "repo:${var.github_repository}:ref:refs/heads/main"
#         }
#       }
#     }]
#     Version = "1"
#   })
# }