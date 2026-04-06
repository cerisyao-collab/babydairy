## 1. API 客户端基础设施

- [x] 1.1 创建 utils/config.js 配置 API 基础地址
- [x] 1.2 创建 utils/api.js 统一请求封装
- [x] 1.3 实现 token 存储和读取函数
- [x] 1.4 实现请求拦截器（自动添加 Authorization header）
- [x] 1.5 实现错误处理（401 自动跳转登录、网络错误提示）
- [x] 1.6 实现 API 方法封装（login, createRecord, getDailyRecords 等）

## 2. 微信认证流程

- [x] 2.1 更新 app.js 添加全局登录状态管理
- [x] 2.2 实现登录页面或组件（wx.login 调用）
- [x] 2.3 调用 POST /api/auth/login 获取 JWT token
- [x] 2.4 实现 token 存储到 wx.storage
- [x] 2.5 实现 isLoggedIn 和 getUserInfo 辅助函数
- [x] 2.6 实现 401 响应自动重新登录逻辑

## 3. 喂养记录功能迁移

- [x] 3.1 更新 pages/index/index.js 引入 api.js
- [x] 3.2 实现 recordBreast 调用新 API（type: feeding, feeding_type: breast）
- [x] 3.3 实现奶粉弹窗确认调用新 API（type: feeding, feeding_type: formula）
- [x] 3.4 实现记录类型转换函数（frontend type → backend type）
- [x] 3.5 添加加载状态和错误处理

## 4. 排泄记录功能迁移

- [x] 4.1 更新换尿布弹窗确认逻辑
- [x] 4.2 实现小便记录调用 API（type: urine）
- [x] 4.3 实现大便记录调用 API（type: bowel）
- [x] 4.4 实现大小便同时记录（创建两条记录）
- [x] 4.5 添加表单验证和错误处理

## 5. 营养品记录功能迁移

- [x] 5.1 更新营养品弹窗确认逻辑
- [x] 5.2 实现营养品记录调用 API（type: medication）
- [x] 5.3 实现名称到 details.name 的映射
- [x] 5.4 添加输入验证和错误处理

## 6. 护理记录功能迁移

- [x] 6.1 更新 pages/care/care.js 引入 api.js
- [x] 6.2 实现洗澡记录调用 API（type: bathing）
- [x] 6.3 实现剪指甲记录调用 API（type: bathing, notes: 剪指甲）
- [x] 6.4 添加加载状态和成功反馈

## 7. 记录列表页面迁移

- [x] 7.1 更新 pages/records/records.js 引入 api.js
- [x] 7.2 实现 loadRecords 调用 GET /api/records/
- [x] 7.3 实现日期筛选调用 GET /api/records/daily
- [x] 7.4 实现类型筛选逻辑
- [x] 7.5 更新记录显示格式（后端字段映射）

## 8. 宝宝配置管理

- [x] 8.1 更新 pages/mine/mine.js 引入 api.js
- [x] 8.2 实现获取宝宝配置 GET /api/config/baby
- [x] 8.3 实现更新宝宝配置 PUT /api/config/baby
- [x] 8.4 实现出生日期选择和保存
- [x] 8.5 实现性别选择和保存
- [x] 8.6 实现喂养类型选择和保存
- [x] 8.7 实现出生体重输入和保存

## 9. AI 分析展示

- [x] 9.1 创建 components/ai-card/ai-card 组件
- [x] 9.2 实现 AI 分析 API 调用 POST /api/ai/analyze
- [x] 9.3 实现状态显示（正常/偏低/偏高）带颜色指示
- [x] 9.4 实现建议内容显示
- [x] 9.5 实现下次喂养建议时间显示
- [x] 9.6 在首页集成 AI 卡片组件
- [x] 9.7 实现无宝宝配置时的提示

## 10. 每日报告页面

- [x] 10.1 创建 pages/report/report 页面
- [x] 10.2 实现每日报告 API 调用 GET /api/summary/daily/ai
- [x] 10.3 实现日期选择器
- [x] 10.4 实现喂养数据展示（总奶量、次数、间隔）
- [x] 10.5 实现 AI 总结展示
- [x] 10.6 实现空数据状态处理
- [x] 10.7 在首页或导航添加报告入口

## 11. 登录流程优化

- [x] 11.1 实现首次打开自动登录
- [x] 11.2 实现登录 loading 状态
- [x] 11.3 实现登录失败重试机制
- [x] 11.4 移除旧的 Supabase 认证代码

## 12. 清理和测试

- [x] 12.1 移除 utils/supabase.js 文件
- [x] 12.2 更新 app.json 添加新页面路由
- [x] 12.3 测试完整登录流程
- [x] 12.4 测试所有记录类型创建
- [x] 12.5 测试 AI 分析展示
- [x] 12.6 测试宝宝配置保存和读取
- [x] 12.7 测试每日报告展示