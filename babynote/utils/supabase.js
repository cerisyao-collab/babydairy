// utils/supabase.js
const SUPABASE_URL = 'https://aanrodgajjddpzufrqeb.supabase.co'
// 使用 anon public key（安全，推荐）
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFhbnJvZGdhampkZHB6dWZycWViIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM4MDE0ODQsImV4cCI6MjA4OTM3NzQ4NH0._071dmUhVumFu966179EACFPC8PGenQgByPlTteeIrg'

// 微信小程序 Supabase REST 客户端
class SupabaseClient {
  constructor(url, key) {
    this.url = url
    this.key = key
    this.headers = {
      'apikey': key,
      'Authorization': `Bearer ${key}`,
      'Content-Type': 'application/json'
    }
  }

  // ================= 增 =================
  async insert(table, data) {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `${this.url}/rest/v1/${table}`,
        method: 'POST',
        header: {
          ...this.headers,
          'Prefer': 'return=representation'
        },
        data: Array.isArray(data) ? data : [data],
        success: (res) => {
          if (res.statusCode === 201 || res.statusCode === 200) {
            resolve(res.data)
          } else {
            reject(new Error('插入失败，状态码：' + res.statusCode + ' ' + JSON.stringify(res.data)))
          }
        },
        fail: (err) => reject(err)
      })
    })
  }

  // ================= 查 =================
  async select(table, query = '*', filter = '') {
    return new Promise((resolve, reject) => {
      // 对 filter 中的值进行 encodeURIComponent，防止中文或特殊字符出错
      let url = `${this.url}/rest/v1/${table}?select=${query}`
      if (filter) {
        const parts = filter.split('&').map(part => {
          const [key, val] = part.split('=')
          // 只对 value 编码
          return `${key}=${encodeURIComponent(val)}`
        })
        url += '&' + parts.join('&')
      }
      wx.request({
        url,
        method: 'GET',
        header: this.headers,
        success: (res) => {
          if (res.statusCode === 200) {
            resolve(res.data)
          } else {
            reject(new Error('查询失败，状态码：' + res.statusCode + ' ' + JSON.stringify(res.data)))
          }
        },
        fail: (err) => reject(err)
      })
    })
  }

  // ================= 改 =================
  async update(table, data, filter) {
    return new Promise((resolve, reject) => {
      let url = `${this.url}/rest/v1/${table}?${filter}`
      wx.request({
        url,
        method: 'PATCH',
        header: {
          ...this.headers,
          'Prefer': 'return=representation'
        },
        data,
        success: (res) => {
          if (res.statusCode === 200) {
            resolve(res.data)
          } else {
            reject(new Error('更新失败，状态码：' + res.statusCode + ' ' + JSON.stringify(res.data)))
          }
        },
        fail: (err) => reject(err)
      })
    })
  }

  // ================= 删 =================
  async delete(table, filter) {
    return new Promise((resolve, reject) => {
      let url = `${this.url}/rest/v1/${table}?${filter}`
      wx.request({
        url,
        method: 'DELETE',
        header: {
          ...this.headers,
          'Prefer': 'return=representation'
        },
        success: (res) => {
          if (res.statusCode === 200 || res.statusCode === 204) {
            resolve(res.data)
          } else {
            reject(new Error('删除失败，状态码：' + res.statusCode + ' ' + JSON.stringify(res.data)))
          }
        },
        fail: (err) => reject(err)
      })
    })
  }

  // ================= 查询最近记录 =================
  async getRecentRecords(limit = 10) {
    return this.select('records', '*', `order=created_at.desc&limit=${limit}`)
  }
}

const supabase = new SupabaseClient(SUPABASE_URL, SUPABASE_ANON_KEY)

module.exports = { supabase, SUPABASE_URL, SUPABASE_ANON_KEY }