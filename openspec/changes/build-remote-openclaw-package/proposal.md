## Why

目前 OpenClaw 仅支持本地安装（通过 Homebrew 或 npm），无法在远程服务器上使用。用户希望在远程服务器上部署 OpenClaw 以支持团队协作、集中化管理和云端开发场景。

## What Changes

- **远程安装包构建脚本**：创建可打包 OpenClaw 及其依赖的脚本
- **远程部署配置**：支持配置远程服务器连接和部署参数
- **离线包支持**：生成包含所有依赖的完整安装包，支持无网络环境部署
- **版本管理**：支持指定和切换 OpenClaw 版本

## Capabilities

### New Capabilities

- `remote-package-build`: 构建远程安装包的脚本和配置
- `remote-deployment`: 远程服务器部署支持
- `offline-package`: 离线安装包生成
- `version-management`: OpenClaw 版本管理

### Modified Capabilities

<!-- 无现有能力修改 -->

## Impact

- **新增文件**: `scripts/build-remote-package.sh`, `config/deploy.yaml`
- **依赖**: Node.js, npm, tar/rsync
- **目标平台**: macOS (本地构建) → Linux/Unix (远程部署)
