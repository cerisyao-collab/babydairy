#!/bin/bash
#
# build-openclaw-docs.sh - 打包 OpenClaw 核心文档
#
# 用法：./build-openclaw-docs.sh [版本号]
#

set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# 配置
OPENCLAW_ROOT="/opt/homebrew/lib/node_modules/openclaw"
OUTPUT_DIR="$BASE_DIR/dist/openclaw-docs"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 OpenClaw 安装
check_openclaw() {
    log_info "检查 OpenClaw 安装..."

    if [ ! -d "$OPENCLAW_ROOT" ]; then
        log_error "OpenClaw 未安装：$OPENCLAW_ROOT"
        exit 1
    fi

    log_info "OpenClaw 路径：$OPENCLAW_ROOT"
}

# 获取版本号
get_version() {
    if [ -n "$1" ]; then
        VERSION="$1"
    else
        VERSION=$(cat "$OPENCLAW_ROOT/package.json" | grep '"version"' | sed 's/.*"version": "//;s/".*//')
    fi

    log_info "OpenClaw 版本：$VERSION"
}

# 创建输出目录
create_output_dir() {
    log_info "创建输出目录..."
    mkdir -p "$OUTPUT_DIR"
}

# 打包文档
package_docs() {
    PACKAGE_NAME="openclaw-docs-${VERSION}"
    TEMP_DIR=$(mktemp -d)
    PACKAGE_DIR="$TEMP_DIR/$PACKAGE_NAME"

    log_info "创建临时目录：$PACKAGE_DIR"
    mkdir -p "$PACKAGE_DIR"

    # 复制根目录文档
    log_info "复制根目录文档..."
    cp "$OPENCLAW_ROOT/README.md" "$PACKAGE_DIR/"
    cp "$OPENCLAW_ROOT/CHANGELOG.md" "$PACKAGE_DIR/"
    cp "$OPENCLAW_ROOT/LICENSE" "$PACKAGE_DIR/"

    # 复制核心文档模板
    log_info "复制核心文档模板..."
    mkdir -p "$PACKAGE_DIR/templates"
    cp "$OPENCLAW_ROOT/docs/reference/templates/SOUL.md" "$PACKAGE_DIR/templates/"
    cp "$OPENCLAW_ROOT/docs/reference/templates/IDENTITY.md" "$PACKAGE_DIR/templates/"

    # 复制 HOOK.md 文件
    log_info "复制 HOOK 文件..."
    mkdir -p "$PACKAGE_DIR/hooks"
    for hook in "$OPENCLAW_ROOT/dist/bundled/"*/HOOK.md; do
        if [ -f "$hook" ]; then
            hook_name=$(basename $(dirname "$hook"))
            cp "$hook" "$PACKAGE_DIR/hooks/${hook_name}.md"
        fi
    done

    # 复制技能文档模板
    log_info "复制技能文档..."
    mkdir -p "$PACKAGE_DIR/skills"
    for skill_dir in "$OPENCLAW_ROOT/dist/extensions/"*/skills/*/; do
        if [ -d "$skill_dir" ]; then
            skill_name=$(basename "$skill_dir")
            mkdir -p "$PACKAGE_DIR/skills/$skill_name"
            cp "$skill_dir"/*.md "$PACKAGE_DIR/skills/$skill_name/" 2>/dev/null || true
        fi
    done

    # 复制 docs 目录
    log_info "复制 docs 目录..."
    cp -r "$OPENCLAW_ROOT/docs" "$PACKAGE_DIR/"

    # 创建版本文件
    log_info "创建版本文件..."
    cat > "$PACKAGE_DIR/VERSION" << EOF
Package: openclaw-docs
Version: $VERSION
Build Date: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
Source: $OPENCLAW_ROOT
EOF

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

    log_info "打包完成！"
    log_info "安装包：$OUTPUT_DIR/$PACKAGE_NAME.tar.gz"
    log_info "校验和：$OUTPUT_DIR/$PACKAGE_NAME.tar.gz.sha256"
}

# 显示安装包内容
show_package_contents() {
    log_info "安装包内容："
    tar -tzf "$OUTPUT_DIR/$PACKAGE_NAME.tar.gz" | head -30
}

# 主函数
main() {
    log_info "=== OpenClaw 文档打包工具 ==="
    echo ""

    # 检查依赖
    check_openclaw
    get_version "$1"
    create_output_dir

    # 打包
    package_docs

    # 显示内容
    echo ""
    show_package_contents

    echo ""
    log_info "=== 打包完成 ==="
}

# 执行主函数
main "$@"
