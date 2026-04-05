# Terraform variables for Aliyun infrastructure (FC + RDS)

variable "region" {
  description = "Aliyun region for resources"
  type        = string
  default     = "cn-hangzhou"
}

variable "availability_zone" {
  description = "Availability zone within the region"
  type        = string
  default     = "cn-hangzhou-h"
}

variable "instance_name" {
  description = "Name prefix for all resources"
  type        = string
  default     = "baby-diary"
}

# RDS Configuration
variable "rds_instance_type" {
  description = "RDS instance type (Serverless for FC)"
  type        = string
  default     = "serverless.n4.small.1"  # Serverless 规格
}

variable "rds_storage_size" {
  description = "RDS storage size in GB"
  type        = number
  default     = 20
}

variable "db_username" {
  description = "PostgreSQL database username"
  type        = string
  default     = "baby_diary"
}

variable "db_password" {
  description = "PostgreSQL database password"
  type        = string
  sensitive   = true
}

variable "db_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "baby_diary"
}

# FC Configuration
variable "fc_service_name" {
  description = "FC service name"
  type        = string
  default     = "baby-diary-service"
}

variable "fc_function_name" {
  description = "FC function name"
  type        = string
  default     = "api"
}

variable "fc_memory_size" {
  description = "FC function memory size in MB"
  type        = number
  default     = 256
}

variable "fc_timeout" {
  description = "FC function timeout in seconds"
  type        = number
  default     = 30
}

# WeChat Configuration
variable "wechat_app_id" {
  description = "WeChat Mini-program AppID"
  type        = string
  sensitive   = true
}

variable "wechat_app_secret" {
  description = "WeChat Mini-program AppSecret"
  type        = string
  sensitive   = true
}

variable "jwt_secret" {
  description = "JWT secret key for token signing"
  type        = string
  sensitive   = true
}

# LLM Configuration
variable "dashscope_api_key" {
  description = "Alibaba Cloud DashScope API key for LLM"
  type        = string
  sensitive   = true
  default     = ""
}

# KMS Configuration (encrypted secrets)
variable "encrypted_db_password" {
  description = "KMS-encrypted database password (base64 encoded ciphertext)"
  type        = string
  default     = ""
}

variable "encrypted_wechat_app_secret" {
  description = "KMS-encrypted WeChat app secret (base64 encoded ciphertext)"
  type        = string
  default     = ""
}

variable "encrypted_dashscope_api_key" {
  description = "KMS-encrypted DashScope API key (base64 encoded ciphertext)"
  type        = string
  default     = ""
}

variable "encrypted_jwt_secret" {
  description = "KMS-encrypted JWT secret (base64 encoded ciphertext)"
  type        = string
  default     = ""
}

# OIDC Configuration for GitHub Actions
variable "github_oidc_fingerprints" {
  description = "GitHub OIDC public key fingerprints for token verification"
  type        = list(string)
  default     = []
  # Obtain from: https://token.actions.githubusercontent.com/.well-known/jwks
  # Example: ["a0sha1fingerprint..."]
}

variable "github_repository" {
  description = "GitHub repository in format 'owner/repo' for OIDC subject restriction"
  type        = string
  default     = "your-org/babyjour"
}