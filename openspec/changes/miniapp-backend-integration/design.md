## Context

babynote 微信小程序当前架构：
- 前端：微信小程序（pages/index, pages/records, pages/care, pages/mine）
- 后端：Supabase（PostgreSQL + REST API）
- 认证：匿名用户（使用设备信息生成 userId）

babyjour 后端已构建：
- FastAPI 服务（部署在阿里云 FC）
- PostgreSQL（RDS Serverless）
- 微信认证（openid → JWT token）
- AI 喂养分析（通义千问集成）
- 完整的记录和配置 API

迁移目标：让小程序使用 babyjour 后端，保留现有 UI 交互。

## Goals / Non-Goals

**Goals:**
- 实现微信小程序标准认证流程（wx.login → JWT）
- 创建统一 API 客户端封装请求和 token 管理
- 迁移所有记录类型到新后端 API
- 在首页集成 AI 分析状态展示
- 支持宝宝配置用于 AI 分析计算
- 实现每日报告页面/组件

**Non-Goals:**
- 不修改现有 UI 布局和交互逻辑
- 不实现家庭/多宝宝功能（后端暂不支持）
- 不实现数据迁移脚本（用户手动重新录入）
- 不实现订阅消息推送（暂不申请模板）

## Decisions

### 1. API 客户端设计

**决策：创建 utils/api.js 封装所有请求**

理由：
- 统一处理 JWT token 存储和请求头注入
- 统一错误处理（401 自动跳转登录、网络错误提示）
- 方便切换 API 基础地址（开发/生产环境）
- 保持与现有 Supabase 客户端类似的调用方式，减少页面代码改动

替代方案：
- 每个页面直接调用 wx.request → 拒绝：代码重复，token 管理分散
- 使用第三方请求库 → 拒绝：微信小程序限制，原生 wx.request 更稳定

### 2. 认证流程

**决策：使用 wx.login + 后端认证 + JWT token**

流程：
```
1. 小程序调用 wx.login() 获取 code
2. 小程序调用 POST /api/auth/login { code }
3. 后端调用微信 API 获取 openid
4. 后端生成 JWT token 返回
5. 小程序存储 token 到 storage
6. 后续请求携带 Authorization: Bearer <token>
```

理由：
- 微信小程序标准认证方式
- JWT token 无需服务端 session，适合 FC 无状态部署
- openid 与用户绑定，数据持久化

替代方案：
- 继续匿名认证 → 拒绝：无法跨设备同步数据
- 使用 wx.getUserProfile → 拒绝：微信已废弃该接口

### 3. Token 存储策略

**决策：使用 wx.setStorageSync 存储 token**

理由：
- 同步存储，登录后立即可用
- 微信小程序 storage 持久化，用户关闭后仍保留
- 每次请求从 storage 读取 token，无需全局状态管理

Token 过期处理：
- 后端 JWT_EXPIRE_MINUTES = 10080（7天）
- token 过期后请求返回 401
- 前端捕获 401 自动跳转登录页重新登录

### 4. API 基础地址配置

**决策：使用 project.config.js 配置环境变量**

```javascript
// utils/config.js
const ENV = {
  dev: 'http://localhost:9000/api',
  prod: 'https://babyjour.fc.aliyuncs.com/api'
}

const API_BASE = ENV.prod // 根据环境切换
```

理由：
- 简单配置，方便切换
- 微信小程序限制动态配置，编译时确定更稳定

### 5. 记录类型映射

**决策：保持现有记录类型命名**

小程序类型 → 后端类型：
- feeding_breast → feeding (feeding_type: breast)
- feeding_formula → feeding (feeding_type: formula)
- diaper_urine → urine
- diaper_stool → bowel
- diaper_both → urine + bowel（两条记录）
- supplement → medication
- bathing → bathing
- nail_cutting → bathing（details.note: 剪指甲）

理由：
- 后端已有固定类型定义
- 前端映射层处理转换
- 用户无需感知类型变化

## Risks / Trade-offs

### Risk: Token 过期导致用户数据丢失
→ **Mitigation**: Token 7天有效期，足够长；401 自动重新登录；登录后数据自动关联 openid

### Risk: 网络请求失败影响用户体验
→ **Mitigation**: 统一错误提示；关键操作（记录）显示 loading；失败后允许重试

### Risk: API 基础地址变更需要重新发布
→ **Mitigation**: 使用小程序版本管理；dev/prod 环境隔离

### Risk: Supabase 用户数据无法迁移
→ **Mitigation**: 提示用户重新录入；考虑后续提供数据导出/导入功能

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    微信小程序 (babynote)                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  pages/index        pages/records       pages/mine          │
│  (喂养记录+AI)      (记录列表)          (登录+配置)           │
│       │                  │                  │               │
│       └──────────────────┼──────────────────┘               │
│                          │                                  │
│                    utils/api.js                              │
│  (统一请求封装、token管理、错误处理)                          │
│                          │                                  │
└──────────────────────────┼──────────────────────────────────┘
                           │ wx.request
                           │ Authorization: Bearer <jwt>
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                FastAPI Backend (babyjour)                    │
│                      阿里云 FC                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  /api/auth/login    /api/records/     /api/config/baby      │
│  /api/ai/analyze    /api/summary/     /api/records/daily    │
│                                                             │
│                    PostgreSQL                                │
│                  (RDS Serverless)                            │
│                                                             │
│                    通义千问 LLM                               │
│                  (喂养分析服务)                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```