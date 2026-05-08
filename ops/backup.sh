#!/bin/bash
# 备份脚本 — 代码 + 数据
set -e

BACKUP_DIR="$HOME/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

mkdir -p "$BACKUP_DIR"

echo "📦 开始备份..."

# 1. 代码备份 (git bundle)
cd ~/projects/sirius-agent
git bundle create "$BACKUP_DIR/sirius-agent-$DATE.bundle" --all 2>/dev/null
echo "  ✅ 代码: sirius-agent-$DATE.bundle"

# 2. 数据备份 (客户需求等)
if [ -d data/contacts ]; then
    tar czf "$BACKUP_DIR/data-$DATE.tar.gz" data/ 2>/dev/null
    echo "  ✅ 数据: data-$DATE.tar.gz"
fi

# 3. 清理旧备份 (保留30天)
find "$BACKUP_DIR" -name "*.bundle" -mtime +$RETENTION_DAYS -delete 2>/dev/null
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null

echo "✅ 备份完成 (保留 ${RETENTION_DAYS} 天)"
echo "   路径: $BACKUP_DIR"
