# OIDC Provider for GitHub Actions
# 注意：阿里云 Terraform Provider 当前版本不支持 alicloud_ram_oidc_provider
# 需要通过阿里云控制台手动创建 OIDC Provider

# ==================== OIDC Provider (手动创建) ====================
# 请在阿里云 RAM 控制台创建 OIDC Provider:
# https://ram.console.aliyun.com/providers
#
# 配置步骤:
# 1. 进入 RAM 控制台 -> OIDC 身份提供商
# 2. 创建提供商:
#    - 名称: github-actions
#    - 类型: OIDC
#    - Issuer URL: https://token.actions.githubusercontent.com
#    - Client ID: github-actions
#    - 公钥指纹:
#      - CA435A638A8CFED6B89364E064E08460B91C6250
#      - 38E9B30B3A023A1B72309921A69A42FCC496C42C
#      - 4F3E9AD8C9A6F5EB3173006F4FA630E28F43DCE9
#
# 3. 创建后，提供商 ARN 格式为:
#    acs:ram::ACCOUNT_ID:oidc-provider/github-actions
#
# 4. 然后修改 roles.tf 中角色的信任策略，将 OIDC Principal 替换为:
#    "OIDC": ["acs:ram::ACCOUNT_ID:oidc-provider/github-actions"]