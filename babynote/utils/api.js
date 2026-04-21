// utils/api.js - FC 后端 API 客户端
const { getApiBaseUrl } = require('./config')

// ================= 登录 =================

/**
 * 微信登录：使用 wx.login 获取 code，换取 JWT token
 */
function login() {
  return new Promise((resolve, reject) => {
    wx.login({
      success: (loginRes) => {
        if (!loginRes.code) {
          reject(new Error('微信登录失败，未获取到 code'))
          return
        }
        console.log('wx.login code:', loginRes.code.substring(0, 10) + '...')
        wx.request({
          url: `${getApiBaseUrl()}/api/auth/login`,
          method: 'POST',
          header: { 'Content-Type': 'application/json' },
          data: { code: loginRes.code },
          success: (res) => {
            console.log('登录响应 status:', res.statusCode)
            if (res.statusCode === 200) {
              const data = res.data
              console.log('login response:', data.token ? 'has token' : 'no token')
              // 保存 token 和用户信息
              wx.setStorageSync('token', data.token)
              wx.setStorageSync('userInfo', {
                userId: data.openid,
                openid: data.openid,
                nickName: data.nickname || '',
                avatarUrl: data.avatar_url || ''
              })
              resolve(data)
            } else {
              const msg = res.data?.detail || `服务器错误 (${res.statusCode})`
              reject(new Error(typeof msg === 'string' ? msg : JSON.stringify(msg)))
            }
          },
          fail: (err) => reject(new Error('网络请求失败: ' + err.errMsg))
        })
      },
      fail: (err) => reject(new Error('wx.login 失败: ' + err.errMsg))
    })
  })
}

/**
 * 获取当前 token
 */
function getToken() {
  return wx.getStorageSync('token') || null
}

/**
 * 清除登录状态
 */
function logout() {
  wx.removeStorageSync('token')
  wx.removeStorageSync('userInfo')
}

// ================= 请求封装 =================

function request(method, path, data) {
  return new Promise((resolve, reject) => {
    const token = getToken()
    const header = { 'Content-Type': 'application/json' }
    if (token) {
      header['Authorization'] = `Bearer ${token}`
    }

    wx.request({
      url: `${getApiBaseUrl()}${path}`,
      method,
      header,
      data: data || undefined,
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else if (res.statusCode === 401) {
          // token 过期，清除登录状态
          logout()
          reject(new Error('登录已过期，请重新登录'))
        } else {
          const msg = res.data?.detail || res.data?.message || `请求失败 (${res.statusCode})`
          reject(typeof msg === 'string' ? new Error(msg) : new Error(JSON.stringify(msg)))
        }
      },
      fail: (err) => reject(new Error(err.errMsg || '网络请求失败'))
    })
  })
}

// ================= 记录管理 =================

/**
 * 创建记录
 */
function createRecord(type, details, timestamp) {
  return request('POST', '/api/records/', {
    type,
    details: details || {},
    timestamp,
    skip_duplicate_check: true
  })
}

/**
 * 查询记录
 */
function listRecords(options = {}) {
  const params = []
  if (options.start_date) params.push(`start_date=${options.start_date}`)
  if (options.end_date) params.push(`end_date=${options.end_date}`)
  if (options.type) params.push(`type=${options.type}`)
  const query = params.length ? `?${params.join('&')}` : ''
  return request('GET', `/api/records/${query}`).then(res => res.records || [])
}

/**
 * 删除记录
 */
function deleteRecord(id) {
  return request('DELETE', `/api/records/${id}`)
}

/**
 * 获取单条记录
 */
function getRecord(id) {
  return request('GET', `/api/records/${id}`)
}

/**
 * 更新记录
 */
function updateRecord(id, updates) {
  return request('PUT', `/api/records/${id}`, updates)
}

// ================= 宝宝配置 =================

/**
 * 获取宝宝配置
 */
function getBabyConfig() {
  return request('GET', '/api/config/baby')
}

/**
 * 更新宝宝配置
 */
function updateBabyConfig(data) {
  return request('PUT', '/api/config/baby', data)
}

// ================= 用户信息 =================

/**
 * 获取用户信息
 */
function getUserProfile() {
  return request('GET', '/api/auth/profile')
}

/**
 * 更新用户信息
 */
function updateUserProfile(data) {
  return request('PUT', '/api/auth/profile', data)
}

module.exports = {
  login,
  logout,
  getToken,
  createRecord,
  listRecords,
  deleteRecord,
  getRecord,
  updateRecord,
  getBabyConfig,
  updateBabyConfig,
  getUserProfile,
  updateUserProfile
}
