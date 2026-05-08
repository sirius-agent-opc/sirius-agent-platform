#!/bin/bash
# 磁盘使用检查
THRESHOLD=85  # 使用率超过此值告警

USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')

if [ "$USAGE" -gt "$THRESHOLD" ]; then
    echo "[$(date)] ⚠️ 磁盘使用率 ${USAGE}%，超过阈值 ${THRESHOLD}%"
    echo "  清理建议: docker system prune -f"
else
    echo "[$(date)] ✅ 磁盘使用率 ${USAGE}%，正常"
fi
