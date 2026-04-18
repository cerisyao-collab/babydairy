// utils/config.js - API 端点配置

// FC HTTP 触发器 URL 格式:
// https://{accountId}.{region}.fcapp.run/{serviceName}/{functionName}
// 或: https://{functionName}.{serviceName}.{accountId}.{region}.fcapp.run
// 部署后从 FC 控制台或 s deploy 输出中获取实际 URL

const FC_ACCOUNT_ID = '1031059086324334'
const FC_REGION = 'cn-shanghai'
const FC_SERVICE_NAME = 'baby-diary-service'
const FC_FUNCTION_NAME = 'api'

// 生产环境 API 地址（FC HTTP 触发器 URL）
const PROD_API_BASE_URL = 'https://api-baby-di-service-lcajvpgpkx.cn-shanghai.fcapp.run'

// 开发环境 API 地址（可选：本地代理或测试环境）
const DEV_API_BASE_URL = 'http://localhost:3000'

// 当前环境（手动切换：'production' | 'development'）
const ENV = 'production'

// 获取当前环境的 API 基础地址
function getApiBaseUrl() {
  return ENV === 'production' ? PROD_API_BASE_URL : DEV_API_BASE_URL
}

// 是否跳过合法域名校验（仅开发环境使用）
const SKIP_DOMAIN_CHECK = ENV === 'development'

module.exports = {
  ENV,
  PROD_API_BASE_URL,
  DEV_API_BASE_URL,
  FC_ACCOUNT_ID,
  FC_REGION,
  FC_SERVICE_NAME,
  FC_FUNCTION_NAME,
  getApiBaseUrl,
  SKIP_DOMAIN_CHECK
}
