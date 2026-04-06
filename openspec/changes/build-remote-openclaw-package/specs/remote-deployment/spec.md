## ADDED Requirements

### Requirement: 系统必须支持远程服务器部署
系统 SHALL 支持将 OpenClaw 部署到远程服务器。

#### Scenario: SSH 连接建立
- **WHEN** 用户提供远程服务器地址和凭据
- **THEN** 系统能够建立 SSH 连接

#### Scenario: 文件传输
- **WHEN** SSH 连接建立后
- **THEN** 安装包能够传输到远程服务器

### Requirement: 部署必须支持配置参数
部署脚本 SHALL 支持配置远程服务器参数。

#### Scenario: 自定义部署目录
- **WHEN** 用户指定目标目录
- **THEN** OpenClaw 安装到指定目录

#### Scenario: 自定义 SSH 端口
- **WHEN** 用户使用非标准 SSH 端口
- **THEN** 部署脚本能够使用指定端口连接
