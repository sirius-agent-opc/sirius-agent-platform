"""
Sirius Agent Platform API
"""
import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from fastapi.responses import HTMLResponse, FileResponse

app = FastAPI(title="Sirius Agent Platform API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Models ────────────────────────────────────────────

class ChatRequest(BaseModel):
    messages: list[dict]
    system_prompt: Optional[str] = "You are a helpful assistant."
    model: Optional[str] = "gpt-4o-mini"

class ChatResponse(BaseModel):
    reply: str
    model: str

class AgentRunRequest(BaseModel):
    agent_type: str  # "chat" | "rag" | "workflow"
    input: dict
    config: Optional[dict] = {}

class ContactRequest(BaseModel):
    name: str
    contact: str
    desc: str
    budget: str = "未定"
    time: Optional[str] = None

class AgentRunResponse(BaseModel):
    status: str
    output: dict

# ─── LLM Client ────────────────────────────────────────

def get_llm():
    """Get LLM client (OpenAI / DeepSeek compatible)"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    from openai import OpenAI
    return OpenAI(api_key=api_key, base_url=base_url)

# ─── Agent 模板加载 ────────────────────────────────

def load_template(template_id: str):
    """动态加载 Agent 模板"""
    import importlib, json
    templates_path = os.path.join(os.path.dirname(__file__), "..", "..", "agents", "templates.json")
    if os.path.exists(templates_path):
        with open(templates_path) as f:
            index = json.load(f)
        for t in index.get("templates", []):
            if t["id"] == template_id:
                module_path = f"agents.{t['path'].replace('/', '.')}.{t['entry'].replace('.py', '')}"
                mod = importlib.import_module(module_path)
                cls = getattr(mod, t["class"])
                config_path = os.path.join(os.path.dirname(__file__), "..", "..", "agents", t["path"], t["config"])
                return cls(config_path)
    return None

# ─── 客户咨询 ──────────────────────────────────────

@app.post("/contact")
def contact(req: ContactRequest):
    """客户需求提交"""
    # 记录到日志
    import json, datetime
    entry = req.model_dump()
    entry["received_at"] = datetime.datetime.now().isoformat()
    
    # 写入文件
    os.makedirs("data/contacts", exist_ok=True)
    with open(f"data/contacts/{datetime.date.today()}.jsonl", "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    # 标记新需求（供 OpenClaw 检测）
    os.makedirs("data/notifications", exist_ok=True)
    with open(f"data/notifications/new_contact.json", "w") as f:
        f.write(json.dumps(entry, ensure_ascii=False))
    
    print(f"📩 新客户需求: {req.name} / {req.contact}")
    return {"status": "received", "message": "需求已收到，24小时内回复"}

# ─── 手动查邮件 ────────────────────────────────────

import subprocess

@app.get("/check-email")
def check_email():
    """手动触发邮件检查"""
    script = os.path.join(os.path.dirname(__file__), "..", "..", "ops", "email-monitor.py")
    if os.path.exists(script):
        try:
            result = subprocess.run(
                ["python3", script],
                capture_output=True, text=True, timeout=20
            )
            return {"status": "done", "output": result.stdout.strip() or result.stderr.strip()}
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "message": "邮件检查超时，稍后重试"}
    return {"status": "error", "message": "脚本不存在"}

# ─── 在线体验页面 ───────────────────────────────────

@app.get("/demo", response_class=HTMLResponse)
def demo_page():
    """Agent 在线体验页面"""
    html_path = os.path.join(os.path.dirname(__file__), "..", "web", "chat.html")
    if os.path.exists(html_path):
        with open(html_path, encoding="utf-8") as f:
            return f.read()
    return HTMLResponse("<h1>Demo page not found</h1>", status_code=404)

# ─── Endpoints ─────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "api_version": "0.1.0", "llm_configured": bool(os.getenv("OPENAI_API_KEY"))}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """通用对话接口"""
    client = get_llm()
    
    if client:
        messages = [{"role": "system", "content": req.system_prompt}]
        messages.extend(req.messages)
        resp = client.chat.completions.create(
            model=req.model,
            messages=messages,
            temperature=0.7,
        )
        return ChatResponse(reply=resp.choices[0].message.content, model=req.model)
    
    # Mock 响应（演示用）
    return ChatResponse(
        reply=f"[演示模式] 收到 {len(req.messages)} 条消息。配置 OPENAI_API_KEY 环境变量即可接入真实 LLM。",
        model="mock",
    )

@app.post("/agents/run", response_model=AgentRunResponse)
def run_agent(req: AgentRunRequest):
    """运行指定类型的 Agent（使用模板）"""
    agent = load_template(req.agent_type)
    if not agent:
        raise HTTPException(status_code=400, detail=f"未知 Agent 类型: {req.agent_type}")
    
    try:
        result = agent.run(req.input)
        return AgentRunResponse(status="success", output=result)
    except Exception as e:
        return AgentRunResponse(status="error", output={"error": str(e)})

@app.get("/agents")
def list_agents():
    """列出可用 Agent 模板"""
    import json
    templates_path = os.path.join(os.path.dirname(__file__), "..", "..", "agents", "templates.json")
    if os.path.exists(templates_path):
        with open(templates_path) as f:
            index = json.load(f)
        return {"templates": index["templates"], "llm_configured": bool(os.getenv("OPENAI_API_KEY"))}
    return {"templates": [], "llm_configured": bool(os.getenv("OPENAI_API_KEY"))}
