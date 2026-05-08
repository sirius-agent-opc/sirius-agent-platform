#!/bin/bash
# 监控脚本 — API 挂了自动重启
set -e

API_PORT=8000
PROJECT_DIR="$HOME/projects/sirius-agent"
LOG_FILE="/tmp/api.log"

# 检查端口
if ! curl -sf "http://localhost:$API_PORT/health" > /dev/null 2>&1; then
    echo "[$(date)] ❌ API 无响应，尝试重启..."
    
    # 杀旧进程
    kill $(lsof -t -i:$API_PORT) 2>/dev/null || true
    sleep 2
    
    # 重启
    cd "$PROJECT_DIR"
    export PATH="$PATH:/home/yuanyf/.local/bin"
    export OPENAI_API_KEY="sk-1c7940eff7824ea0885f65551edd7c26"
    export OPENAI_BASE_URL="https://api.deepseek.com/v1"
    
    nohup uvicorn services.api.main:app --host 0.0.0.0 --port $API_PORT > "$LOG_FILE" 2>&1 &
    sleep 3
    
    if curl -sf "http://localhost:$API_PORT/health" > /dev/null 2>&1; then
        echo "[$(date)] ✅ 重启成功"
    else
        echo "[$(date)] ❌ 重启失败，需要人工介入"
    fi
else
    echo "[$(date)] ✅ API 运行正常"
fi
