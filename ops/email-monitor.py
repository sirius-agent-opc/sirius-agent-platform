"""
邮件监控 — 检测新客户邮件，写入通知文件供 OpenClaw 检测
"""
import imaplib, ssl, json, os, time, sys, socket
from email import message_from_bytes
from datetime import datetime

EMAIL = "sirius.nrly@gmail.com"
PASSWORD = "ihsdlzmqawlhlzja"
PROJECT_DIR = os.path.expanduser("~/projects/sirius-agent")
NOTIFY_FILE = os.path.join(PROJECT_DIR, "data/notifications/new_email.json")

# 设置超时
socket.setdefaulttimeout(15)

def check_inbox():
    try:
        ctx = ssl.create_default_context()
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993, ssl_context=ctx)
        mail.login(EMAIL, PASSWORD)
        mail.select("INBOX")

        # 只看最新未读
        status, ids = mail.search(None, "(UNSEEN)")
        if status != "OK" or not ids[0]:
            mail.close()
            mail.logout()
            return False

        all_ids = ids[0].split()
        latest = all_ids[-1]  # 只看最新一封

        status, data = mail.fetch(latest, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT)])")
        if status != "OK":
            mail.close()
            mail.logout()
            return False

        msg = message_from_bytes(data[0][1])
        subject = str(msg.get("Subject", ""))
        sender = str(msg.get("From", ""))

        keywords = ["需求", "咨询", "合作", "报价", "agent", "AI", "hello", "hi"]
        if any(k in subject.lower() for k in keywords):
            entry = {
                "from": sender,
                "subject": subject,
                "received_at": datetime.now().isoformat(),
            }
            os.makedirs(os.path.dirname(NOTIFY_FILE), exist_ok=True)
            with open(NOTIFY_FILE, "w") as f:
                json.dump(entry, f, ensure_ascii=False)
            print("NEW_EMAIL:" + json.dumps(entry, ensure_ascii=False))
            mail.close()
            mail.logout()
            return True

        mail.close()
        mail.logout()
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    check_inbox()
