// pages/mine/mine.js
const { supabase } = require('../../utils/supabase')
const { formatRecordTime, formatRecordType, formatRecordValue } = require('../../utils/recordFormat')

Page({
  data: {
    // 用户
    userInfo: null,
    hasAuth: false,

    // 家庭
    familyId: '',
    familyName: '',
    inputFamilyId: '',
    familyNameInput: '',

    // 宝宝
    babyList: [],
    selectedBabyId: '',
    showBabyModal: false,
    babyName: '',
    babyGender: '男',
    babyBirthday: '',
    babyHeight: '',
    babyWeight: '',

    // 我的记录
    myRecords: []
  },

  onLoad() {
    const user = wx.getStorageSync('userInfo')
    const familyId = wx.getStorageSync('familyId')
    const familyName = wx.getStorageSync('familyName')
    const selectedBabyId = wx.getStorageSync('selectedBabyId')
    
    if (user) this.setData({ userInfo: user, hasAuth: true })
    if (familyId) {
      this.setData({ familyId, familyName, selectedBabyId })
      this.loadBabies()
      this.loadMyRecords()
    }
  },

  onShow() {
    this.loadBabies()
    this.loadMyRecords()
  },

  // ================= 登录 =================
  getUserProfile() {
    wx.getUserProfile({
      desc: '用于记录宝宝数据',
      success: (res) => {
        // 生成唯一用户 ID（使用微信 openId 或设备信息）
        const systemInfo = wx.getSystemInfoSync()
        const userId = 'user_' + systemInfo.brand + '_' + systemInfo.model.replace(/\s/g, '') + '_' + Date.now()
        
        const userInfo = {
          ...res.userInfo,
          userId: userId
        }
        
        this.setData({
          userInfo: userInfo,
          hasAuth: true
        })
        wx.setStorageSync('userInfo', userInfo)
        wx.setStorageSync('userId', userId)
        wx.showToast({ title: '登录成功' })
      }
    })
  },

  // ================= 家庭 =================
  onInputChange(e) {
    const field = e.currentTarget.dataset.field
    this.setData({ [field]: e.detail.value })
  },

  async createFamily() {
    const { familyNameInput, userInfo } = this.data
    if (!familyNameInput) {
      wx.showToast({ title: '请输入家庭名称', icon: 'none' })
      return
    }
    try {
      wx.showLoading({ title: '创建中...' })
      const res = await supabase.insert('family', {
        name: familyNameInput,
        creator_id: userInfo?.nickName || '匿名'
      })
      const familyId = res[0].id
      wx.setStorageSync('familyId', familyId)
      wx.setStorageSync('familyName', familyNameInput)
      this.setData({ familyId, familyName: familyNameInput })
      wx.hideLoading()
      wx.showToast({ title: '创建成功' })
      this.loadBabies()
    } catch (err) {
      wx.hideLoading()
      console.error(err)
      wx.showToast({ title: '创建失败', icon: 'none' })
    }
  },

  onFamilyInput(e) {
    this.setData({ inputFamilyId: e.detail.value })
  },

  async joinFamily() {
    const { inputFamilyId } = this.data
    if (!inputFamilyId) {
      wx.showToast({ title: '请输入家庭ID', icon: 'none' })
      return
    }
    try {
      wx.showLoading({ title: '加入中...' })
      const result = await supabase.select('family', '*', `id=eq.${inputFamilyId}`)
      if (!result.length) {
        wx.hideLoading()
        wx.showToast({ title: '家庭不存在', icon: 'none' })
        return
      }
      const family = result[0]
      wx.setStorageSync('familyId', family.id)
      wx.setStorageSync('familyName', family.name)
      this.setData({ familyId: family.id, familyName: family.name })
      wx.hideLoading()
      wx.showToast({ title: '加入成功' })
      this.loadBabies()
      this.loadMyRecords()
    } catch (err) {
      wx.hideLoading()
      console.error(err)
      wx.showToast({ title: '加入失败', icon: 'none' })
    }
  },

  // ================= 宝宝 =================
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
  async addBaby() {
    const { babyName, babyGender, babyBirthday, babyHeight, babyWeight, familyId } = this.data
    if (!babyName || !familyId) {
      wx.showToast({ title: '请完善信息', icon: 'none' })
      return
    }
    try {
      wx.showLoading({ title: '添加中...' })
      await supabase.insert('baby', {
        family_id: familyId,
        name: babyName,
        gender: babyGender,
        birthday: babyBirthday || null,
        birth_height: babyHeight ? parseFloat(babyHeight) : null,
        birth_weight: babyWeight ? parseFloat(babyWeight) : null
      })
      wx.hideLoading()
      wx.showToast({ title: '添加成功' })
      this.setData({
        babyName: '',
        babyGender: '男',
        babyBirthday: '',
        babyHeight: '',
        babyWeight: ''
      })
      this.closeBabyModal()
      this.loadBabies()
    } catch (err) {
      wx.hideLoading()
      console.error(err)
      wx.showToast({ title: '添加失败', icon: 'none' })
    }
  },
  async deleteBaby(e) {
    const id = e.currentTarget.dataset.id
    wx.showModal({
      title: '确认删除',
      content: '删除后不可恢复',
      success: async (res) => {
        if (!res.confirm) return
        try {
          await supabase.delete('baby', `id=eq.${id}`)
          wx.showToast({ title: '已删除' })
          this.loadBabies()
        } catch (err) {
          console.error(err)
          wx.showToast({ title: '删除失败', icon: 'none' })
        }
      }
    })
  },
  async loadBabies() {
    const { familyId, selectedBabyId } = this.data
    if (!familyId) return
    try {
      const list = await supabase.select('baby', '*', `family_id=eq.${familyId}`)
      this.setData({ babyList: list || [] })

      if (!list || list.length === 0) {
        this.clearSelectedBaby()
        return
      }

      const babyExists = list.some(b => b.id === selectedBabyId)
      if (!selectedBabyId || !babyExists) {
        const firstBabyId = list[0].id
        this.setData({ selectedBabyId: firstBabyId })
        wx.setStorageSync('selectedBabyId', firstBabyId)
      }
    } catch (err) {
      console.error('加载宝宝失败', err)
    }
  },

  // 切换宝宝
  selectBaby(e) {
    const babyId = e.currentTarget.dataset.id
    this.setData({ selectedBabyId: babyId })
    wx.setStorageSync('selectedBabyId', babyId)
    wx.showToast({
      title: '已切换到' + (e.currentTarget.dataset.name || '该宝宝'),
      icon: 'success'
    })
  },

  clearSelectedBaby() {
    this.setData({ selectedBabyId: '' })
    wx.removeStorageSync('selectedBabyId')
  },

  exitFamily() {
    wx.showModal({
      title: '退出家庭',
      content: '确认退出后会清除家庭信息和当前宝宝选择',
      success: (res) => {
        if (!res.confirm) return
        this.clearFamily()
      }
    })
  },

  clearFamily() {
    wx.removeStorageSync('familyId')
    wx.removeStorageSync('familyName')
    this.clearSelectedBaby()
    this.setData({
      familyId: '',
      familyName: '',
      babyList: [],
      myRecords: []
    })
  },

 
// ================= 我的记录 =================
async loadMyRecords() {
  const { userInfo } = this.data
  
  // 优先使用存储的 userId，兼容旧数据
  let userId = wx.getStorageSync('userId')
  if (!userId && userInfo) {
    // 兼容旧版本：使用设备信息生成 userId
    const systemInfo = wx.getSystemInfoSync()
    userId = 'anon_' + systemInfo.brand + '_' + systemInfo.model.replace(/\s/g, '')
  }
  
  if (!userId) return

  try {
    const list = await supabase.select(
      'records',
      '*',
      `user_id=eq.'${userId}'&order=created_at.desc`
    )
    const formatted = (list || []).map(item => ({
      ...item,
      displayType: formatRecordType(item.type),
      displayValue: formatRecordValue(item),
      displayTime: formatRecordTime(item.created_at || item.create_at),
      displayUserName: item.user_name || '匿名'
    }))
    this.setData({ myRecords: formatted })
  } catch (err) {
    console.error('加载记录失败', err)
  }
},

async deleteRecord(e) {
  const id = e.currentTarget.dataset.id
  wx.showModal({
    title: '确认删除',
    content: '删除后不可恢复',
    success: async (res) => {
      if (!res.confirm) return
      try {
        await supabase.delete('records', `id=eq.${id}`)
        wx.showToast({ title: '已删除' })
        this.loadMyRecords()
      } catch (err) {
        console.error(err)
        wx.showToast({ title: '删除失败', icon: 'none' })
      }
    }
  })
},

// 移除 addOrEditRecord 和 openRecordModal 等新增/编辑相关方法
});
