"""
邮件监控 — 通过 Gmail Atom Feed 检测新邮件 (通过代理)
"""
import json, os, re, subprocess
from datetime import datetime

EMAIL = "sirius.nrly@gmail.com"
PASSWORD = "ihsdlzmqawlhlzja"
PROJECT_DIR = os.path.expanduser("~/projects/sirius-agent")
NOTIFY_FILE = os.path.join(PROJECT_DIR, "data/notifications/new_email.json")
LAST_ID_FILE = os.path.join(PROJECT_DIR, "data/notifications/last_email_id.txt")

def get_atom_feed():
    """通过代理拉取 Gmail Atom Feed"""
    cmd = [
        "curl", "-s", "--connect-timeout", "10", "--max-time", "15",
        "-x", "http://127.0.0.1:7890",
        "-u", f"{EMAIL}:{PASSWORD}",
        "https://mail.google.com/mail/feed/atom"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def parse_feed(xml_text):
    """解析 Atom Feed，提取邮件条目"""
    entries = []
    # 提取每个 entry
    parts = xml_text.split("<entry>")
    if len(parts) < 2:
        return entries
    
    for part in parts[1:]:
        title = extract_tag(part, "title")
        summary = extract_tag(part, "summary")[:200]
        author_name = extract_tag(part, "author>name")
        author_email = extract_tag(part, "author>email")
        entry_id = extract_tag(part, "id")
        modified = extract_tag(part, "modified")
        
        entries.append({
            "id": entry_id,
            "title": title,
            "from": f"{author_name} <{author_email}>",
            "preview": summary[:100],
            "time": modified,
        })
    return entries

def extract_tag(text, tag_path):
    """提取 XML 标签内容，支持 author>name 格式"""
    if ">" in tag_path:
        # 嵌套标签: author>name -> 先找 <author> 再在里面找 <name>
        outer, inner = tag_path.split(">", 1)
        outer_match = re.search(f"<{outer}[^>]*>(.*?)</{outer}>", text, re.DOTALL)
        if outer_match:
            inner_match = re.search(f"<{inner}[^>]*>(.*?)</{inner}>", outer_match.group(1), re.DOTALL)
            return inner_match.group(1).strip() if inner_match else ""
        return ""
    match = re.search(f"<{tag_path}[^>]*>(.*?)</{tag_path}>", text, re.DOTALL)
    return match.group(1).strip() if match else ""

def load_last_id():
    """读取上次处理的最新邮件 ID"""
    if os.path.exists(LAST_ID_FILE):
        with open(LAST_ID_FILE) as f:
            return f.read().strip()
    return ""

def save_last_id(entry_id):
    """保存最新邮件 ID"""
    os.makedirs(os.path.dirname(LAST_ID_FILE), exist_ok=True)
    with open(LAST_ID_FILE, "w") as f:
        f.write(entry_id)

def check_mail():
    xml = get_atom_feed()
    if not xml or "fullcount" not in xml:
        print("FEED_FAILED")
        return False
    
    entries = parse_feed(xml)
    if not entries:
        print("NO_ENTRIES")
        return False
    
    fullcount = extract_tag(xml, "fullcount")
    print(f"COUNT: {fullcount} unread")
    
    # 跳过已知系统通知域名
    skip_domains = [
        "notifications@github.com", "noreply@github.com",
        "no-reply@slack.com", "no-reply@accounts.google.com",
        "no-reply@email.slackhq.com",
    ]
    # 客户相关的关键词（标题含这些才通知）
    keywords = ["需求", "咨询", "合作", "报价", "agent", "AI", "智能客服", "知识库", "agent"]
    
    for entry in entries:
        from_lower = entry["from"].lower()
        # 跳过系统通知
        if any(d in from_lower for d in skip_domains):
            continue
        # 跳过自己的邮件（客户不会从自己邮箱发）
        if EMAIL in from_lower:
            continue
        title = entry["title"]
        if not title:
            continue
        # 检查标题是否含客户关键词（优先匹配）
        if any(k in title.lower() for k in keywords):
            notify = {
                "from": entry["from"],
                "subject": entry["title"],
                "preview": entry["preview"],
                "received_at": datetime.now().isoformat(),
            }
            os.makedirs(os.path.dirname(NOTIFY_FILE), exist_ok=True)
            with open(NOTIFY_FILE, "w") as f:
                json.dump(notify, f, ensure_ascii=False)
            print("NEW_EMAIL:" + json.dumps(notify, ensure_ascii=False))
            save_last_id(entry["id"])
            return True
    
    # 如果没有任何匹配，保存最新邮件ID但不通知
    if entries:
        save_last_id(entries[0]["id"])
    print("NO_NEW_CLIENT_EMAIL")
    return False

if __name__ == "__main__":
    check_mail()
