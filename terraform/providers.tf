# Aliyun provider configuration
terraform {
  required_version = ">= 1.0"

  required_providers {
    alicloud = {
      source  = "aliyun/alicloud"
      version = ">= 1.180.0"
    }
  }

  backend "oss" {
    bucket = "baby-diary-sec-sh2025"
    prefix = "terraform"
    key    = "terraform.tfstate"
    region = "cn-shanghai"
  }
}

provider "alicloud" {
  region = var.region

  # 使用 aliyun CLI 的配置文件
  shared_credentials_file = pathexpand("~/.aliyun/config.json")
  profile                 = "default"
}