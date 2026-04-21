// utils/config.js - API 端点配置

// FC HTTP 触发器 URL
const PROD_API_BASE_URL = 'https://api-baby-di-service-lcajvpgpkx.cn-shanghai.fcapp.run'
const DEV_API_BASE_URL = 'http://localhost:3000'

// 当前环境（手动切换：'production' | 'development'）
const ENV = 'production'

// 获取当前环境的 API 基础地址
function getApiBaseUrl() {
  return ENV === 'production' ? PROD_API_BASE_URL : DEV_API_BASE_URL
}

module.exports = {
  ENV,
  PROD_API_BASE_URL,
  DEV_API_BASE_URL,
  getApiBaseUrl
}
