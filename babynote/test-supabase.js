// test-supabase.js - 测试 Supabase 连接
// 在微信开发者工具的控制台直接运行这个

const SUPABASE_URL = 'https://aanrodgajjddpzufrqeb.supabase.co'
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFhbnJvZGdhampkZHB6dWZycWViIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM4MDE0ODQsImV4cCI6MjA4OTM3NzQ4NH0._071dmUhVumFu966179EACFPC8PGenQgByPlTteeIrg'

// 测试插入
wx.request({
  url: `${SUPABASE_URL}/rest/v1/records`,
  method: 'POST',
  header: {
    'apikey': SUPABASE_ANON_KEY,
    'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
  },
  data: {
    type: 'feeding',
    user_id: 'test_user',
    user_name: '测试'
  },
  success: (res) => {
    console.log('✅ 插入成功！', res.statusCode, res.data)
  },
  fail: (err) => {
    console.error('❌ 插入失败', err)
  }
})

// 测试查询
wx.request({
  url: `${SUPABASE_URL}/rest/v1/records?select=*&order=created_at.desc&limit=5`,
  method: 'GET',
  header: {
    'apikey': SUPABASE_ANON_KEY,
    'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
    'Content-Type': 'application/json'
  },
  success: (res) => {
    console.log('✅ 查询成功！', res.statusCode, res.data)
  },
  fail: (err) => {
    console.error('❌ 查询失败', err)
  }
})
