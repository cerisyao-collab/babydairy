// 生成简单的 tabbar 图标
const fs = require('fs')
const path = require('path')

// 简单的 1x1 像素 PNG（实际应该用真正的图标）
// 这里创建一个占位文件，提示用户需要添加真实图标
const icons = [
  'home.png',
  'home-active.png',
  'care.png',
  'care-active.png',
  'list.png',
  'list-active.png',
  'user.png',
  'user-active.png'
]

const imagesDir = path.join(__dirname, 'images')

if (!fs.existsSync(imagesDir)) {
  fs.mkdirSync(imagesDir, { recursive: true })
}

console.log('请在 images 文件夹中添加以下 tabbar 图标文件：')
console.log('- home.png / home-active.png (首页图标)')
console.log('- care.png / care-active.png (护理图标)')
console.log('- list.png / list-active.png (记录图标)')
console.log('- user.png / user-active.png (我的图标)')
console.log('\n建议尺寸：81x81 像素')

// 创建说明文件
fs.writeFileSync(
  path.join(imagesDir, 'README.txt'),
  '请将 tabbar 图标放在此文件夹\n建议尺寸：81x81 像素\n格式：PNG\n'
)
