// utils/api.js - FC 后端 API 客户端
const { getApiBaseUrl } = require('./config')

/**
 * 解析 FC 响应
 * FC 使用 Lambda 代理格式：{statusCode, headers, body, isBase64Encoded}
 * body 是 JSON 字符串，需要手动解析
 */
function parseFCResponse(res) {
  // 如果 res.data 是字符串（Lambda 代理格式），解析 body 字段
  if (typeof res.data === 'string') {
    try {
      const parsed = JSON.parse(res.data)
      return {
        statusCode: parsed.statusCode || res.statusCode,
        data: parsed.body && typeof parsed.body === 'string' ? JSON.parse(parsed.body) : parsed
      }
    } catch {
      return { statusCode: res.statusCode, data: null }
    }
  }
  // 如果 res.data 有 body 字段且是字符串（FC 直接返回）
  if (res.data && typeof res.data.body === 'string') {
    try {
      const bodyData = JSON.parse(res.data.body)
      return {
        statusCode: res.data.statusCode || res.statusCode,
        data: bodyData
      }
    } catch {
      return { statusCode: res.statusCode, data: null }
    }
  }
  return { statusCode: res.statusCode, data: res.data }
}

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
            console.log('=== raw res ===')
            console.log('res.statusCode:', res.statusCode)
            console.log('typeof res.data:', typeof res.data)
            console.log('res.data:', res.data)
            const { statusCode, data } = parseFCResponse(res)
            console.log('=== parsed ===')
            console.log('statusCode:', statusCode)
            console.log('data type:', typeof data)
            console.log('data keys:', data ? Object.keys(data) : 'null')
            console.log('has token:', !!data?.token)
            if (statusCode === 200 && data && data.token) {
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
              const msg = data?.detail || data?.error?.message || `服务器错误 (${statusCode})`
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
        const { statusCode, data: parsedData } = parseFCResponse(res)
        if (statusCode >= 200 && statusCode < 300) {
          resolve(parsedData)
        } else if (statusCode === 401) {
          logout()
          reject(new Error('登录已过期，请重新登录'))
        } else {
          const msg = parsedData?.detail || parsedData?.error?.message || `请求失败 (${statusCode})`
          reject(typeof msg === 'string' ? new Error(msg) : new Error(JSON.stringify(msg)))
        }
      },
      fail: (err) => reject(new Error(err.errMsg || '网络请求失败'))
    })
  })
}

// ================= 记录管理 =================

function createRecord(type, details, timestamp) {
  return request('POST', '/api/records/', {
    type,
    details: details || {},
    timestamp,
    skip_duplicate_check: true
  })
}

function listRecords(options = {}) {
  const params = []
  if (options.start_date) params.push(`start_date=${options.start_date}`)
  if (options.end_date) params.push(`end_date=${options.end_date}`)
  if (options.type) params.push(`type=${options.type}`)
  const query = params.length ? `?${params.join('&')}` : ''
  return request('GET', `/api/records/${query}`).then(res => res.records || [])
}

function deleteRecord(id) {
  return request('DELETE', `/api/records/${id}`)
}

function getRecord(id) {
  return request('GET', `/api/records/${id}`)
}

function updateRecord(id, updates) {
  return request('PUT', `/api/records/${id}`, updates)
}

// ================= 宝宝配置 =================

function getBabyConfig() {
  return request('GET', '/api/config/baby')
}

function updateBabyConfig(data) {
  return request('PUT', '/api/config/baby', data)
}

// ================= 用户信息 =================

function getUserProfile() {
  return request('GET', '/api/auth/profile')
}

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
