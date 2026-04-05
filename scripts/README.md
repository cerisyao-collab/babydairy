# OpenClaw 远程安装包

将 OpenClaw 打包成可远程部署的安装包，支持离线安装和团队协作。

## 快速开始

### 1. 构建安装包

```bash
# 使用当前安装的版本
./scripts/build-remote-package.sh

# 使用指定版本
./scripts/build-remote-package.sh 2026.3.23-2
```

构建完成后，安装包位于 `./dist/` 目录。

### 2. 本地安装（测试）

```bash
cd dist
tar -xzf openclaw-*.tar.gz
cd openclaw-*/
./install.sh
```

### 3. 远程部署

```bash
# 部署到远程服务器
./scripts/deploy.sh 192.168.1.100

# 指定用户和端口
./scripts/deploy.sh 192.168.1.100 -u admin -p 2222

# 指定安装包
./scripts/deploy.sh 192.168.1.100 -f ./dist/openclaw-*.tar.gz
```

## 脚本说明

### build-remote-package.sh

构建 OpenClaw 远程安装包。

**功能：**
- 检查 Node.js 和 npm 依赖
- 检查 OpenClaw 安装
- 打包所有文件和依赖
- 生成 SHA256 校验和

**参数：**
```bash
./scripts/build-remote-package.sh [版本号]
```

### install.sh

在目标服务器上安装 OpenClaw。

**功能：**
- 检查 Node.js 环境
- 解压安装包
- 设置文件权限
- 配置环境变量

**参数：**
```bash
./install.sh [安装目录]
```

### deploy.sh

部署 OpenClaw 到远程服务器。

**功能：**
- SSH 连接测试
- SCP 文件传输
- 远程执行安装

**参数：**
```bash
./scripts/deploy.sh <远程主机> [选项]

选项:
  -u, --user USER      SSH 用户名（默认：root）
  -p, --port PORT      SSH 端口（默认：22）
  -d, --dir DIR        远程安装目录（默认：/opt/openclaw）
  -f, --file FILE      安装包路径
  -h, --help           显示帮助
```

## 配置文件

编辑 `config/deploy.yaml` 自定义默认配置：

```yaml
ssh:
  user: root
  port: 22

deploy:
  remote_dir: /opt/openclaw

version:
  default: latest
```

## 验证安装包

```bash
# 验证校验和
shasum -a 256 -c openclaw-*.tar.gz.sha256

# 应该显示：openclaw-*.tar.gz: OK
```

## 故障排除

### 问题：SSH 连接失败

**解决方案：**
1. 检查远程主机地址是否正确
2. 检查 SSH 端口是否正确
3. 检查防火墙设置
4. 使用 `-v` 参数查看详细信息：`ssh -v user@host`

### 问题：Node.js 版本不兼容

**解决方案：**
- 确保远程服务器 Node.js 版本 >= 16
- 使用 `node -v` 检查版本

### 问题：权限错误

**解决方案：**
- 确保使用有足够权限的用户
- 使用 `sudo` 执行安装脚本

## 文件结构

```
babyjour/
├── scripts/
│   ├── build-remote-package.sh   # 构建脚本
│   ├── install.sh                # 安装脚本
│   └── deploy.sh                 # 部署脚本
├── config/
│   └── deploy.yaml               # 配置文件
└── dist/                         # 构建输出
    ├── openclaw-<version>.tar.gz
    └── openclaw-<version>.tar.gz.sha256
```
