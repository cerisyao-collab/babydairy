# 首页新增换尿布和营养品记录功能 🎯

## 功能概述

在首页原有的母乳、奶粉按钮基础上，新增两个实用功能：
- 💩 **换尿布**：可多选（尿尿/粑粑）
- 💊 **营养品**：自定义添加并选择记录

## 界面布局

### 完整的首页按钮
```
┌─────────────────────────────┐
│  🤱 母乳   🥛 奶粉         │
│  💩 换尿布  💊 营养品       │
└─────────────────────────────┘

2x2 网格布局，美观整齐
```

## 功能详情

### 1. 换尿布功能 💩

#### 操作流程
```
点击 "💩 换尿布"
  ↓
弹出换尿布窗口
  ↓
选择类型（可多选）：
  - 💧 尿尿
  - 💩 粑粑
  ↓
点击 "确认"
  ↓
保存并关闭弹窗
```

#### 交互特点
- ✅ **支持多选**：可同时选择尿尿和粑粑
- ✅ **视觉反馈**：选中的按钮高亮显示
- ✅ **智能判断**：根据选择自动确定记录类型
- ✅ **强制验证**：至少选择一个类型才能提交

#### 数据类型映射
| 用户选择 | 数据库类型 | 详情字段 |
|---------|-----------|---------|
| 只选尿尿 | `diaper_urine` | "小便" |
| 只选粑粑 | `diaper_stool` | "大便" |
| 都选 | `diaper_both` | "大小便" |

#### 代码实现

**WXML**:
```xml
<!-- 换尿布弹窗 -->
<view class="modal-mask" wx:if="{{showDiaperModal}}" bindtap="closeDiaperModal">
  <view class="modal-content" catchtap="">
    <view class="modal-header">
      <text class="modal-title">💩 记录换尿布</text>
    </view>
    
    <view class="modal-body">
      <!-- 尿布类型选择 - 可多选 -->
      <view class="option-group">
        <view class="option-label">类型（可多选）</view>
        <view class="option-buttons-multi">
          <view class="option-btn-multi {{diaperUrine ? 'active' : ''}}" 
                bindtap="toggleDiaperUrine">
            💧 尿尿
          </view>
          <view class="option-btn-multi {{diaperStool ? 'active' : ''}}" 
                bindtap="toggleDiaperStool">
            💩 粑粑
          </view>
        </view>
      </view>
    </view>
    
    <view class="modal-footer">
      <button class="modal-btn cancel" bindtap="closeDiaperModal">取消</button>
      <button class="modal-btn confirm" bindtap="confirmDiaper">确认</button>
    </view>
  </view>
</view>
```

**JS Data**:
```javascript
// 换尿布弹窗
showDiaperModal: false,
diaperUrine: false,  // 是否选中尿尿
diaperStool: false,  // 是否选中粑粑
```

**JS Methods**:
```javascript
// 打开换尿布弹窗
openDiaperModal() {
  this.setData({
    diaperUrine: false,
    diaperStool: false,
    showDiaperModal: true
  })
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
    wx.showToast({ title: '请至少选择一个类型', icon: 'none' })
    return
  }

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

  // 保存到数据库
  const recordData = {
    type: recordType,
    user_id: userId,
    user_name: userName,
    detail: detail
  }
  await supabase.insert('records', recordData)
}
```

### 2. 营养品功能 💊

#### 操作流程
```
点击 "💊 营养品"
  ↓
弹出营养品窗口
  ↓
输入营养品名称 → 点击 "添加"
  ↓
显示已添加的营养品按钮
  ↓
点击按钮切换选中状态
  ↓
点击 "记录" 保存选中的营养品
```

#### 交互特点
- ✅ **自主添加**：用户可输入任意营养品名称
- ✅ **批量管理**：一次可添加多个营养品
- ✅ **灵活选择**：每次记录可选择不同的组合
- ✅ **即时反馈**：添加后自动清空输入框
- ✅ **防重复**：同名营养品会提示已存在

#### 数据结构
```javascript
supplements: [
  { id: 1, name: '维生素 D', selected: true },
  { id: 2, name: 'DHA', selected: false },
  { id: 3, name: '益生菌', selected: true }
]
```

#### 代码实现

**WXML**:
```xml
<!-- 营养品弹窗 -->
<view class="modal-mask" wx:if="{{showSupplementModal}}" bindtap="closeSupplementModal">
  <view class="modal-content" catchtap="">
    <view class="modal-header">
      <text class="modal-title">💊 记录营养品</text>
    </view>
    
    <view class="modal-body">
      <!-- 添加营养品输入框 -->
      <view class="option-group">
        <view class="option-label">营养品名称</view>
        <view class="input-group">
          <input 
            class="supplement-input" 
            placeholder="请输入营养品名称"
            value="{{newSupplementName}}"
            bindinput="onSupplementInput" />
          <button class="add-btn" bindtap="addSupplement">添加</button>
        </view>
      </view>
      
      <!-- 已添加的营养品列表 -->
      <view class="option-group" wx:if="{{supplements.length > 0}}">
        <view class="option-label">已添加的营养品</view>
        <view class="supplement-list">
          <view 
            class="supplement-item {{item.selected ? 'selected' : ''}}" 
            wx:for="{{supplements}}" 
            wx:key="id"
            bindtap="toggleSupplement"
            data-index="{{index}}">
            {{item.name}}
            <text class="check-icon" wx:if="{{item.selected}}">✓</text>
          </view>
        </view>
      </view>
    </view>
    
    <view class="modal-footer">
      <button class="modal-btn cancel" bindtap="closeSupplementModal">取消</button>
      <button class="modal-btn confirm" bindtap="confirmSupplement">记录</button>
    </view>
  </view>
</view>
```

**JS Data**:
```javascript
// 营养品弹窗
showSupplementModal: false,
newSupplementName: '',     // 输入框内容
supplements: [],           // 已添加的营养品列表
```

**JS Methods**:
```javascript
// 打开营养品弹窗
openSupplementModal() {
  this.setData({
    newSupplementName: '',
    supplements: [],
    showSupplementModal: true
  })
},

// 输入营养品名称
onSupplementInput(e) {
  this.setData({ newSupplementName: e.detail.value })
},

// 添加营养品到列表
addSupplement() {
  const name = this.data.newSupplementName.trim()
  if (!name) {
    wx.showToast({ title: '请输入营养品名称', icon: 'none' })
    return
  }

  // 检查是否已存在
  const exists = this.data.supplements.some(item => item.name === name)
  if (exists) {
    wx.showToast({ title: '该营养品已添加', icon: 'none' })
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
    wx.showToast({ title: '请至少选择一个营养品', icon: 'none' })
    return
  }

  // 将所有选中的营养品名称拼接
  const supplementNames = selectedSupplements.map(item => item.name).join(', ')

  const recordData = {
    type: 'supplement',
    user_id: userId,
    user_name: userName,
    detail: supplementNames
  }
  await supabase.insert('records', recordData)
}
```

## 样式设计

### 按钮配色方案

```css
/* 母乳 - 紫色渐变 */
.action-btn.feeding {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* 奶粉 - 粉红渐变 */
.action-btn.formula {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

/* 换尿布 - 橙色渐变 */
.action-btn.diaper {
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
}

/* 营养品 - 青粉渐变 */
.action-btn.supplement {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
}
```

### 多选按钮样式

```css
.option-btn-multi {
  flex: 1;
  padding: 24rpx 20rpx;
  background: #f8f9fa;  /* 未选中：浅灰 */
  border-radius: 16rpx;
  transition: all 0.3s;
}

.option-btn-multi.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);  /* 选中：紫色渐变 */
  color: #fff;
  box-shadow: 0 4rpx 12rpx rgba(102, 126, 234, 0.3);
}
```

### 营养品标签样式

```css
.supplement-item {
  display: inline-flex;
  align-items: center;
  padding: 16rpx 24rpx;
  background: #f8f9fa;  /* 未选中：浅灰 */
  border-radius: 24rpx;
  border: 2rpx solid #e0e0e0;
}

.supplement-item.selected {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);  /* 选中：紫色渐变 */
  color: #fff;
  border-color: #667eea;
  box-shadow: 0 4rpx 12rpx rgba(102, 126, 234, 0.3);
}

.check-icon {
  margin-left: 8rpx;
  font-size: 24rpx;
  font-weight: bold;
}
```

## 用户场景

### 场景 A：换尿布（只尿尿）
1. 宝宝尿了
2. 点击 "💩 换尿布"
3. 点击 "💧 尿尿"（按钮高亮）
4. 点击 "确认"
5. 记录成功："换尿布（小便）记录成功"

### 场景 B：换尿布（又尿又拉）
1. 发现宝宝又尿又拉
2. 点击 "💩 换尿布"
3. 依次点击 "💧 尿尿" 和 "💩 粑粑"（都高亮）
4. 点击 "确认"
5. 记录成功："换尿布（大小便）记录成功"

### 场景 C：补充营养品
1. 早上给宝宝喂了维生素 D 和 DHA
2. 点击 "💊 营养品"
3. 输入 "维生素 D" → 点击 "添加"
4. 输入 "DHA" → 点击 "添加"
5. 两个按钮都已显示（默认都选中，有 ✓ 标记）
6. 点击 "记录"
7. 记录成功："营养品（维生素 D, DHA）记录成功"

### 场景 D：选择性记录营养品
1. 中午只喂了益生菌
2. 点击 "💊 营养品"
3. 添加 "维生素 D"、"DHA"、"益生菌"
4. 点击 "维生素 D" 取消选中（去掉 ✓）
5. 点击 "DHA" 取消选中
6. 保持 "益生菌" 选中状态
7. 点击 "记录"
8. 记录成功："营养品（益生菌）记录成功"

## 数据验证

### 换尿布验证
```javascript
// 必须至少选择一个类型
if (!this.data.diaperUrine && !this.data.diaperStool) {
  wx.showToast({
    title: '请至少选择一个类型',
    icon: 'none'
  })
  return
}
```

### 营养品验证
```javascript
// 必须至少选择一个营养品
const selectedSupplements = this.data.supplements.filter(item => item.selected)
if (selectedSupplements.length === 0) {
  wx.showToast({
    title: '请至少选择一个营养品',
    icon: 'none'
  })
  return
}
```

## 文件变更清单

### pages/index/index.wxml
**新增内容**:
- ✅ 换尿布按钮（第 34-38 行）
- ✅ 营养品按钮（第 40-44 行）
- ✅ 换尿布弹窗（第 92-118 行）
- ✅ 营养品弹窗（第 120-165 行）

**修改内容**:
- ✅ 修复所有 `<View>` 为 `<view>`（规范治理）

### pages/index/index.js
**新增 Data**:
```javascript
// 换尿布弹窗
showDiaperModal: false,
diaperUrine: false,
diaperStool: false,

// 营养品弹窗
showSupplementModal: false,
newSupplementName: '',
supplements: [],
```

**新增 Methods**:
- ✅ `openDiaperModal()` - 打开换尿布弹窗
- ✅ `closeDiaperModal()` - 关闭换尿布弹窗
- ✅ `toggleDiaperUrine()` - 切换尿尿选项
- ✅ `toggleDiaperStool()` - 切换粑粑选项
- ✅ `confirmDiaper()` - 确认换尿布记录
- ✅ `openSupplementModal()` - 打开营养品弹窗
- ✅ `closeSupplementModal()` - 关闭营养品弹窗
- ✅ `onSupplementInput()` - 输入营养品名称
- ✅ `addSupplement()` - 添加营养品到列表
- ✅ `toggleSupplement()` - 切换营养品选中状态
- ✅ `confirmSupplement()` - 确认营养品记录

### pages/index/index.wxss
**新增样式类**:
- ✅ `.action-btn.diaper` - 换尿布按钮样式
- ✅ `.action-btn.supplement` - 营养品按钮样式
- ✅ `.option-buttons-multi` - 多选按钮容器
- ✅ `.option-btn-multi` - 多选按钮
- ✅ `.option-btn-multi.active` - 多选按钮选中状态
- ✅ `.input-group` - 输入框组合
- ✅ `.supplement-input` - 营养品输入框
- ✅ `.add-btn` - 添加按钮
- ✅ `.supplement-list` - 营养品列表
- ✅ `.supplement-item` - 营养品项
- ✅ `.supplement-item.selected` - 营养品选中状态
- ✅ `.check-icon` - 对勾图标

## 测试检查清单

### 换尿布功能测试
- [ ] 点击 "💩 换尿布" 能打开弹窗
- [ ] 只选 "💧 尿尿" 能正常记录
- [ ] 只选 "💩 粑粑" 能正常记录
- [ ] 同时选两个能正常记录
- [ ] 不选择时点击 "确认" 会提示
- [ ] 选中的按钮有高亮效果
- [ ] 记录成功后显示正确提示

### 营养品功能测试
- [ ] 点击 "💊 营养品" 能打开弹窗
- [ ] 输入名称后点击 "添加" 能添加到列表
- [ ] 添加后输入框自动清空
- [ ] 同名营养品会提示已存在
- [ ] 点击营养品按钮能切换选中状态
- [ ] 选中的营养品有 ✓ 标记和高亮
- [ ] 不选择任何营养品时点击 "记录" 会提示
- [ ] 能正常记录选中的营养品
- [ ] 多个营养品名称用逗号分隔显示

### UI 测试
- [ ] 四个按钮布局整齐（2x2 网格）
- [ ] 每个按钮颜色不同但协调
- [ ] 弹窗动画流畅
- [ ] 按钮点击有反馈
- [ ] 文字大小适中

## 数据库记录示例

### 换尿布记录
```javascript
// 只尿尿
{
  type: 'diaper_urine',
  detail: '小便',
  user_id: '...',
  user_name: '...'
}

// 只粑粑
{
  type: 'diaper_stool',
  detail: '大便',
  user_id: '...',
  user_name: '...'
}

// 大小便
{
  type: 'diaper_both',
  detail: '大小便',
  user_id: '...',
  user_name: '...'
}
```

### 营养品记录
```javascript
{
  type: 'supplement',
  detail: '维生素 D, DHA, 益生菌',  // 逗号分隔
  user_id: '...',
  user_name: '...'
}
```

## 未来优化方向

### 换尿布功能
1. **快捷操作**：长按按钮直接记录上次类型
2. **统计展示**：显示今天换了几次尿布
3. **时间提醒**：多久没换尿布提醒

### 营养品功能
1. **常用列表**：保存常用的营养品，下次快速选择
2. **用量记录**：记录每次吃的量（如 1 粒、5ml）
3. **周期设置**：设置每天吃还是隔天吃
4. **库存管理**：快吃完时提醒购买

## 更新日志

**版本**: v3.0 - 功能增强版  
**日期**: 2026-03-18  

**新增功能**:
- ✅ 新增换尿布记录功能（支持多选）
- ✅ 新增营养品记录功能（自定义添加）
- ✅ 首页按钮变为 2x2 网格布局
- ✅ 完善的输入验证和错误提示

**改进内容**:
- ✅ 优化弹窗交互体验
- ✅ 统一按钮配色方案
- ✅ 规范 WXML 标签大小写

**影响范围**:
- 首页界面
- 记录类型增加
- 数据存储格式

**向后兼容**:
- ✅ 所有历史数据完整保留
- ✅ 原有功能正常工作
- ✅ 数据库 schema 无需变更

---

**设计理念**：实用、灵活、易用 ❤️

**BabyNote Team** 
