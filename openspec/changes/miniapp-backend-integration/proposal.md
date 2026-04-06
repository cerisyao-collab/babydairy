## Why

The babynote 微信小程序目前使用 Supabase 作为后端，需要迁移到我们已构建的 FastAPI 后端服务。这样可以：
1. 统一数据管理，使用阿里云 RDS PostgreSQL Serverless
2. 集成 AI 喂养分析功能（已完成的后端能力）
3. 使用微信小程序标准认证流程而非匿名用户
4. 降低多后端维护成本

## What Changes

- 创建统一的 API 客户端层（utils/api.js），替代现有 Supabase 客户端
- 实现微信小程序标准登录流程（wx.login → 后端认证 → JWT token）
- 迁移所有记录类型到后端 API（喂养、换尿布、营养品、护理等）
- 集成 AI 分析功能到首页展示
- 支持宝宝配置（出生日期、性别、喂养类型）用于 AI 分析
- 实现每日报告展示

**BREAKING**: 完全替换 Supabase 后端调用，现有 Supabase 数据需要迁移方案

## Capabilities

### New Capabilities

- `miniapp-auth`: 微信小程序认证流程（wx.login、openid 获取、JWT token 管理）
- `miniapp-api-client`: 统一的 API 客户端封装（请求拦截、错误处理、token 存储）
- `miniapp-feeding`: 喂养记录功能（母乳、奶粉记录）
- `miniapp-diaper`: 排泄记录功能（小便、大便记录）
- `miniapp-supplement`: 营养品记录功能
- `miniapp-care`: 护理记录功能（洗澡、剪指甲等）
- `miniapp-baby-config`: 宝宝配置管理（出生日期、性别、体重等）
- `miniapp-ai-display`: AI 分析结果展示（首页状态卡片、建议展示）
- `miniapp-daily-report`: 每日报告展示

### Modified Capabilities

无（这是新增功能集成）

## Impact

### 代码变更
- `utils/supabase.js` → `utils/api.js`（新建，替代 Supabase）
- `pages/index/index.js` - 调用新 API，集成 AI 分析展示
- `pages/records/records.js` - 调用新 API 获取记录列表
- `pages/mine/mine.js` - 登录流程、宝宝配置
- `pages/care/care.js` - 护理记录调用新 API
- `app.js` - 全局登录状态管理

### API 调用
- POST /api/auth/login - 微信登录
- POST /api/records/ - 创建记录
- GET /api/records/daily - 获取当日记录
- GET /api/config/baby - 获取/更新宝宝配置
- POST /api/ai/analyze - AI 分析
- GET /api/summary/daily/ai - AI 每日报告

### 数据迁移
- Supabase 现有数据需要迁移脚本或用户手动重新录入