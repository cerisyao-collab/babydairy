# 代码清理与用户 ID 统一修复

## 执行时间
2025-03-21

## 修改内容

### 1. 调试代码清理

#### 1.1 删除所有 console.log
清理了以下文件中的调试日志：
- `pages/index/index.js` - 删除 22 处 console.log（换尿布、营养品弹窗调试日志）
- `pages/records/records.js` - 删除 7 处 console.log（数据加载和筛选日志）
- `pages/care/care.js` - 删除 1 处 console.log（身高体重数据验证日志）

**保留**了 `console.error` 用于错误处理。

#### 1.2 整理调试文档
将所有调试文档移动到 `docs/debug/` 目录：
- DEBUG_MODAL_LOGS.md
- DEBUG_SLIDER.md
- FIX_*.md (12 个文件)
- FEATURE_UPDATE.md
- HOMEPAGE_*.md (3 个文件)
- TROUBLESHOOTING_MODAL_COMPLETE.md

### 2. 用户 ID 统一修复

#### 问题描述
- `pages/mine/mine.js` 中 `loadMyRecords` 使用 `userInfo.id` 查询记录
- 但微信 `getUserProfile` 返回的 userInfo 没有 `id` 字段
- 首页记录使用设备信息生成 userId（`anon_` + brand + model）
- 导致"我的记录"页面无法正确加载用户数据

#### 修复方案

**统一 userId 生成策略：**
1. 用户登录时生成唯一 userId 并存储到 `wx.setStorageSync('userId')`
2. 所有记录页面优先从 storage 获取 userId
3. 兼容旧数据：如果 storage 没有 userId，使用设备信息生成

**修改文件：**

1. **pages/mine/mine.js**
   - `getUserProfile()`: 登录后生成 userId 并存储
   - `loadMyRecords()`: 优先使用 storage 中的 userId，兼容旧版本

2. **pages/index/index.js**
   - `recordBreast()`: 使用统一 userId
   - `confirmFeeding()`: 使用统一 userId
   - `confirmDiaper()`: 使用统一 userId
   - `confirmSupplement()`: 使用统一 userId

3. **pages/care/care.js**
   - `recordHeightWeight()`: 使用统一 userId
   - `recordTemperature()`: 使用统一 userId
   - `recordBathing()`: 使用统一 userId
   - `recordNailCutting()`: 使用统一 userId

#### 代码示例

```javascript
// 统一 userId 获取逻辑
let userId = wx.getStorageSync('userId');
if (!userId) {
  const systemInfo = wx.getSystemInfoSync();
  userId = 'anon_' + systemInfo.brand + '_' + systemInfo.model.replace(/\s/g, '');
}
const userName = wx.getStorageSync('userInfo')?.nickName || '匿名用户';
```

## 影响范围

### 正面影响
- ✅ 代码更干净，无调试日志污染
- ✅ 用户 ID 统一，"我的记录"页面可以正确显示数据
- ✅ 兼容旧数据，不会导致已有记录丢失
- ✅ 登录后用户昵称会正确显示（之前显示"匿名用户"）

### 注意事项
- 已登录用户需要重新登录以生成新的 userId
- 旧数据（使用设备信息生成的 userId）仍然可以查询到
- 新记录将使用统一的 userId，确保数据一致性

## 后续建议

1. **多设备支持**：当前 userId 基于单设备，如果用户换手机会导致 userId 变化。建议：
   - 使用微信开放标签获取 openId
   - 或实现简单的账号系统（手机号/微信登录）

2. **数据迁移**：如果未来实现真正的用户系统，需要将旧数据迁移到新用户 ID

3. **安全加固**：Supabase RLS 策略应该基于 user_id 隔离数据，防止跨用户访问
