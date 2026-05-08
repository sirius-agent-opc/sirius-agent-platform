"""
邮件监控 — 检测 Gmail 新邮件 (使用 STARTTLS 方式)
"""
import imaplib, json, os, socket, time
from email import message_from_bytes
from datetime import datetime

EMAIL = "sirius.nrly@gmail.com"
PASSWORD = "ihsdlzmqawlhlzja"
PROJECT_DIR = os.path.expanduser("~/projects/sirius-agent")
NOTIFY_FILE = os.path.join(PROJECT_DIR, "data/notifications/new_email.json")

def check_inbox():
    socket.setdefaulttimeout(20)
    
    for attempt in range(2):
        try:
            # 先用明文连接，再升级到 TLS (比直接 SSL 更稳定)
            mail = imaplib.IMAP4("imap.gmail.com", 143)
            mail.starttls()
            mail.login(EMAIL, PASSWORD)
            mail.select("INBOX")

            status, ids = mail.search(None, "(UNSEEN)")
            if status != "OK" or not ids[0]:
                mail.close()
                mail.logout()
                return {"status": "ok", "unread": 0, "new": False}

            ids_list = ids[0].split()
            for num in ids_list:
                status, data = mail.fetch(num, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT)])")
                if status != "OK":
                    continue

                msg = message_from_bytes(data[0][1])
                subject = str(msg.get("Subject", ""))
                sender = str(msg.get("From", ""))

                # 跳过 GitHub 通知
                if "notifications@github.com" in sender:
                    continue

                keywords = ["需求", "咨询", "合作", "报价", "agent", "AI", "hello", "hi", "test", "测试", "sirius"]
                if any(k in subject.lower() for k in keywords):
                    entry = {
                        "from": sender,
                        "subject": subject.replace("\r", "").replace("\n", ""),
                        "received_at": datetime.now().isoformat(),
                    }
                    os.makedirs(os.path.dirname(NOTIFY_FILE), exist_ok=True)
                    with open(NOTIFY_FILE, "w") as f:
                        json.dump(entry, f, ensure_ascii=False)
                    mail.close()
                    mail.logout()
                    return {"status": "ok", "unread": len(ids_list), "new": True, "entry": entry}

            mail.close()
            mail.logout()
            return {"status": "ok", "unread": len(ids_list), "new": False}

        except Exception as e:
            print(f"Attempt {attempt+1}: {e}")
            if attempt < 1:
                time.sleep(3)
            continue

    return {"status": "error", "error": str(e) if 'e' in dir() else "failed"}

if __name__ == "__main__":
    result = check_inbox()
    print(json.dumps(result, ensure_ascii=False))
