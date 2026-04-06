## ADDED Requirements

### Requirement: 系统必须支持生成离线安装包
系统 SHALL 能够生成包含所有依赖的离线安装包。

#### Scenario: 完整依赖打包
- **WHEN** 生成离线包时
- **THEN** 包含所有 node_modules 依赖

#### Scenario: 无网络环境安装
- **WHEN** 在无网络服务器上安装
- **THEN** 安装包能够正常安装无需外部依赖

### Requirement: 离线包必须验证完整性
离线安装包 SHALL 提供校验和验证。

#### Scenario: SHA256 校验和生成
- **WHEN** 构建完成时
- **THEN** 生成 .sha256 校验和文件

#### Scenario: 安装前验证
- **WHEN** 安装前
- **THEN** 可验证安装包完整性
