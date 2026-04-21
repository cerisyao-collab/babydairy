const pad = (n) => n.toString().padStart(2, '0')

const formatRecordTime = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const now = new Date()
  if (d.toDateString() === now.toDateString()) {
    return `今天 ${pad(d.getHours())}:${pad(d.getMinutes())}`
  }
  return `${d.getMonth() + 1}/${d.getDate()} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

const formatRecordType = (type) => {
  if (!type) return '未知'
  const map = {
    feeding: '喂奶', bowel: '大便', urine: '小便',
    medication: '营养品', bathing: '洗澡', sleep: '睡眠',
    growth: '生长指标', illness: '病情'
  }
  return map[type] || type
}

const formatRecordValue = (item) => {
  if (item.value !== null && item.value !== undefined && item.value !== '') {
    return item.value
  }
  if (item.detail !== null && item.detail !== undefined && item.detail !== '') {
    return item.detail
  }
  return '-'
}

module.exports = {
  formatRecordTime,
  formatRecordType,
  formatRecordValue
}
