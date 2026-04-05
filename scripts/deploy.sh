#!/bin/bash
#
# deploy.sh - OpenClaw 远程部署脚本
#
# 用法：./deploy.sh <远程主机> [选项]
#

set -e

# 配置
DEFAULT_SSH_PORT="22"
DEFAULT_REMOTE_DIR="/opt/openclaw"
DEFAULT_USER="root"

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

# 显示使用说明
show_usage() {
    echo "用法：$0 <远程主机> [选项]"
    echo ""
    echo "参数:"
    echo "  远程主机             远程服务器地址（IP 或域名）"
    echo ""
    echo "选项:"
    echo "  -u, --user USER      SSH 用户名（默认：$DEFAULT_USER）"
    echo "  -p, --port PORT      SSH 端口（默认：$DEFAULT_SSH_PORT）"
    echo "  -d, --dir DIR        远程安装目录（默认：$DEFAULT_REMOTE_DIR）"
    echo "  -f, --file FILE      安装包路径（默认：./dist/中最新的安装包）"
    echo "  -h, --help           显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 192.168.1.100                              # 使用默认配置"
    echo "  $0 192.168.1.100 -u admin -p 2222             # 指定用户和端口"
    echo "  $0 192.168.1.100 -f ./dist/openclaw-*.tar.gz  # 指定安装包"
    echo ""
}

# 解析参数
parse_args() {
    REMOTE_HOST=""
    SSH_USER="$DEFAULT_USER"
    SSH_PORT="$DEFAULT_SSH_PORT"
    REMOTE_DIR="$DEFAULT_REMOTE_DIR"
    PACKAGE_FILE=""

    while [[ $# -gt 0 ]]; do
        case $1 in
            -u|--user)
                SSH_USER="$2"
                shift 2
                ;;
            -p|--port)
                SSH_PORT="$2"
                shift 2
                ;;
            -d|--dir)
                REMOTE_DIR="$2"
                shift 2
                ;;
            -f|--file)
                PACKAGE_FILE="$2"
                shift 2
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                if [ -z "$REMOTE_HOST" ]; then
                    REMOTE_HOST="$1"
                else
                    log_error "未知参数：$1"
                    show_usage
                    exit 1
                fi
                shift
                ;;
        esac
    done

    if [ -z "$REMOTE_HOST" ]; then
        log_error "请指定远程主机地址"
        show_usage
        exit 1
    fi
}

# 查找安装包
find_package() {
    if [ -z "$PACKAGE_FILE" ]; then
        # 查找 dist 目录中最新的安装包
        if [ -d "./dist" ]; then
            PACKAGE_FILE=$(ls -t ./dist/openclaw-*.tar.gz 2>/dev/null | head -1)
        fi
    fi

    if [ ! -f "$PACKAGE_FILE" ]; then
        log_error "未找到安装包：$PACKAGE_FILE"
        log_info "请先运行 ./build-remote-package.sh 构建安装包"
        exit 1
    fi

    log_info "使用安装包：$PACKAGE_FILE"
}

# 测试 SSH 连接
test_ssh_connection() {
    log_info "测试 SSH 连接到 $REMOTE_HOST..."

    if ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no -p "$SSH_PORT" "$SSH_USER@$REMOTE_HOST" "echo '连接成功'" > /dev/null 2>&1; then
        log_info "SSH 连接成功"
    else
        log_error "SSH 连接失败，请检查："
        echo "  - 远程主机地址是否正确"
        echo "  - SSH 端口是否正确"
        echo "  - 用户名和密码/密钥是否正确"
        echo "  - 网络连接是否正常"
        exit 1
    fi
}

# 传输安装包
transfer_package() {
    log_info "传输安装包到远程服务器..."

    # 在远程服务器创建临时目录
    TEMP_DIR=$(ssh -p "$SSH_PORT" "$SSH_USER@$REMOTE_HOST" "mktemp -d")
    log_info "远程临时目录：$TEMP_DIR"

    # 传输文件
    scp -P "$SSH_PORT" "$PACKAGE_FILE" "$SSH_USER@$REMOTE_HOST:$TEMP_DIR/"

    log_info "传输完成"
}

# 远程安装
remote_install() {
    log_info "在远程服务器上安装 OpenClaw..."

    ssh -p "$SSH_PORT" "$SSH_USER@$REMOTE_HOST" << EOF
        cd $TEMP_DIR
        tar -xzf *.tar.gz
        cd openclaw-*/

        # 创建安装目录
        sudo mkdir -p $REMOTE_DIR

        # 移动文件
        sudo mv * $REMOTE_DIR/

        # 设置权限
        sudo chmod +x \$REMOTE_DIR/bin/* 2>/dev/null || true
        sudo chmod +x \$REMOTE_DIR/*.sh 2>/dev/null || true

        # 创建环境变量文件
        cat | sudo tee \$REMOTE_DIR/openclaw-env.sh > /dev/null << ENVEOF
# OpenClaw 环境变量
export OPENCLAW_HOME="$REMOTE_DIR"
export PATH="\$OPENCLAW_HOME:\$PATH"
ENVEOF

        # 清理临时目录
        cd /tmp
        rm -rf $TEMP_DIR

        echo "OpenClaw 已安装到 $REMOTE_DIR"
EOF

    log_info "远程安装完成"
}

# 显示安装说明
show_post_install_info() {
    echo ""
    log_info "=== 部署完成 ==="
    echo ""
    echo "在远程服务器上，执行以下命令以使用 OpenClaw："
    echo ""
    echo "  # 临时添加到 PATH"
    echo "  ssh $SSH_USER@$REMOTE_HOST 'source $REMOTE_DIR/openclaw-env.sh'"
    echo ""
    echo "  # 永久添加"
    echo "  ssh $SSH_USER@$REMOTE_HOST \"echo 'source $REMOTE_DIR/openclaw-env.sh' >> ~/.bashrc\""
    echo ""
    echo "  # 验证安装"
    echo "  ssh $SSH_USER@$REMOTE_HOST 'openclaw --version'"
    echo ""
}

# 主函数
main() {
    log_info "=== OpenClaw 远程部署工具 ==="
    echo ""

    # 解析参数
    parse_args "$@"

    # 查找安装包
    find_package

    # 测试 SSH 连接
    test_ssh_connection

    # 传输安装包
    transfer_package

    # 远程安装
    remote_install

    # 显示安装说明
    show_post_install_info
}

# 执行主函数
main "$@"
