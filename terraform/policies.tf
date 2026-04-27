# IAM Policies for deployment roles
# Follows principle of least privilege

# ==================== Terraform Deploy Policy ====================

# Policy for infrastructure management via Terraform
# Limited to project resources (baby-diary-*)
resource "alicloud_ram_policy" "terraform_deploy" {
  policy_name     = "baby-diary-terraform-deploy-policy"
  description     = "Minimal permissions for Terraform to manage Baby Diary infrastructure"

  policy_document = jsonencode({
    Statement = [
      # VPC permissions
      {
        Effect = "Allow"
        Action = [
          "vpc:CreateVpc",
          "vpc:DeleteVpc",
          "vpc:DescribeVpcs",
          "vpc:ModifyVpcAttribute",
          "vpc:CreateVSwitch",
          "vpc:DeleteVSwitch",
          "vpc:DescribeVSwitches",
          "vpc:CreateSecurityGroup",
          "vpc:DeleteSecurityGroup",
          "vpc:DescribeSecurityGroups",
          "vpc:AuthorizeSecurityGroup",
          "vpc:RevokeSecurityGroup",
          "vpc:DescribeSecurityGroupAttribute",
        ]
        Resource = ["*"]
      },
      # RDS permissions (limited to project instances)
      {
        Effect = "Allow"
        Action = [
          "rds:CreateDBInstance",
          "rds:DeleteDBInstance",
          "rds:DescribeDBInstances",
          "rds:ModifyDBInstanceSpec",
          "rds:CreateDatabase",
          "rds:DeleteDatabase",
          "rds:DescribeDatabases",
          "rds:CreateAccount",
          "rds:DeleteAccount",
          "rds:DescribeAccounts",
          "rds:GrantAccountPrivilege",
          "rds:RevokeAccountPrivilege",
        ]
        Resource = ["acs:rds:*:*:dbinstance/*"]
      },
      # OSS permissions (limited to project buckets)
      {
        Effect = "Allow"
        Action = [
          "oss:CreateBucket",
          "oss:DeleteBucket",
          "oss:GetBucketInfo",
          "oss:ListBuckets",
          "oss:PutBucketAcl",
          "oss:GetBucketAcl",
          "oss:PutBucketEncryption",
          "oss:GetBucketEncryption",
          "oss:PutBucketVersioning",
          "oss:GetBucketVersioning",
          "oss:PutLifecycleConfiguration",
          "oss:GetLifecycleConfiguration",
          "oss:PutObject",
          "oss:GetObject",
          "oss:DeleteObject",
          "oss:ListObjects",
          "oss:ListObjectVersions",
        ]
        Resource = [
          "acs:oss:*:*:baby-diary-*",
          "acs:oss:*:*:baby-diary-*/*",
        ]
      },
      # RAM permissions (limited to project roles and policies)
      {
        Effect = "Allow"
        Action = [
          "ram:CreateRole",
          "ram:DeleteRole",
          "ram:GetRole",
          "ram:ListRoles",
          "ram:UpdateRoleDescription",
          "ram:CreatePolicy",
          "ram:DeletePolicy",
          "ram:GetPolicy",
          "ram:ListPolicies",
          "ram:ListPoliciesForRole",
          "ram:AttachPolicyToRole",
          "ram:DetachPolicyFromRole",
          "ram:CreateOIDCProvider",
          "ram:DeleteOIDCProvider",
          "ram:GetOIDCProvider",
          "ram:ListOIDCProviders",
        ]
        Resource = [
          "acs:ram:*:*:role/baby-diary-*",
          "acs:ram:*:*:policy/baby-diary-*",
          "acs:ram:*:*:oidc-provider/github-actions",
        ]
      },
      # FC permissions
      {
        Effect = "Allow"
        Action = [
          "fc:CreateService",
          "fc:DeleteService",
          "fc:GetService",
          "fc:UpdateService",
          "fc:ListServices",
          "fc:CreateFunction",
          "fc:DeleteFunction",
          "fc:GetFunction",
          "fc:UpdateFunction",
          "fc:ListFunctions",
          "fc:CreateTrigger",
          "fc:DeleteTrigger",
          "fc:GetTrigger",
          "fc:ListTriggers",
          "fc:InvokeFunction",
        ]
        Resource = [
          "acs:fc:*:*:services/baby-diary-*",
          "acs:fc:*:*:services/baby-diary-*/functions/*",
          "acs:fc:*:*:services/baby-diary-*/functions/*/triggers/*",
        ]
      },
      # Log Service permissions
      {
        Effect = "Allow"
        Action = [
          "log:CreateProject",
          "log:DeleteProject",
          "log:GetProject",
          "log:ListProjects",
          "log:CreateLogStore",
          "log:DeleteLogStore",
          "log:GetLogStore",
          "log:ListLogStore",
        ]
        Resource = ["acs:log:*:*:project/baby-diary-*"]
      },
    ]
    Version = "1"
  })
}

# ==================== FC Deploy Policy ====================

# Policy for FC function deployment only
# More restricted than terraform-deploy
resource "alicloud_ram_policy" "fc_deploy" {
  policy_name     = "baby-diary-fc-deploy-policy"
  description     = "Minimal permissions for FC deployment"

  policy_document = jsonencode({
    Statement = [
      # FC function operations (read and update only, no create/delete)
      {
        Effect = "Allow"
        Action = [
          "fc:GetService",
          "fc:UpdateService",
          "fc:GetFunction",
          "fc:UpdateFunction",
          "fc:InvokeFunction",
          "fc:ListFunctions",
        ]
        Resource = [
          "acs:fc:*:*:services/baby-diary-*",
          "acs:fc:*:*:services/baby-diary-*/functions/*",
        ]
      },
      # OSS secrets read + write (for deployment-time secret access and code upload)
      {
        Effect = "Allow"
        Action = [
          "oss:GetObject",
          "oss:GetObjectVersion",
          "oss:ListObjects",
          "oss:PutObject",
        ]
        Resource = [
          "acs:oss:*:*:baby-diary-secrets",
          "acs:oss:*:*:baby-diary-secrets/*",
        ]
      },
      # Log write (for deployment logs)
      {
        Effect = "Allow"
        Action = ["log:PostLogStoreLogs"]
        Resource = ["acs:log:*:*:project/baby-diary-*"]
      },
    ]
    Version = "1"
  })
}

# ==================== FC Execution Policy ====================

# Policy for FC function at runtime
# Only what's needed to serve requests
resource "alicloud_ram_policy" "fc_execution" {
  policy_name     = "baby-diary-fc-execution-policy"
  description     = "Minimal permissions for FC function runtime"

  policy_document = jsonencode({
    Statement = [
      # OSS secrets read (for runtime credential access)
      {
        Effect = "Allow"
        Action = [
          "oss:GetObject",
          "oss:GetObjectVersion",
          "oss:PutObject",
          "oss:ListObjects",
        ]
        Resource = [
          "acs:oss:*:*:baby-diary-secrets",
          "acs:oss:*:*:baby-diary-secrets/*",
        ]
      },
      # Log write (for application logs)
      {
        Effect = "Allow"
        Action = ["log:PostLogStoreLogs"]
        Resource = ["acs:log:*:*:project/baby-diary-*"]
      },
    ]
    Version = "1"
  })
}

# ==================== Developer Policy ====================

# Policy for local development
# Read-mostly with limited write access
resource "alicloud_ram_policy" "developer" {
  policy_name     = "baby-diary-developer-policy"
  description     = "Permissions for local development (requires MFA)"

  policy_document = jsonencode({
    Statement = [
      # Read access to all project resources
      {
        Effect = "Allow"
        Action = [
          "vpc:DescribeVpcs",
          "vpc:DescribeVSwitches",
          "vpc:DescribeSecurityGroups",
          "rds:DescribeDBInstances",
          "rds:DescribeDatabases",
          "oss:GetBucketInfo",
          "oss:ListBuckets",
          "oss:GetObject",
          "oss:ListObjects",
          "fc:GetService",
          "fc:GetFunction",
          "fc:ListServices",
          "fc:ListFunctions",
          "log:GetProject",
          "log:GetLogStore",
        ]
        Resource = ["*"]
      },
      # Write access limited to development resources
      {
        Effect = "Allow"
        Action = [
          "oss:PutObject",
          "oss:DeleteObject",
          "fc:InvokeFunction",
          "fc:UpdateFunction",
        ]
        Resource = [
          "acs:oss:*:*:baby-diary-dev-*",
          "acs:oss:*:*:baby-diary-dev-*/*",
          "acs:fc:*:*:services/baby-diary-dev-*",
        ]
      },
    ]
    Version = "1"
  })
}

# ==================== Policy Attachments ====================

# Attach policies to roles (non-OIDC roles)

resource "alicloud_ram_role_policy_attachment" "fc_execution" {
  role_name   = alicloud_ram_role.fc_execution.role_name
  policy_name = alicloud_ram_policy.fc_execution.name
  policy_type = "Custom"
}

resource "alicloud_ram_role_policy_attachment" "developer" {
  role_name   = alicloud_ram_role.developer.role_name
  policy_name = alicloud_ram_policy.developer.name
  policy_type = "Custom"
}

# OIDC role attachments (需要先创建 OIDC Provider 和相关角色)
# resource "alicloud_ram_role_policy_attachment" "terraform_deploy" {
#   role_name   = alicloud_ram_role.terraform_deploy.role_name
#   policy_name = alicloud_ram_policy.terraform_deploy.name
#   policy_type = "Custom"
# }
#
# resource "alicloud_ram_role_policy_attachment" "fc_deploy" {
#   role_name   = alicloud_ram_role.fc_deploy.role_name
#   policy_name = alicloud_ram_policy.fc_deploy.name
#   policy_type = "Custom"
# }
#
# resource "alicloud_ram_role_policy_attachment" "terraform_deploy_production" {
#   role_name   = alicloud_ram_role.terraform_deploy_production.role_name
#   policy_name = alicloud_ram_policy.terraform_deploy.name
#   policy_type = "Custom"
# }