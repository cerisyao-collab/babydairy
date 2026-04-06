## ADDED Requirements

### Requirement: 系统必须支持 OpenClaw 版本管理
系统 SHALL 支持指定和切换 OpenClaw 版本。

#### Scenario: 指定版本构建
- **WHEN** 用户指定版本号
- **THEN** 构建该版本的安装包

#### Scenario: 默认最新版本
- **WHEN** 用户未指定版本
- **THEN** 默认构建最新安装的版本

### Requirement: 版本信息必须记录
安装包 SHALL 包含版本信息文件。

#### Scenario: 版本文件包含
- **WHEN** 构建完成时
- **THEN** 安装包包含 version.txt 文件

#### Scenario: 安装后查询
- **WHEN** 安装完成后
- **THEN** 用户可以查询安装的版本号
