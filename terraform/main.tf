# Main Terraform configuration for Baby Diary API (FC + RDS)
# 适用于函数计算部署的基础设施

# ==================== OSS 密钥存储 ====================

# OSS Bucket 用于存储加密的主密钥和凭证
# 使用 SSE-OSS 服务端加密，无额外 KMS 费用
resource "alicloud_oss_bucket" "secrets" {
  bucket = "baby-diary-sec-sh2025"

  # 启用服务端加密 (SSE-OSS，阿里云托管密钥，免费)
  server_side_encryption_rule {
    sse_algorithm = "AES256"
  }

  # 启用版本控制（用于密钥备份和恢复）
  versioning {
    status = "Enabled"
  }

  # 生命周期规则：保留历史版本 90 天
  lifecycle_rule {
    id      = "keep-old-versions"
    enabled = true

    noncurrent_version_expiration {
      days = 90
    }
  }

  tags = {
    Name    = "${var.instance_name}-secrets-bucket"
    Project = "baby-diary"
  }
}

# RAM Policy 限制 OSS bucket 仅 FC 角色可访问
resource "alicloud_ram_policy" "secrets_bucket_access" {
  policy_name     = "${var.instance_name}-secrets-bucket-access"
  policy_document = jsonencode({
    Statement = [
      {
        Action = [
          "oss:GetObject",
          "oss:GetObjectVersion",
          "oss:PutObject",
          "oss:DeleteObject",
          "oss:ListObjects",
          "oss:ListObjectVersions"
        ]
        Effect   = "Allow"
        Resource = [
          "acs:oss:*:*:${alicloud_oss_bucket.secrets.bucket}",
          "acs:oss:*:*:${alicloud_oss_bucket.secrets.bucket}/*"
        ]
      }
    ]
    Version = "1"
  })
  description = "Policy for FC to access secrets OSS bucket"
}

# 将 Policy 绑定到 FC 执行角色（假设角色已存在或通过 s.yaml 创建）
# 注意：FC 角色通常通过 Serverless Devs (s.yaml) 管理
# 此处输出 Policy 名称供 FC 配置引用

# ==================== 密钥轮换定时任务 ====================
# FC 定时触发器通过 Serverless Devs (s.yaml) 配置
# 定时触发器配置示例（30 天检查周期）:
# triggers:
#   - name: key-rotation-trigger
#     type: timer
#     config:
#       cronExpression: "CRON_TZ=Asia/Shanghai 0 0 1 */1 *"  # 每月1日0点
#       enable: true

# RAM Policy for key rotation function
resource "alicloud_ram_policy" "key_rotation_access" {
  policy_name     = "${var.instance_name}-key-rotation-access"
  policy_document = jsonencode({
    Statement = [
      {
        Action = [
          "oss:GetObject",
          "oss:GetObjectVersion",
          "oss:PutObject",
          "oss:ListObjects",
          "oss:ListObjectVersions",
          "log:PostLogStoreLogs"
        ]
        Effect   = "Allow"
        Resource = [
          "acs:oss:*:*:${alicloud_oss_bucket.secrets.bucket}",
          "acs:oss:*:*:${alicloud_oss_bucket.secrets.bucket}/*"
        ]
      },
      {
        Action = ["log:PostLogStoreLogs"]
        Effect = "Allow"
        Resource = ["*"]
      }
    ]
    Version = "1"
  })
  description = "Policy for FC key rotation function"
}

# ==================== VPC 配置 ====================
resource "alicloud_vpc" "main" {
  vpc_name  = "${var.instance_name}-vpc"
  cidr_block = "10.0.0.0/16"

  tags = {
    Name    = "${var.instance_name}-vpc"
    Project = "baby-diary"
  }
}

# VSwitch for RDS (FC 会自动使用此 VSwitch)
resource "alicloud_vswitch" "rds" {
  vswitch_name = "${var.instance_name}-rds-vswitch"
  vpc_id       = alicloud_vpc.main.id
  cidr_block   = "10.0.1.0/24"
  zone_id      = var.availability_zone

  tags = {
    Name    = "${var.instance_name}-rds-vswitch"
    Project = "baby-diary"
  }
}

# Security Group for RDS (允许 FC 访问)
resource "alicloud_security_group" "rds" {
  security_group_name = "${var.instance_name}-rds-sg"
  vpc_id              = alicloud_vpc.main.id

  tags = {
    Name    = "${var.instance_name}-rds-sg"
    Project = "baby-diary"
  }
}

# Allow PostgreSQL from VPC (FC 函数在 VPC 内)
resource "alicloud_security_group_rule" "allow_postgres" {
  type              = "ingress"
  ip_protocol       = "tcp"
  port_range        = "5432/5432"
  security_group_id = alicloud_security_group.rds.id
  cidr_ip           = "10.0.0.0/16"  # 允许 VPC 内所有访问
  priority          = 1
}

# RDS PostgreSQL Instance (按量付费)
resource "alicloud_db_instance" "postgres" {
  engine               = "PostgreSQL"
  engine_version       = "14.0"
  instance_name        = "${var.instance_name}-db"
  vswitch_id           = alicloud_vswitch.rds.id

  # 按量付费 - 使用变量配置规格
  instance_charge_type = "Postpaid"
  instance_type        = var.rds_instance_type
  instance_storage     = var.rds_storage_size

  # Security group
  security_group_ids   = [alicloud_security_group.rds.id]

  # 白名单 - 允许 VPC 内访问
  security_ips         = ["10.0.0.0/16"]

  tags = {
    Name    = "${var.instance_name}-db"
    Project = "baby-diary"
  }
}

# RDS Account
resource "alicloud_db_account" "main" {
  instance_id      = alicloud_db_instance.postgres.id
  account_name     = var.db_username
  account_password = var.db_password
  account_type     = "Normal"
}

# RDS Database
resource "alicloud_db_database" "main" {
  instance_id   = alicloud_db_instance.postgres.id
  name          = var.db_name
  character_set = "UTF8"
}

# FC 服务需要手动配置 VPC，这里输出 VPC 信息供 s.yaml 使用
# FC 函数通过 Serverless Devs 部署，不通过 Terraform