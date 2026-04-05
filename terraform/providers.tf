# Aliyun provider configuration
terraform {
  required_version = ">= 1.0"

  required_providers {
    alicloud = {
      source  = "aliyun/alicloud"
      version = ">= 1.180.0"
    }
  }

  # Backend for state storage (local for trial)
  # For production, use OSS backend:
  # backend "oss" {
  #   bucket = "your-terraform-state-bucket"
  #   prefix = "baby-diary/"
  # }
}

provider "alicloud" {
  region = var.region

  # 使用 aliyun CLI 的配置文件
  shared_credentials_file = pathexpand("~/.aliyun/config.json")
  profile                 = "default"
}