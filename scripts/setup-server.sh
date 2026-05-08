#!/bin/bash
# 服务器初始化脚本
set -e

REPO="https://github.com/sirius-agent-opc/sirius-agent-platform.git"
TARGET="$HOME/projects/sirius-agent-platform"

echo "🚀 设置开发服务器..."

# 安装 Node（如果不存在）
if ! command -v node &> /dev/null; then
    echo "📦 安装 Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

# 克隆仓库
if [ ! -d "$TARGET" ]; then
    mkdir -p "$(dirname "$TARGET")"
    git clone "$REPO" "$TARGET"
    echo "✅ 仓库已克隆"
else
    cd "$TARGET" && git pull
    echo "✅ 仓库已更新"
fi

# 项目初始化
cd "$TARGET"
npm init -y 2>/dev/null || true
echo "✅ 项目初始化完成"
