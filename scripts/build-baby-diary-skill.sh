#!/bin/bash
#
# build-baby-diary-skill.sh - 打包 baby-diary 技能
#
# 用法：./build-baby-diary-skill.sh [版本号]
#

set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# 配置
SKILL_NAME="baby-diary"
SKILL_SOURCE="$HOME/.openclaw/skills/baby_diary_skill"
OUTPUT_DIR="$BASE_DIR/dist/skills"
VERSION_FILE="$SKILL_SOURCE/skill.toml"

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

# 检查技能源目录
check_source() {
    log_info "检查技能源目录..."

    if [ ! -d "$SKILL_SOURCE" ]; then
        log_error "技能源目录不存在：$SKILL_SOURCE"
        exit 1
    fi

    log_info "技能源目录：$SKILL_SOURCE"
}

# 获取版本号
get_version() {
    if [ -n "$1" ]; then
        VERSION="$1"
    elif [ -f "$VERSION_FILE" ]; then
        VERSION=$(grep '^version' "$VERSION_FILE" | sed 's/version = "//;s/"//')
    else
        VERSION=$(date +%Y%m%d)
    fi

    log_info "技能版本：$VERSION"
}

# 创建输出目录
create_output_dir() {
    log_info "创建输出目录..."
    mkdir -p "$OUTPUT_DIR"
}

# 打包技能
package_skill() {
    PACKAGE_NAME="${SKILL_NAME}-${VERSION}"
    TEMP_DIR=$(mktemp -d)
    PACKAGE_DIR="$TEMP_DIR/$PACKAGE_NAME"

    log_info "创建临时目录：$PACKAGE_DIR"
    mkdir -p "$PACKAGE_DIR"

    # 复制技能文件（只复制必要的文件）
    log_info "复制技能文件..."

    # 核心文件
    cp "$SKILL_SOURCE/SKILL.md" "$PACKAGE_DIR/"
    cp "$SKILL_SOURCE/README.md" "$PACKAGE_DIR/" 2>/dev/null || true
    cp "$SKILL_SOURCE/skill.toml" "$PACKAGE_DIR/" 2>/dev/null || true
    cp "$SKILL_SOURCE/openclaw.plugin.json" "$PACKAGE_DIR/" 2>/dev/null || true

    # baby-diary 核心代码
    if [ -d "$SKILL_SOURCE/baby-diary" ]; then
        cp -r "$SKILL_SOURCE/baby-diary" "$PACKAGE_DIR/"
        # 清理 Python 缓存
        find "$PACKAGE_DIR/baby-diary" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
        find "$PACKAGE_DIR/baby-diary" -name "*.pyc" -delete 2>/dev/null || true
    fi

    # 可选的 openspec 变更（如果有）
    for dir in openspec-apply-change openspec-archive-change openspec-explore openspec-propose; do
        if [ -d "$SKILL_SOURCE/$dir" ]; then
            cp -r "$SKILL_SOURCE/$dir" "$PACKAGE_DIR/"
        fi
    done

    # 创建版本文件
    log_info "创建版本文件..."
    cat > "$PACKAGE_DIR/VERSION" << EOF
Skill: $SKILL_NAME
Version: $VERSION
Build Date: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
Source: $SKILL_SOURCE
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
    tar -tzf "$OUTPUT_DIR/$PACKAGE_NAME.tar.gz" | head -20
}

# 主函数
main() {
    log_info "=== baby-diary 技能打包工具 ==="
    echo ""

    # 检查依赖
    check_source
    get_version "$1"
    create_output_dir

    # 打包
    package_skill

    # 显示内容
    echo ""
    show_package_contents

    echo ""
    log_info "=== 打包完成 ==="
}

# 执行主函数
main "$@"
