#!/bin/bash
#
# build-remote-package.sh - 构建 OpenClaw 远程安装包
#
# 用法：./build-remote-package.sh [版本号]
#       版本号可选，默认为当前安装的版本
#

set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# 配置
OPENCLAW_PACKAGE_NAME="openclaw"
DEFAULT_INSTALL_DIR="/opt/homebrew/lib/node_modules"
OUTPUT_DIR="$BASE_DIR/dist"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 Node.js 是否已安装
check_nodejs() {
    log_info "检查 Node.js 安装..."
    if ! command -v node &> /dev/null; then
        log_error "Node.js 未安装，请先安装 Node.js"
        exit 1
    fi
    NODE_VERSION=$(node -v)
    log_info "Node.js 版本：$NODE_VERSION"
}

# 检查 npm 是否已安装
check_npm() {
    log_info "检查 npm 安装..."
    if ! command -v npm &> /dev/null; then
        log_error "npm 未安装，请先安装 npm"
        exit 1
    fi
    NPM_VERSION=$(npm -v)
    log_info "npm 版本：$NPM_VERSION"
}

# 检查 OpenClaw 是否已全局安装
check_openclaw() {
    log_info "检查 OpenClaw 安装..."
    OPENCLAW_VERSION=$(npm ls -g openclaw --depth=0 2>/dev/null | grep openclaw@ | head -1 | sed 's/.*openclaw@//')

    if [ -z "$OPENCLAW_VERSION" ]; then
        log_error "OpenClaw 未全局安装"
        exit 1
    fi

    # 如果用户指定了版本号，使用用户指定的版本
    if [ -n "$1" ]; then
        OPENCLAW_VERSION="$1"
        log_info "使用指定版本：$OPENCLAW_VERSION"
    else
        log_info "OpenClaw 版本：$OPENCLAW_VERSION"
    fi
}

# 获取 OpenClaw 安装路径
get_openclaw_path() {
    NPM_ROOT=$(npm root -g)
    OPENCLAW_PATH="$NPM_ROOT/$OPENCLAW_PACKAGE_NAME"

    if [ ! -d "$OPENCLAW_PATH" ]; then
        log_error "OpenClaw 安装目录不存在：$OPENCLAW_PATH"
        exit 1
    fi

    log_info "OpenClaw 路径：$OPENCLAW_PATH"
}

# 创建输出目录
create_output_dir() {
    log_info "创建输出目录：$OUTPUT_DIR"
    mkdir -p "$OUTPUT_DIR"
}

# 打包 OpenClaw
package_openclaw() {
    PACKAGE_NAME="openclaw-${OPENCLAW_VERSION}-remote"
    TEMP_DIR=$(mktemp -d)
    PACKAGE_DIR="$TEMP_DIR/$PACKAGE_NAME"

    log_info "创建临时目录：$PACKAGE_DIR"
    mkdir -p "$PACKAGE_DIR"

    # 复制 OpenClaw 文件
    log_info "复制 OpenClaw 文件..."
    cp -r "$OPENCLAW_PATH"/* "$PACKAGE_DIR/"

    # 复制 node_modules 依赖
    log_info "复制 node_modules 依赖..."
    cp -r "$OPENCLAW_PATH/node_modules" "$PACKAGE_DIR/"

    # 创建版本文件
    log_info "创建版本文件..."
    echo "$OPENCLAW_VERSION" > "$PACKAGE_DIR/VERSION"
    date -u +"%Y-%m-%dT%H:%M:%SZ" > "$PACKAGE_DIR/BUILD_DATE"

    # 创建安装脚本
    log_info "创建安装脚本..."
    cp "$(dirname "$0")/install.sh" "$PACKAGE_DIR/" 2>/dev/null || cp "./install.sh" "$PACKAGE_DIR/"
    chmod +x "$PACKAGE_DIR/install.sh"

    # 创建压缩包
    log_info "创建压缩包..."
    cd "$TEMP_DIR"
    tar -czf "$OUTPUT_DIR/$PACKAGE_NAME.tar.gz" "$PACKAGE_NAME"

    # 生成 SHA256 校验和
    log_info "生成 SHA256 校验和..."
    cd "$OUTPUT_DIR"
    shasum -a 256 "$PACKAGE_NAME.tar.gz" > "$PACKAGE_NAME.tar.gz.sha256"

    # 清理临时目录
    log_info "清理临时目录..."
    rm -rf "$TEMP_DIR"

    log_info "构建完成！"
    log_info "安装包：$OUTPUT_DIR/$PACKAGE_NAME.tar.gz"
    log_info "校验和：$OUTPUT_DIR/$PACKAGE_NAME.tar.gz.sha256"
}

# 显示使用说明
show_usage() {
    echo "用法：$0 [版本号]"
    echo ""
    echo "参数:"
    echo "  版本号    可选，指定要打包的 OpenClaw 版本，默认为当前安装的版本"
    echo ""
    echo "示例:"
    echo "  $0                    # 使用当前安装的版本"
    echo "  $0 2026.3.23-2        # 使用指定版本"
    echo ""
}

# 主函数
main() {
    log_info "=== OpenClaw 远程安装包构建工具 ==="
    echo ""

    # 显示使用说明（如果用户请求帮助）
    if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
        show_usage
        exit 0
    fi

    # 检查依赖
    check_nodejs
    check_npm
    check_openclaw "$1"
    get_openclaw_path
    create_output_dir

    # 打包
    package_openclaw

    echo ""
    log_info "=== 构建完成 ==="
}

# 执行主函数
main "$@"
