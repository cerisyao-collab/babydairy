## ADDED Requirements

### Requirement: 系统必须能够构建 OpenClaw 远程安装包
系统 SHALL 能够打包 OpenClaw 及其所有依赖到单个压缩文件中。

#### Scenario: 成功构建安装包
- **WHEN** 用户运行构建脚本
- **THEN** 生成包含 OpenClaw 和所有依赖的 .tar.gz 文件

#### Scenario: 包含版本信息
- **WHEN** 构建完成时
- **THEN** 安装包文件名包含版本号（如 openclaw-2026.3.23-2.tar.gz）

### Requirement: 构建脚本必须验证依赖
构建脚本 SHALL 在打包前验证所有必需的依赖已安装。

#### Scenario: Node.js 存在检查
- **WHEN** 开始构建时
- **THEN** 检查 Node.js 是否已安装并报告版本

#### Scenario: npm 依赖检查
- **WHEN** 开始构建时
- **THEN** 验证 openclaw npm 包已全局安装

### Requirement: 安装包必须包含安装脚本
安装包 SHALL 包含 install.sh 脚本用于远程安装。

#### Scenario: 安装脚本执行
- **WHEN** 用户在远程服务器运行 install.sh
- **THEN** 自动安装 OpenClaw 到指定目录
