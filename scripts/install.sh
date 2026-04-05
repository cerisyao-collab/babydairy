#!/bin/bash
#
# install.sh - OpenClaw 远程安装脚本
#
# 用法：./install.sh [目标目录]
#       目标目录可选，默认为 /opt/openclaw
#

set -e

# 配置
DEFAULT_INSTALL_DIR="/opt/openclaw"

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
        log_error "Node.js 未安装，请先安装 Node.js (v16+)"
        exit 1
    fi
    NODE_VERSION=$(node -v)
    log_info "Node.js 版本：$NODE_VERSION"
}

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 确定安装目录
get_install_dir() {
    if [ -n "$1" ]; then
        INSTALL_DIR="$1"
    else
        INSTALL_DIR="$DEFAULT_INSTALL_DIR"
    fi

    # 处理相对路径
    if [[ "$INSTALL_DIR" != /* ]]; then
        INSTALL_DIR="$(pwd)/$INSTALL_DIR"
    fi
}

# 检查目标目录
check_install_dir() {
    if [ -d "$INSTALL_DIR" ]; then
        log_warn "目标目录已存在：$INSTALL_DIR"
        read -p "是否覆盖安装？(y/N): " confirm
        if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
            log_info "安装已取消"
            exit 0
        fi
        log_info "删除现有安装..."
        rm -rf "$INSTALL_DIR"
    fi

    log_info "创建安装目录：$INSTALL_DIR"
    mkdir -p "$INSTALL_DIR"
}

# 解压安装包
extract_package() {
    log_info "解压安装包..."

    # 找到压缩包（当前目录或脚本所在目录）
    if [ -f "openclaw-*.tar.gz" ]; then
        PACKAGE_FILE="openclaw-*.tar.gz"
    elif [ -f "$SCRIPT_DIR/openclaw-*.tar.gz" ]; then
        PACKAGE_FILE="$SCRIPT_DIR/openclaw-*.tar.gz"
    else
        log_error "未找到 OpenClaw 安装包"
        exit 1
    fi

    # 解压到临时目录
    TEMP_DIR=$(mktemp -d)
    tar -xzf $PACKAGE_FILE -C "$TEMP_DIR"

    # 移动文件到安装目录
    mv "$TEMP_DIR"/*/* "$INSTALL_DIR/"
    rm -rf "$TEMP_DIR"

    log_info "安装完成：$INSTALL_DIR"
}

# 设置权限
set_permissions() {
    log_info "设置文件权限..."
    chmod +x "$INSTALL_DIR"/bin/* 2>/dev/null || true
    chmod +x "$INSTALL_DIR"/*.sh 2>/dev/null || true
}

# 配置环境变量
setup_environment() {
    log_info "配置环境变量..."

    # 创建配置文件
    cat > "$INSTALL_DIR/openclaw-env.sh" << EOF
# OpenClaw 环境变量
export OPENCLAW_HOME="$INSTALL_DIR"
export PATH="\$OPENCLAW_HOME:\$PATH"
EOF

    echo ""
    log_info "=== 安装完成 ==="
    echo ""
    echo "要将 OpenClaw 添加到 PATH，请执行以下命令之一："
    echo ""
    echo "  # 当前会话临时添加"
    echo "  source $INSTALL_DIR/openclaw-env.sh"
    echo ""
    echo "  # 永久添加（~/.bashrc 或 ~/.zshrc）"
    echo "  echo 'source $INSTALL_DIR/openclaw-env.sh' >> ~/.bashrc"
    echo "  source ~/.bashrc"
    echo ""
    echo "验证安装："
    echo "  openclaw --version"
    echo ""
}

# 主函数
main() {
    log_info "=== OpenClaw 远程安装工具 ==="
    echo ""

    # 检查依赖
    check_nodejs

    # 获取安装目录
    get_install_dir "$1"

    # 检查目标目录
    check_install_dir

    # 解压安装包
    extract_package

    # 设置权限
    set_permissions

    # 配置环境变量
    setup_environment
}

# 执行主函数
main "$@"
