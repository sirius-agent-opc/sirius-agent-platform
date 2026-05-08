#!/bin/bash
# VPN 启动脚本 — mihomo + clash 订阅
set -e

CONFIG_DIR="$HOME/.config/mihomo"
CONFIG_FILE="$CONFIG_DIR/config.yaml"
SUB_URL="https://mi.wwwowo.com/sub?target=clash&url=https%3A%2F%2Fsub4.wwwowo.com%2Fapi%2Fsubscribe%2F%3Fuid%3D8b32c9c1-2536-45f0-956b-9b0f6d3939cd%26country%3D"

mkdir -p "$CONFIG_DIR"

echo "🚀 启动 mihomo..."

# 拉取最新订阅
echo "  更新订阅配置..."
curl -sL "$SUB_URL" -o "$CONFIG_FILE"
echo "  配置已更新 ($(wc -c < $CONFIG_FILE) bytes)"

# 确保 HTTP 代理端口 7890 已启用（默认 clash 配置已有）
# 添加 system proxy 设置
cat >> "$CONFIG_FILE" << EOF

# system-proxy: true  # 系统代理
EOF

# 启动 mihomo（后台）
MIHOMO_BIN="/usr/local/bin/mihomo"
if [ ! -x "$MIHOMO_BIN" ]; then
    MIHOMO_BIN="$HOME/.local/bin/mihomo"
fi

nohup "$MIHOMO_BIN" -d "$CONFIG_DIR" > /tmp/mihomo.log 2>&1 &
PID=$!
echo "  PID: $PID"

# 等待启动
sleep 2
if kill -0 $PID 2>/dev/null; then
    echo "✅ mihomo 运行中 (端口 7890/7891)"
    echo "   HTTP 代理: http://127.0.0.1:7890"
    echo "   SOCKS5 代理: socks5://127.0.0.1:7891"
else
    echo "❌ 启动失败"
    cat /tmp/mihomo.log
    exit 1
fi
