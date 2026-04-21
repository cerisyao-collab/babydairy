const api = require('../../utils/api')

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
    if (!api.getToken()) {
      this.setData({ allRecords: [], records: [] })
      return
    }
    try {
      const records = await api.listRecords()
      // 时间倒序
      records.sort((a, b) => new Date(b.timestamp || b.created_at || 0) - new Date(a.timestamp || a.created_at || 0))
      this.setData({ allRecords: records }, () => {
        this.applyFilter()
      })
    } catch (err) {
      console.error('[records] 加载失败', err)
      wx.showToast({ title: '加载失败', icon: 'none' })
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
      list = list.filter(i => i.type === 'feeding')
    } else if (filter === 'diaper') {
      list = list.filter(i => i.type === 'bowel' || i.type === 'urine')
    } else if (filter === 'care') {
      list = list.filter(i => i.type === 'bathing')
    } else if (filter === 'growth') {
      list = list.filter(i => i.type === 'growth')
    } else if (filter === 'illness') {
      list = list.filter(i => i.type === 'illness')
    } else if (filter === 'medication') {
      list = list.filter(i => i.type === 'medication')
    }

    // 预处理数据，添加格式化字段
    const formattedList = list.map(item => ({
      ...item,
      displayType: item.type_name || this.formatType(item.type),
      displayValue: this.formatValue(item),
      displayTime: this.formatTime(item.timestamp || item.created_at)
    }))

    this.setData({ records: formattedList })
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
    const map = {
      feeding: '喂奶', bowel: '大便', urine: '小便',
      medication: '营养品', bathing: '洗澡', sleep: '睡眠',
      growth: '生长指标', illness: '病情'
    }
    return map[type] || type
  },

  // 内容展示
  formatValue(item) {
    const d = item.details || {}
    const parts = []
    if (d.feeding_type) parts.push(d.feeding_type === 'breast' ? '母乳' : (d.feeding_type === 'formula' ? `奶粉 ${d.amount_ml || ''}ml` : d.feeding_type))
    if (d.amount_ml && !d.feeding_type) parts.push(`${d.amount_ml}ml`)
    if (d.name) parts.push(d.name)
    if (d.temperature) parts.push(`${d.temperature}°C`)
    if (d.height_cm) parts.push(`身高 ${d.height_cm}cm`)
    if (d.weight_kg) parts.push(`体重 ${d.weight_kg}kg`)
    if (d.symptom) parts.push(d.symptom)
    if (d.notes) parts.push(d.notes)
    return parts.join(' ') || '-'
  }
})
