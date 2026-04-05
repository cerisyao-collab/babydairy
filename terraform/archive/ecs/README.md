# 归档：ECS 部署方案

此目录包含原 ECS + RDS 部署方案的配置文件，用于回退。

## 文件说明

- `Dockerfile` - Docker 容器构建文件
- 原 Terraform 配置已更新为 FC 方案

## 如何回退到 ECS 方案

1. 恢复 Dockerfile 到项目根目录
2. 创建新的 ECS Terraform 配置
3. 使用 Docker 部署

```bash
# 构建 Docker 镜像
docker build -t baby-diary-api .

# 运行容器
docker run -d \
  --name baby-diary \
  -p 8000:8000 \
  -e DATABASE_URL="..." \
  -e WECHAT_APP_ID="..." \
  -e WECHAT_APP_SECRET="..." \
  -e JWT_SECRET="..." \
  baby-diary-api
```

## 成本对比

| 方案 | 月成本 |
|------|--------|
| ECS + RDS | ~90-140元 |
| FC + RDS Serverless | ~35-70元 |