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
    height: '身高cm',
    weight: '体重kg',
    head: '头围cm',
    foot: '脚长cm',
    temperature: '体温°C',
    feeding_breast: '母乳',
    feeding_formula: '奶粉',
    bathing: '洗澡',
    nail_cutting: '剪指甲',
    diaper: '换尿布',
    diaper_stool: '换尿布',
    diaper_urine: '换尿布',
    diaper_both: '换尿布',
    supplement: '营养品'
  }
  if (type.startsWith('feeding_')) {
    return map[type] || '喂养'
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
