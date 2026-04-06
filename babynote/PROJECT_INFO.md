# BabyNote - 婴儿喂养记录小程序 🍼

## 📱 功能特性

### 四大模块

1. **🏠 首页（生理活动记录）**
   - 喂奶记录 🍼
   - 排便记录 💩
   - 显示最近 20 条记录
   - 支持下拉刷新

2. **🛁 护理（护理记录页）**
   - 洗澡记录 🚿
   - 换衣记录 👕
   - 剪指甲记录 ✂️
   - 护理记录列表

3. **📋 记录（查看所有记录）**
   - 全部记录汇总
   - 按类型筛选（全部/喂奶/排便/护理）
   - 最多显示 100 条记录

4. **👤 我的（个人记录管理）**
   - 用户授权登录
   - 查看我的记录
   - 删除我的记录（需配置后端）
   - 设置、帮助等功能菜单

## 🚀 快速开始

### 1. 配置 Supabase

#### 1.1 创建 Supabase 项目
1. 访问 https://supabase.com
2. 创建新项目
3. 等待项目初始化完成

#### 1.2 创建数据库表
在 Supabase SQL Editor 中运行以下 SQL：

```sql
-- 创建记录表
CREATE TABLE records (
  id BIGSERIAL PRIMARY KEY,
  type TEXT NOT NULL,          -- 'feeding', 'diaper', 'bathing', 'changing', 'nail_cutting'
  user_id TEXT,                -- 用户标识
  user_name TEXT,              -- 用户昵称
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 启用 Row Level Security
ALTER TABLE records ENABLE ROW LEVEL SECURITY;

-- 创建策略：允许所有人读取和插入
DROP POLICY IF EXISTS "允许所有人读取" ON records;
CREATE POLICY "允许所有人读取" ON records
  FOR SELECT USING (true);

DROP POLICY IF EXISTS "允许所有人插入" ON records;
CREATE POLICY "允许所有人插入" ON records
  FOR INSERT WITH CHECK (true);

-- 创建索引加速查询
CREATE INDEX idx_records_created_at ON records(created_at DESC);
CREATE INDEX idx_records_type ON records(type);
```

#### 1.3 获取 API 密钥
1. 进入项目设置 → API
2. 复制 `Project URL` 和 `anon public` 密钥

#### 1.4 填入配置
编辑 `utils/supabase.js`，确保配置正确：

```javascript
const SUPABASE_URL = 'https://你的项目 ID.supabase.co'
const SUPABASE_ANON_KEY = '你的 anon key'
```

### 2. 微信开发者工具

1. 打开微信开发者工具
2. 导入项目文件夹
3. 在 `project.config.json` 中确认 AppID
4. 编译运行

## 🎨 TabBar 底部导航

小程序已配置底部触摸栏，包含四个标签：
- 🏠 首页
- 🛁 护理
- 📋 记录
- 👤 我的

**注意**：当前使用 emoji 作为图标，如需使用自定义图标，请：
1. 准备 81x81 像素的 PNG 图标
2. 放置在 `images/` 文件夹
3. 更新 `app.json` 中的 tabBar 配置

## 📊 数据库架构

### records 表

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | BIGSERIAL | 主键 |
| type | TEXT | 记录类型 |
| user_id | TEXT | 用户 ID |
| user_name | TEXT | 用户昵称 |
| created_at | TIMESTAMPTZ | 创建时间 |

### 支持的记录类型

- `feeding` - 喂奶 🍼
- `diaper` - 排便 💩
- `bathing` - 洗澡 🚿
- `changing` - 换衣 👕
- `nail_cutting` - 剪指甲 ✂️

## 🔧 技术实现

### 目录结构

```
babynote/
├── pages/
│   ├── index/        # 首页
│   ├── care/         # 护理页
│   ├── records/      # 记录页
│   └── mine/         # 我的
├── utils/
│   ├── supabase.js   # Supabase 客户端
│   └── util.js       # 工具函数
├── images/           # 图标资源（可选）
├── app.js
├── app.json
└── README.md
```

### 核心功能

1. **Supabase REST API 集成**
   - 自定义微信小程序客户端
   - 支持插入和查询操作
   - 自动处理认证头

2. **用户系统**
   - 微信用户信息授权
   - 本地缓存用户信息
   - 匿名模式支持

3. **数据管理**
   - 时间格式化（今天/昨天/日期）
   - 下拉刷新
   - 数据筛选和排序

## ⚠️ 注意事项

1. **安全性**
   - 当前使用 anon public key
   - 建议在生产环境配置正确的 RLS 策略
   - 不要泄露 service_role key

2. **删除功能**
   - "我的"页面中的删除功能需要后端支持
   - 需要在 Supabase 添加删除策略：
   ```sql
   DROP POLICY IF EXISTS "允许所有人删除" ON records;
   CREATE POLICY "允许所有人删除" ON records
     FOR DELETE USING (true);
   ```

3. **图标资源**
   - 当前使用 emoji 作为 tabBar 图标
   - 建议使用专业设计的图标提升用户体验

## 🎯 后续扩展建议

- [ ] 添加宝宝信息（多宝宝支持）
- [ ] 添加喂奶时长/奶量记录
- [ ] 添加排便性状记录
- [ ] 统计图表（每日/每周汇总）
- [ ] 提醒功能（定时提醒喂奶）
- [ ] 导出功能（导出为 Excel）
- [ ] 编辑已有记录
- [ ] 图片上传（拍照记录）
- [ ] 数据备份和恢复

## 📝 更新日志

### v1.1.0 (当前版本)
- ✅ 新增底部 TabBar 导航
- ✅ 新增护理记录页面
- ✅ 新增所有记录页面
- ✅ 新增个人中心页面
- ✅ 优化页面布局和样式
- ✅ 修复 Supabase 连接问题

### v1.0.0
- ✅ 基础喂奶和排便记录
- ✅ Supabase 集成
- ✅ 用户授权登录

## 👨‍💻 开发说明

### 添加新的记录类型

1. 在对应页面添加按钮和处理函数
2. 更新 `getTypeName` 和 `getTypeIcon` 映射
3. 在数据库中创建相应策略（如需要）

### 修改 TabBar 样式

编辑 `app.json` 中的 `tabBar` 配置：
- `color`: 默认文字颜色
- `selectedColor`: 选中时文字颜色
- `backgroundColor`: 背景色

## 📞 技术支持

如有问题，请检查：
1. Supabase 配置是否正确
2. 数据库表和策略是否创建
3. 微信开发者工具控制台错误信息
4. 网络连接状态

---

**BabyNote** - 用心记录宝宝的每一个成长瞬间 ❤️
