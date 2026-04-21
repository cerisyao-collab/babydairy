// pages/mine/mine.js
const api = require('../../utils/api')
const { formatRecordTime, formatRecordType, formatRecordValue } = require('../../utils/recordFormat')

// FC 后端记录类型映射
const RECORD_TYPE_NAMES = {
  'feeding': '喂奶', 'bowel': '大便', 'urine': '小便',
  'medication': '营养品', 'bathing': '洗澡', 'sleep': '睡眠',
  'growth': '生长指标', 'illness': '病情'
}

Page({
  data: {
    userInfo: null,
    hasAuth: false,
    babyConfig: { baby_name: '宝宝', gender: 'unknown', birth_date: null, birth_weight: null },
    myRecords: []
  },

  async onLoad() {
    // 检查登录状态
    const token = api.getToken()
    const userInfo = wx.getStorageSync('userInfo')
    if (token && userInfo) {
      this.setData({ userInfo, hasAuth: true })
      await Promise.all([
        this.loadBabyConfig(),
        this.loadMyRecords()
      ])
    }
  },

  onShow() {
    if (this.data.hasAuth) {
      this.loadBabyConfig()
      this.loadMyRecords()
    }
  },

  // ================= 登录 =================
  async handleLogin() {
    wx.showLoading({ title: '登录中...' })
    try {
      const data = await api.login()
      console.log('登录成功，token:', !!data.token)
      const userInfo = {
        userId: data.openid,
        openid: data.openid,
        nickName: data.nickname || '宝宝家长',
        avatarUrl: data.avatar_url || ''
      }
      this.setData({ userInfo, hasAuth: true, babyConfig: null })
      // 验证 token 确实存储了
      const savedToken = wx.getStorageSync('token')
      console.log('storage token:', !!savedToken)
      wx.hideLoading()
      wx.showToast({ title: '登录成功' })
      // 登录成功后加载数据
      this.loadBabyConfig()
      this.loadMyRecords()
    } catch (err) {
      wx.hideLoading()
      console.error('登录失败', err)
      wx.showModal({
        title: '登录失败',
        content: err.message || '请检查网络连接',
        showCancel: false
      })
    }
  },

  // ================= 宝宝配置 =================
  async loadBabyConfig() {
    try {
      const config = await api.getBabyConfig()
      this.setData({ babyConfig: config })
    } catch (err) {
      console.error('加载宝宝配置失败', err)
    }
  },

  // 打开编辑宝宝信息弹窗（复用 addBaby 弹窗）
  onEditBaby() {
    const { babyConfig } = this.data
    this.setData({
      showBabyModal: true,
      babyName: babyConfig.baby_name || '',
      babyGender: babyConfig.gender === 'male' ? '男' : (babyConfig.gender === 'female' ? '女' : '男'),
      babyBirthday: babyConfig.birth_date || '',
      babyHeight: babyConfig.birth_weight ? String(babyConfig.birth_weight) : '',
      babyWeight: ''
    })
  },

  onInputChange(e) {
    const field = e.currentTarget.dataset.field
    this.setData({ [field]: e.detail.value })
  },

  async saveBabyConfig() {
    const { babyName, babyGender, babyBirthday, babyHeight } = this.data
    if (!babyName) {
      wx.showToast({ title: '请输入宝宝姓名', icon: 'none' })
      return
    }
    try {
      wx.showLoading({ title: '保存中...' })
      await api.updateBabyConfig({
        baby_name: babyName,
        gender: babyGender === '男' ? 'male' : 'female',
        birth_date: babyBirthday || null,
        birth_weight: babyHeight ? parseFloat(babyHeight) : null
      })
      wx.hideLoading()
      wx.showToast({ title: '保存成功' })
      this.setData({ showBabyModal: false })
      this.loadBabyConfig()
    } catch (err) {
      wx.hideLoading()
      console.error('保存失败', err)
      wx.showToast({ title: err.message || '保存失败', icon: 'none' })
    }
  },

  // ================= 宝宝弹窗 =================
  openBabyModal() {
    this.setData({ showBabyModal: true })
  },
  closeBabyModal() {
    this.setData({ showBabyModal: false })
  },
  selectGender(e) {
    this.setData({ babyGender: e.currentTarget.dataset.value })
  },
  selectBirthday(e) {
    this.setData({ babyBirthday: e.detail.value })
  },

  // ================= 退出登录 =================
  handleLogout() {
    wx.showModal({
      title: '退出登录',
      content: '确认退出登录？',
      success: (res) => {
        if (!res.confirm) return
        api.logout()
        this.setData({
          userInfo: null, hasAuth: false,
          babyConfig: null, myRecords: []
        })
        wx.showToast({ title: '已退出登录' })
      }
    })
  },

  // ================= 我的记录 =================
  async loadMyRecords() {
    try {
      const list = await api.listRecords()
      const formatted = (list || []).map(item => ({
        ...item,
        displayType: item.type_name || RECORD_TYPE_NAMES[item.type] || item.type,
        displayValue: this.formatRecordDetail(item.details),
        displayTime: this.formatDisplayTime(item.timestamp || item.created_at),
        displayUserName: '我'
      }))
      this.setData({ myRecords: formatted })
    } catch (err) {
      console.error('加载记录失败', err)
    }
  },

  formatRecordDetail(details) {
    if (!details) return ''
    const parts = []
    if (details.feeding_type) parts.push(details.feeding_type === 'breast' ? '母乳' : '奶粉')
    if (details.amount_ml) parts.push(`${details.amount_ml}ml`)
    if (details.name) parts.push(details.name)
    return parts.join(' ') || JSON.stringify(details)
  },

  formatDisplayTime(timeStr) {
    if (!timeStr) return ''
    try {
      const date = new Date(timeStr)
      const now = new Date()
      const diff = now - date
      const h = this.padZero(date.getHours())
      const m = this.padZero(date.getMinutes())
      if (diff < 24 * 60 * 60 * 1000 && date.getDate() === now.getDate()) {
        return `今天 ${h}:${m}`
      }
      const yesterday = new Date(now)
      yesterday.setDate(yesterday.getDate() - 1)
      if (date.getDate() === yesterday.getDate()) {
        return `昨天 ${h}:${m}`
      }
      return `${date.getMonth() + 1}/${date.getDate()} ${h}:${m}`
    } catch {
      return timeStr
    }
  },

  padZero(num) {
    return String(num).padStart(2, '0')
  },

  async deleteRecord(e) {
    const id = e.currentTarget.dataset.id
    wx.showModal({
      title: '确认删除',
      content: '删除后不可恢复',
      success: async (res) => {
        if (!res.confirm) return
        try {
          await api.deleteRecord(id)
          wx.showToast({ title: '已删除' })
          this.loadMyRecords()
        } catch (err) {
          console.error(err)
          wx.showToast({ title: '删除失败', icon: 'none' })
        }
      }
    })
  }
})
