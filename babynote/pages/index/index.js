// pages/index/index.js
const { supabase } = require('../../utils/supabase')

Page({
  data: {
    loading: false,
    
    // 奶粉弹窗
    showFeedingModal: false,
    formulaAmount: 150, // 奶粉毫升数
    
    // 换尿布弹窗
    showDiaperModal: false,
    diaperUrine: false,
    diaperStool: false,
    
    // 营养品弹窗
    showSupplementModal: false,
    newSupplementName: '',
    supplements: [], // { id, name, selected }
  },

  onLoad() {
    // 不需要授权，直接使用匿名方式
  },

  // 获取记录上下文（userId, familyId, babyId）
  getRecordContext() {
    // 获取 userId
    let userId = wx.getStorageSync('userId')
    if (!userId) {
      const systemInfo = wx.getSystemInfoSync()
      userId = 'anon_' + systemInfo.brand + '_' + systemInfo.model.replace(/\s/g, '')
    }
    
    // 获取 familyId 和 babyId
    const familyId = wx.getStorageSync('familyId') || ''
    const babyId = wx.getStorageSync('selectedBabyId') || ''
    const userName = wx.getStorageSync('userInfo')?.nickName || '匿名用户'

    return { userId, familyId, babyId, userName }
  },

  // 阻止事件冒泡（用于弹窗）
  stopEvent(e) {
    // catchtap 已经阻止了冒泡，这个方法是双重保险
  },

  // 记录母乳（直接保存）
  async recordBreast() {
    wx.showLoading({ title: '记录中...' })
    
    try {
      const { userId, familyId, babyId, userName } = this.getRecordContext()

      const recordData = {
        type: 'feeding_breast',
        user_id: userId,
        user_name: userName,
        detail: '母乳',
        family_id: familyId || null,
        baby_id: babyId || null
      }

      await supabase.insert('records', recordData)
      
      wx.hideLoading()
      wx.showToast({
        title: '母乳喂养记录成功',
        icon: 'success'
      })
    } catch (err) {
      wx.hideLoading()
      console.error('记录失败', err)
      wx.showToast({
        title: err.message || '记录失败',
        icon: 'none',
        duration: 3000
      })
    }
  },

  // 打开奶粉弹窗
  openFormulaModal() {
    this.setData({
      formulaAmount: 150,
      showFeedingModal: true
    })
  },

  // 关闭弹窗（按钮调用）
  closeFeedingModal() {
    this.setData({ showFeedingModal: false })
  },

  // 滑动选择奶量
  onFormulaAmountChange(e) {
    const amount = parseInt(e.detail.value)
    this.setData({ formulaAmount: amount })
  },

  // 确认奶粉记录
  async confirmFeeding() {
    wx.showLoading({ title: '保存中...' })
    
    try {
      const { userId, familyId, babyId, userName } = this.getRecordContext()

      const recordData = {
        type: 'feeding_formula',
        user_id: userId,
        user_name: userName,
        detail: `${this.data.formulaAmount}ml`,
        family_id: familyId || null,
        baby_id: babyId || null
      }

      await supabase.insert('records', recordData)
      
      wx.hideLoading()
      wx.showToast({
        title: `奶粉（${this.data.formulaAmount}ml）记录成功`,
        icon: 'success'
      })

      this.closeFeedingModal()
    } catch (err) {
      wx.hideLoading()
      console.error('记录失败', err)
      wx.showToast({
        title: err.message || '记录失败',
        icon: 'none',
        duration: 3000
      })
    }
  },

  // 打开换尿布弹窗
  openDiaperModal() {
    this.setData({
      diaperUrine: false,
      diaperStool: false,
      showDiaperModal: true
    })
  },

  // 关闭换尿布弹窗（按钮调用）
  closeDiaperModal() {
    this.setData({ showDiaperModal: false })
  },

  // 点击遮罩层关闭换尿布弹窗
  closeDiaperModalByMask() {
    this.setData({ showDiaperModal: false })
  },

  // 切换尿尿选项
  toggleDiaperUrine() {
    this.setData({ diaperUrine: !this.data.diaperUrine })
  },

  // 切换粑粑选项
  toggleDiaperStool() {
    this.setData({ diaperStool: !this.data.diaperStool })
  },

  // 确认换尿布记录
  async confirmDiaper() {
    // 必须至少选择一个类型
    if (!this.data.diaperUrine && !this.data.diaperStool) {
      wx.showToast({
        title: '请至少选择一个类型',
        icon: 'none'
      })
      return
    }

    wx.showLoading({ title: '保存中...' })
    
    try {
      const { userId, familyId, babyId, userName } = this.getRecordContext()

      // 根据选择确定类型
      let recordType = ''
      let detail = ''
      
      if (this.data.diaperUrine && this.data.diaperStool) {
        recordType = 'diaper_both'
        detail = '大小便'
      } else if (this.data.diaperUrine) {
        recordType = 'diaper_urine'
        detail = '小便'
      } else {
        recordType = 'diaper_stool'
        detail = '大便'
      }

      const recordData = {
        type: recordType,
        user_id: userId,
        user_name: userName,
        detail: detail,
        family_id: familyId || null,
        baby_id: babyId || null
      }

      await supabase.insert('records', recordData)
      
      wx.hideLoading()
      wx.showToast({
        title: `换尿布（${detail}）记录成功`,
        icon: 'success'
      })

      this.closeDiaperModal()
    } catch (err) {
      wx.hideLoading()
      console.error('记录失败', err)
      wx.showToast({
        title: err.message || '记录失败',
        icon: 'none',
        duration: 3000
      })
    }
  },

  // 打开营养品弹窗
  openSupplementModal() {
    // 保留之前添加的营养品，清空输入框
    this.setData({
      newSupplementName: '',
      showSupplementModal: true,
      supplements: this.data.supplements // 保持之前列表
    })
  },

  // 关闭营养品弹窗（按钮调用）
  closeSupplementModal() {
    this.setData({ showSupplementModal: false })
  },

  // 点击遮罩层关闭营养品弹窗
  closeSupplementModalByMask() {
    this.setData({ showSupplementModal: false })
  },

  // 输入营养品名称
  onSupplementInput(e) {
    this.setData({ newSupplementName: e.detail.value })
  },

  // 添加营养品到列表
  addSupplement() {
    const name = this.data.newSupplementName.trim()
    if (!name) {
      wx.showToast({
        title: '请输入营养品名称',
        icon: 'none'
      })
      return
    }

    // 检查是否已存在
    const exists = this.data.supplements.some(item => item.name === name)
    if (exists) {
      wx.showToast({
        title: '该营养品已添加',
        icon: 'none'
      })
      return
    }

    // 添加到列表，默认选中
    const newSupplement = {
      id: Date.now(),
      name: name,
      selected: true
    }

    this.setData({
      supplements: [...this.data.supplements, newSupplement],
      newSupplementName: '' // 清空输入框
    })
  },

  // 切换营养品选中状态
  toggleSupplement(e) {
    const index = e.currentTarget.dataset.index
    const supplements = [...this.data.supplements]
    supplements[index].selected = !supplements[index].selected
    this.setData({ supplements })
  },

  // 确认营养品记录
  async confirmSupplement() {
    // 必须至少选择一个营养品
    const selectedSupplements = this.data.supplements.filter(item => item.selected)
    if (selectedSupplements.length === 0) {
      wx.showToast({
        title: '请至少选择一个营养品',
        icon: 'none'
      })
      return
    }

    wx.showLoading({ title: '保存中...' })
    
    try {
      const { userId, familyId, babyId, userName } = this.getRecordContext()

      // 将所有选中的营养品名称拼接
      const supplementNames = selectedSupplements.map(item => item.name).join(', ')

      const recordData = {
        type: 'supplement',
        user_id: userId,
        user_name: userName,
        detail: supplementNames,
        family_id: familyId || null,
        baby_id: babyId || null
      }

      await supabase.insert('records', recordData)
      
      wx.hideLoading()
      wx.showToast({
        title: `营养品（${supplementNames}）记录成功`,
        icon: 'success',
        duration: 2000
      })

      this.closeSupplementModal()
    } catch (err) {
      wx.hideLoading()
      console.error('记录失败', err)
      wx.showToast({
        title: err.message || '记录失败',
        icon: 'none',
        duration: 3000
      })
    }
  },

  // 格式化时间
  formatTime(dateStr) {
    if (!dateStr) return ''
    
    const date = new Date(dateStr)
    const now = new Date()
    const diff = now - date
    
    // 今天
    if (diff < 24 * 60 * 60 * 1000 && date.getDate() === now.getDate()) {
      return `今天 ${this.padZero(date.getHours())}:${this.padZero(date.getMinutes())}`
    }
    
    // 昨天
    const yesterday = new Date(now)
    yesterday.setDate(yesterday.getDate() - 1)
    if (date.getDate() === yesterday.getDate()) {
      return `昨天 ${this.padZero(date.getHours())}:${this.padZero(date.getMinutes())}`
    }
    
    // 其他日期
    return `${date.getMonth() + 1}/${date.getDate()} ${this.padZero(date.getHours())}:${this.padZero(date.getMinutes())}`
  },

  padZero(num) {
    return num.toString().padStart(2, '0')
  },

  // 获取类型名称
  getTypeName(type) {
    const typeNames = {
      'feeding': '喂奶',
      'feeding_breast': '喂奶（母乳）',
      'feeding_formula': '喂奶（奶粉）',
      'diaper': '排便',
      'diaper_urine': '换尿布（小便）',
      'diaper_stool': '换尿布（大便）',
      'diaper_both': '换尿布（大小便）',
      'bathing': '洗澡',
      'changing': '换衣',
      'nail_cutting': '剪指甲'
    }
    return typeNames[type] || type
  },

  // 获取类型图标
  getTypeIcon(type) {
    const icons = {
      'feeding': '🍼',
      'feeding_breast': '🤱',
      'feeding_formula': '🥛',
      'diaper': '💩',
      'diaper_urine': '💧',
      'diaper_stool': '💩',
      'diaper_both': '🔄',
      'bathing': '🚿',
      'changing': '👕',
      'nail_cutting': '✂️'
    }
    return icons[type] || '📝'
  }
})
