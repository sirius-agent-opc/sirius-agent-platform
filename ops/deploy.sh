#!/bin/bash
# 一键部署 — 拉代码 + 重启
set -e

cd ~/projects/sirius-agent
echo "🚀 开始部署..."

# 拉取最新代码
git pull origin main
echo "✅ 代码已更新"

# 安装依赖 (Python)
pip install --break-system-packages -r requirements.txt 2>/dev/null | tail -1

# 重启 API
kill $(lsof -t -i:8000) 2>/dev/null || true
sleep 2

export PATH="$PATH:/home/yuanyf/.local/bin"
export OPENAI_API_KEY="sk-1c7940eff7824ea0885f65551edd7c26"
export OPENAI_BASE_URL="https://api.deepseek.com/v1"

nohup uvicorn services.api.main:app --host 0.0.0.0 --port 8000 > /tmp/api.log 2>&1 &
sleep 3

# 验证
if curl -sf localhost:8000/health > /dev/null 2>&1; then
    echo "✅ 部署成功！$(curl -s localhost:8000/health)"
else
    echo "❌ 部署失败"
    cat /tmp/api.log
fi
