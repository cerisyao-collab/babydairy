# Baby Diary API

微信小程序宝宝日记后端服务，使用阿里云函数计算(FC)部署，集成 AI 喂养分析功能。

## 功能特性

### 核心功能
- 📝 **喂养记录** - 支持母乳/奶粉喂养记录
- 📊 **自动统计** - 每日奶量、喂养次数、喂养间隔统计
- 📈 **每日报告** - 自动生成每日喂养总结
- 🤖 **AI 分析** - 基于标准的喂养分析建议（新增）

### AI 喂养分析功能
- **智能判断** - 自动判断喂养状态（正常/偏低/偏高）
- **问题识别** - 识别奶量不足、间隔过长等问题
- **个性化建议** - 基于宝宝年龄提供针对性建议
- **AI 问答** - 支持喂养相关问题的智能问答
- **喂养提醒** - 计算建议下次喂养时间

## 架构

```
微信小程序 → FC (FastAPI) → RDS PostgreSQL Serverless
                    ↓
              通义千问 LLM API
```

## 快速开始

### 1. 安装 Serverless Devs

```bash
npm install -g @serverless-devs/s
```

### 2. 配置阿里云凭证

**推荐方式：使用 OIDC 无密钥部署**

```bash
# 安装 aliyun CLI
brew install aliyun-cli  # macOS
# 或参考: https://help.aliyun.com/document_detail/139508.html

# 使用浏览器登录（推荐）
aliyun configure --mode Browser
```

详细配置见: [docs/deploy-security.md](docs/deploy-security.md)

**备选方式：使用 AccessKey**

```bash
s config add
# 输入 AccessKeyID 和 AccessKeySecret
```

### 3. 创建基础设施 (RDS + VPC)

```bash
cd terraform

# 复制配置文件模板
cp terraform.tfvars.example terraform.tfvars

# 编辑 terraform.tfvars 填入实际值
# 特别注意: github_oidc_fingerprints 和 github_repository

# 创建资源
terraform init
terraform apply
```

### 4. 配置 GitHub Actions (自动化部署)

1. 在 GitHub 仓库设置 Secrets:
   - `TERRAFORM_DEPLOY_ROLE_ARN` - 从 terraform output 获取
   - `FC_DEPLOY_ROLE_ARN` - 从 terraform output 获取
   - `OIDC_PROVIDER_ARN` - 从 terraform output 获取
   - `VPC_ID`, `VSWITCH_ID`, `SECURITY_GROUP_ID`
   - `OSS_SECRETS_BUCKET`, `OSS_ENDPOINT`

2. 推送代码自动部署:
```bash
git push origin main
```

详细配置见: [docs/deploy-security.md](docs/deploy-security.md)

### 5. 本地部署 (手动)

```bash
# 设置环境变量
export VPC_ID="vpc-xxx"
export VSWITCH_ID="vsw-xxx"
export SECURITY_GROUP_ID="sg-xxx"
export DATABASE_URL="postgresql://user:pass@host:5432/baby_diary"
export WECHAT_APP_ID="wx..."
export WECHAT_APP_SECRET="..."
export JWT_SECRET="..."
export DASHSCOPE_API_KEY="sk-xxx"

# 部署
./scripts/deploy_fc.sh deploy
```

## 本地开发

### 安装依赖

```bash
pip install -r requirements.txt
```

### 本地运行

```bash
uvicorn src.api.main:app --reload
```

### 本地调试 FC

```bash
./scripts/deploy_fc.sh local
# 访问 http://localhost:9000
```

## API 文档

部署后访问：
- Swagger UI: `https://<fc-endpoint>/api/docs`
- ReDoc: `https://<fc-endpoint>/api/redoc`
- OpenAPI JSON: `https://<fc-endpoint>/api/openapi.json`

### AI 分析 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/ai/analyze` | POST | 分析当日喂养数据 |
| `/api/ai/chat` | POST | AI 喂养问答 |
| `/api/summary/daily/ai` | GET | AI 增强版每日报告 |

#### AI 分析请求示例

```json
// POST /api/ai/analyze
{
  "date": "2024-01-15"  // 可选，默认今天
}

// POST /api/ai/chat
{
  "question": "宝宝奶量够吗？",
  "context": {
    "baby_age_days": 15,
    "today_milk": 500
  }
}
```

#### AI 分析响应示例

```json
{
  "status": "normal",
  "confidence": 0.8,
  "metrics": {
    "milk_volume": {
      "value": 500,
      "min": 300,
      "max": 500,
      "status": "normal",
      "description": "奶量500ml，处于正常范围"
    }
  },
  "issues": [],
  "recommendations": ["喂养情况良好，继续保持当前节奏"],
  "ai_summary": "今日奶量500ml，喂养状态良好，继续保持。",
  "next_feeding_suggestion": "2024-01-15T19:30:00"
}
```

## 项目结构

```
src/
├── api/                  # FastAPI 端点
│   ├── main.py          # 应用入口
│   ├── index.py         # FC handler
│   ├── auth.py          # 认证端点
│   ├── records.py       # 记录端点
│   ├── summary.py       # 总结端点
│   ├── config.py        # 配置端点
│   └── ai.py            # AI 分析端点 (新增)
├── models/              # SQLAlchemy 模型
├── services/            # 业务逻辑
│   ├── ai_analyzer.py   # AI 喂养分析 (新增)
│   ├── llm_service.py   # 通义千问服务 (新增)
│   └── standards_service.py # 喂养标准服务 (新增)
├── data/                # 数据文件
│   └── feeding_standards.json # 喂养标准数据 (新增)
├── db/                  # 数据库配置
│   ├── session.py       # 标准连接池
│   └── session_fc.py    # FC 优化连接池
└── config.py            # 应用配置
terraform/               # 基础设施配置
scripts/                 # 部署脚本
tests/                   # 测试用例
```

## 成本估算

| 资源 | 规格 | 月成本 |
|------|------|--------|
| FC 函数 | 256MB, 按量 | ~5-20元 |
| RDS PostgreSQL Serverless | 1核1G, 20GB | ~30-50元 |
| **总计** | | **~35-70元/月** |

## 回滚到 ECS 方案

如需回滚到 ECS 部署：

1. 保留的 ECS Terraform 配置在 `terraform/archive/ecs/` 目录
2. 使用 Docker 部署：参考原 Dockerfile
3. 切换小程序 API 地址

## 相关文档

- [部署安全指南 (OIDC)](docs/deploy-security.md) - 无密钥部署配置
- [回滚方案](docs/rollback-plan.md) - 部署问题回滚指南
- [测试说明](README-tests.md) - 测试运行指南
- [Serverless Devs 文档](https://docs.serverless-devs.com/)
- [阿里云函数计算](https://help.aliyun.com/product/50980.html)
- [FastAPI 部署文档](https://fastapi.tiangolo.com/deployment/)
- [通义千问 API 文档](https://help.aliyun.com/document_detail/2712195.html)

## 喂养标准数据来源

AI 分析功能基于以下权威来源：

- 《中国居民膳食指南2022》
- WHO 婴幼儿喂养标准
- 各省妇幼保健院喂养建议

标准数据涵盖：
- 出生第1天至180天的喂养标准
- 喂养次数、奶量、间隔时间的建议范围
- 尿量和排便次数的参考标准

**注意：** AI 提供的分析和建议仅供参考，不能替代医生诊断。如有疑虑请咨询儿科医生。