# BabyNote - 婴儿喂养记录小程序

## 快速开始

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
  type TEXT NOT NULL,          -- 'feeding' 或 'diaper'
  user_id TEXT,                -- 用户标识
  user_name TEXT,              -- 用户昵称
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 启用 Row Level Security (可选，用于多人协作)
ALTER TABLE records ENABLE ROW LEVEL SECURITY;

-- 创建策略：允许所有人读取和插入
CREATE POLICY "允许所有人读取" ON records
  FOR SELECT USING (true);

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
编辑 `utils/supabase.js`，填入你的配置：

```javascript
const SUPABASE_URL = 'https://你的项目 ID.supabase.co'
const SUPABASE_ANON_KEY = '你的 anon key'
```

### 2. 微信开发者工具

1. 打开微信开发者工具
2. 导入项目文件夹：`/Users/hanyuxiao/WeChatProjects/babynote`
3. 在 `project.config.json` 中填入你的 AppID
4. 编译运行

### 3. 功能说明

- 🏠 **首页（生理活动记录）**
  - 🍼 **喂奶记录**：点击打开弹窗
    - 选择喂养方式：母乳 🤱 或 奶粉 🥛
    - 奶粉模式：滑动条选择奶量（50ml-300ml，每 5ml 一档）
  - 👶 **换尿布**：点击打开弹窗
    - 选择类型：小便 💧、大便 💩、大小便 🔄
  - 📋 **最近记录**：显示最近 20 条记录

- 🛁 **护理（护理记录页）**
  - 🚿 洗澡记录
  - 👕 换衣记录
  - ✂️ 剪指甲记录

- 📋 **记录（查看所有记录）**
  - 全部记录汇总
  - 按类型筛选：全部/喂奶/排便/护理

- 👤 **我的（个人记录管理）**
  - 用户信息卡片
  - 查看我的记录
  - 删除我的记录
  - 设置等功能菜单

## 后续扩展建议

- [ ] 添加宝宝信息（多宝宝支持）
- [ ] 添加喂奶时长/奶量记录
- [ ] 添加排便性状记录
- [ ] 统计图表（每日/每周汇总）
- [ ] 提醒功能（定时提醒喂奶）
- [ ] 导出功能（导出为 Excel）

## 技术栈

- 微信小程序原生开发
- Supabase 后端（PostgreSQL + REST API）
- 无服务器架构，按需扩展
