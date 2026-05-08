#!/bin/bash
# 邮件监控 — 用 openssl 通过 IMAP 检查 Gmail
# 比 Python imaplib 更可靠

EMAIL="sirius.nrly@gmail.com"
PASS="ihsdlzmqawlhlzja"
NOTIFY_FILE="$HOME/projects/sirius-agent/data/notifications/new_email.json"
LOG="/tmp/email-monitor.log"

# 通过 openssl 执行 IMAP 命令
result=$(echo -e \
    "1 LOGIN $EMAIL $PASS\r\n" \
    "2 SELECT INBOX\r\n" \
    "3 SEARCH UNSEEN\r\n" \
    "4 LOGOUT\r\n" | timeout 15 openssl s_client -connect imap.gmail.com:993 -quiet 2>/dev/null)

if [ $? -ne 0 ] || [ -z "$result" ]; then
    echo "[$(date)] 连接失败" >> "$LOG"
    exit 1
fi

# 提取未读数量
unseen_count=$(echo "$result" | grep -oP '\* SEARCH \K.*' | head -1)
if [ -z "$unseen_count" ]; then
    echo "[$(date)] 无新邮件" >> "$LOG"
    exit 0
fi

echo "[$(date)] 未读: $unseen_count" >> "$LOG"
# 写入通知
echo "{\"from\":\"gmail\",\"subject\":\"有 $unseen_count 封未读邮件\",\"count\":$unseen_count,\"received_at\":\"$(date -Iseconds)\"}" > "$NOTIFY_FILE"
exit 0
