# 部署回滚方案

本文档记录 OIDC 部署安全方案的回滚步骤。

## 回滚场景

### 场景 1: OIDC 认证失败

**症状**: GitHub Actions 无法获取临时凭证

**原因**:
- OIDC Provider 配置错误
- GitHub 仓库路径配置错误
- GitHub OIDC 公钥指纹过期/更新

**回滚步骤**:

```bash
# 1. 创建临时 AccessKey (如果还没有)
aliyun ram CreateAccessKey --UserName deploy-user

# 2. 在 GitHub Secrets 中添加临时 AK
# ALICLOUD_ACCESS_KEY=<new-key>
# ALICLOUD_SECRET_KEY=<new-secret>

# 3. 修改 GitHub Actions 工作流使用 AK
# 编辑 .github/workflows/deploy.yml:
```

```yaml
# 临时使用 AK 的配置
- name: Configure Aliyun Credentials
  run: |
    echo "ALICLOUD_ACCESS_KEY=${{ secrets.ALICLOUD_ACCESS_KEY }}" >> $GITHUB_ENV
    echo "ALICLOUD_SECRET_KEY=${{ secrets.ALICLOUD_SECRET_KEY }}" >> $GITHUB_ENV
```

```bash
# 4. 重新运行部署

# 5. 问题解决后删除临时 AK
aliyun ram DeleteAccessKey --UserAccessKeyId <key-id>
```

### 场景 2: RAM 角色权限不足

**症状**: 部署时报 "Access denied"

**原因**: 角色策略缺少必要权限

**回滚步骤**:

```bash
# 1. 临时添加管理员权限
aliyun ram AttachPolicyToRole \
  --PolicyType System \
  --PolicyName AdministratorAccess \
  --RoleName baby-diary-terraform-deploy

# 2. 完成部署

# 3. 分析缺失的权限，更新策略

# 4. 移除临时管理员权限
aliyun ram DetachPolicyFromRole \
  --PolicyType System \
  --PolicyName AdministratorAccess \
  --RoleName baby-diary-terraform-deploy
```

### 场景 3: Terraform 状态损坏

**症状**: terraform apply 失败，状态文件损坏

**回滚步骤**:

```bash
# 1. 备份当前状态
cp terraform/terraform.tfstate terraform/terraform.tfstate.backup

# 2. 从 OSS 恢复（如果配置了远程状态）
terraform state pull > terraform/terraform.tfstate

# 3. 或者重新初始化
rm terraform/terraform.tfstate
terraform init
terraform plan  # 验证状态

# 4. 如果无法恢复，手动导入资源
terraform import alicloud_vpc.main vpc-xxx
terraform import alicloud_db_instance.postgres pg-xxx
# ... 依次导入所有资源
```

### 场景 4: FC 函数部署失败

**症状**: s deploy 失败

**回滚步骤**:

```bash
# 1. 查看当前函数版本
aliyun fc GetFunction --ServiceName baby-diary-service --FunctionName api

# 2. 回滚到上一个版本
aliyun fc PublishVersion --ServiceName baby-diary-service
# 获取版本 ID

# 3. 更新别名指向旧版本
aliyun fc UpdateAlias \
  --ServiceName baby-diary-service \
  --AliasName prod \
  --VersionId <previous-version>

# 4. 或使用 Serverless Devs
s deploy --previous-version
```

### 场景 5: 数据库连接失败

**症状**: 应用无法连接 RDS

**回滚步骤**:

```bash
# 1. 检查 RDS 状态
aliyun rds DescribeDBInstances --DBInstanceStatus Running

# 2. 检查白名单
aliyun rds DescribeSecurityGroupConfiguration --DBInstanceId <instance-id>

# 3. 临时添加本机 IP 测试
aliyun rds ModifySecurityGroupConfiguration \
  --DBInstanceId <instance-id> \
  --SecurityGroupId <sg-id>

# 4. 检查 VPC 配置
aliyun vpc DescribeVpcs --VpcId <vpc-id>
aliyun vpc DescribeVSwitches --VSwitchId <vswitch-id>
```

## 完全回滚到 AK 方案

如果 OIDC 方案完全不可用，可以回滚到传统 AK 方案：

```bash
# 1. 创建专用的部署 AK
aliyun ram CreateAccessKey --UserName deploy-user --output cols=AccessKeyId,AccessKeySecret

# 2. 设置 GitHub Secrets
# ALICLOUD_ACCESS_KEY=<key>
# ALICLOUD_SECRET_KEY=<secret>

# 3. 更新 GitHub Actions 工作流
```

```yaml
# .github/workflows/deploy.yml (回滚版本)
name: Deploy (AK)

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set Aliyun Credentials
        run: |
          echo "ALICLOUD_ACCESS_KEY=${{ secrets.ALICLOUD_ACCESS_KEY }}" >> $GITHUB_ENV
          echo "ALICLOUD_SECRET_KEY=${{ secrets.ALICLOUD_SECRET_KEY }}" >> $GITHUB_ENV

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3

      - name: Terraform Apply
        run: terraform apply -auto-approve
        working-directory: terraform
```

```bash
# 4. 删除 OIDC 资源 (可选)
cd terraform
terraform destroy -target=alicloud_ram_oidc_provider.github
terraform destroy -target=alicloud_ram_role.terraform_deploy
terraform destroy -target=alicloud_ram_role.fc_deploy

# 5. 禁用 OIDC Provider
aliyun ram DeleteOIDCProvider --OIDCProviderName github-actions
```

## 预防措施

1. **测试环境验证**: 先在测试仓库验证 OIDC 配置
2. **保留备用 AK**: 禁用但不删除现有 AK，紧急时可用
3. **监控告警**: 配置 AssumeRole 失败告警
4. **文档更新**: 记录每次配置变更

## 联系支持

如果回滚无法解决问题：
- 阿里云工单: https://workorder.console.aliyun.com/
- RAM 文档: https://help.aliyun.com/product/28612.html
- OIDC 文档: https://help.aliyun.com/document_detail/438099.html