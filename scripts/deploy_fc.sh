#!/bin/bash
# Baby Diary API - FC 部署脚本
# 使用 Serverless Devs 部署到阿里云函数计算

set -e

echo "========================================"
echo "Baby Diary API - FC 部署"
echo "========================================"

# 检查必要的环境变量
check_env_vars() {
    local missing=()

    # 检查阿里云凭证
    if [ -z "$ALICLOUD_ACCESS_KEY" ]; then
        missing+=("ALICLOUD_ACCESS_KEY")
    fi
    if [ -z "$ALICLOUD_SECRET_KEY" ]; then
        missing+=("ALICLOUD_SECRET_KEY")
    fi

    # 检查 VPC 配置（从 Terraform 输出获取）
    if [ -z "$VPC_ID" ]; then
        missing+=("VPC_ID")
    fi
    if [ -z "$VSWITCH_ID" ]; then
        missing+=("VSWITCH_ID")
    fi
    if [ -z "$SECURITY_GROUP_ID" ]; then
        missing+=("SECURITY_GROUP_ID")
    fi

    # 检查数据库配置
    if [ -z "$DATABASE_URL" ]; then
        missing+=("DATABASE_URL")
    fi

    # 检查微信配置
    if [ -z "$WECHAT_APP_ID" ]; then
        missing+=("WECHAT_APP_ID")
    fi
    if [ -z "$WECHAT_APP_SECRET" ]; then
        missing+=("WECHAT_APP_SECRET")
    fi

    # 检查 JWT 配置
    if [ -z "$JWT_SECRET" ]; then
        missing+=("JWT_SECRET")
    fi

    if [ ${#missing[@]} -gt 0 ]; then
        echo "错误: 缺少以下环境变量:"
        printf '  - %s\n' "${missing[@]}"
        echo ""
        echo "请设置环境变量后重试。"
        echo ""
        echo "示例:"
        echo "  export VPC_ID=vpc-xxx"
        echo "  export VSWITCH_ID=vsw-xxx"
        echo "  export SECURITY_GROUP_ID=sg-xxx"
        echo "  export DATABASE_URL='postgresql://user:pass@host:5432/db'"
        echo "  export WECHAT_APP_ID=wx..."
        echo "  export WECHAT_APP_SECRET=..."
        echo "  export JWT_SECRET=..."
        exit 1
    fi
}

# 检查 s CLI 是否安装
check_s_cli() {
    if ! command -v s &> /dev/null; then
        echo "错误: Serverless Devs CLI 未安装"
        echo ""
        echo "安装方法:"
        echo "  npm install -g @serverless-devs/s"
        echo ""
        echo "或使用安装脚本:"
        echo "  ./scripts/install_s.sh"
        exit 1
    fi
    echo "✓ Serverless Devs CLI 已安装: $(s -v)"
}

# 配置阿里云凭证
configure_credentials() {
    echo ""
    echo "配置阿里云凭证..."
    if [ -f ~/.s/access.yaml ]; then
        echo "✓ 凭证已配置"
    else
        echo "请配置阿里云凭证:"
        s config add
    fi
}

# 本地测试
local_test() {
    echo ""
    echo "========================================"
    echo "本地测试"
    echo "========================================"
    echo ""
    echo "启动本地调试..."
    echo "访问 http://localhost:9000 测试 API"
    echo ""
    s local start
}

# 部署到 FC
deploy() {
    echo ""
    echo "========================================"
    echo "部署到 FC"
    echo "========================================"
    echo ""
    s deploy
}

# 执行数据库迁移
migrate_db() {
    echo ""
    echo "========================================"
    echo "数据库迁移"
    echo "========================================"
    echo ""
    echo "执行 Alembic 迁移..."
    s exec --command "alembic upgrade head"
    echo "✓ 数据库迁移完成"
}

# 验证部署
verify() {
    echo ""
    echo "========================================"
    echo "验证部署"
    echo "========================================"
    echo ""

    # 获取 FC HTTP 端点
    ENDPOINT=$(s info | grep -oP 'httpTrigger: \K.*')

    if [ -z "$ENDPOINT" ]; then
        echo "警告: 无法获取 HTTP 触发器端点"
        echo "请手动检查部署状态: s info"
        return
    fi

    echo "API 端点: $ENDPOINT"
    echo ""
    echo "健康检查..."
    curl -s "$ENDPOINT/api/health" || echo "警告: 健康检查失败"

    echo ""
    echo "✓ 部署验证完成"
}

# 主流程
main() {
    case "${1:-deploy}" in
        check)
            check_env_vars
            check_s_cli
            echo ""
            echo "✓ 环境检查通过"
            ;;
        local)
            check_env_vars
            check_s_cli
            local_test
            ;;
        deploy)
            check_env_vars
            check_s_cli
            configure_credentials
            deploy
            migrate_db
            verify
            ;;
        migrate)
            migrate_db
            ;;
        verify)
            verify
            ;;
        *)
            echo "用法: $0 {check|local|deploy|migrate|verify}"
            exit 1
            ;;
    esac
}

main "$@"