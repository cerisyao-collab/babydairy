const { supabase } = require('../../utils/supabase')

Page({
  data: {
    records: [],
    allRecords: [],
    filter: 'all'
  },

  onLoad() {
    this.loadRecords()
  },

  onShow() {
    this.loadRecords()
  },

  async loadRecords() {
    try {
      const res = await supabase.getRecentRecords(100)

      let records = Array.isArray(res) ? res : []

      // 时间倒序
      records.sort((a, b) => {
        return new Date(b.created_at || b.create_at || 0) - new Date(a.created_at || a.create_at || 0)
      })

      this.setData({
        allRecords: records
      }, () => {
        this.applyFilter()
      })
    } catch (err) {
      console.error('[records] 加载失败', err)
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      })
    }
  },

  // 切换分类
  onFilterChange(e) {
    const type = e.currentTarget.dataset.type
    this.setData({ filter: type }, () => {
      this.applyFilter()
    })
  },

  // 应用筛选
  applyFilter() {
    const { allRecords, filter } = this.data

    let list = [...allRecords]

    if (filter === 'feeding') {
      list = list.filter(i => i.type && ['feeding_breast','feeding_formula','diaper_both','diaper_stool','diaper_urine','supplement'].includes(i.type))
    } else if (filter === 'care') {
      list = list.filter(i => i.type && ['bathing','nail_cutting'].includes(i.type))
    } else if (filter === 'growth') {
      list = list.filter(i => i.type && ['height','weight','head','foot'].includes(i.type))
    } else if (filter === 'temp') {
      list = list.filter(i => i.type === 'temperature')
    }

    // 预处理数据，添加格式化字段
    const formattedList = list.map(item => {
      return {
        ...item,
        displayType: this.formatType(item.type),
        displayValue: this.formatValue(item),
        displayTime: this.formatTime(item.created_at || item.create_at),
        displayUser_name: item.user_name
      }
    })

    this.setData({
      records: formattedList
    })
  },

  // 时间格式
  formatTime(dateStr) {
    if (!dateStr) return ''

    const d = new Date(dateStr)
    const now = new Date()

    if (d.toDateString() === now.toDateString()) {
      return `今天 ${this.pad(d.getHours())}:${this.pad(d.getMinutes())}`
    }

    return `${d.getMonth()+1}/${d.getDate()} ${this.pad(d.getHours())}:${this.pad(d.getMinutes())}`
  },

  pad(n) {
    return n.toString().padStart(2, '0')
  },

  // 类型展示
  formatType(type) {
    if (!type) return '未知'
    const map = {
      height: '身高cm',
      weight: '体重kg',
      head: '头围cm',
      foot: '脚长cm',
      temperature: '体温°C',
      feeding_breast: '母乳',
      feeding_formula: '奶粉',
      feeding: '喂养',
      bathing: '洗澡',
      nail_cutting: '剪指甲',
      diaper: '换尿布',
      diaper_stool: '换尿布',
      diaper_urine: '换尿布',
      diaper_both: '换尿布',
      supplement: '营养品'
    }
    // 处理前缀
    if (type.startsWith('feeding_')) {
      return map[type] || '喂养'
    }
    return map[type] || type
  },

  // 内容展示
  formatValue(item) {
    // 优先使用 value
    if (item.value !== null && item.value !== undefined && item.value !== '') {
      return item.value
    }
    // 其次使用 detail
    if (item.detail !== null && item.detail !== undefined && item.detail !== '') {
      return item.detail
    }
    // 没有数值时显示 -
    return '-'
  }
  
})
