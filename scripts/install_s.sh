#!/bin/bash
# 安装 Serverless Devs CLI 工具

# 方式1: 使用 npm 安装
npm install -g @serverless-devs/s

# 方式2: 使用 yarn 安装
# yarn global add @serverless-devs/s

# 验证安装
s -v

# 配置阿里云凭证
# s config add
# 输入 AccessKeyID 和 AccessKeySecret