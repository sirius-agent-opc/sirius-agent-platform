"""
Sirius Agent Platform API
"""
import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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
    """运行指定类型的 Agent"""
    if req.agent_type == "chat":
        return AgentRunResponse(
            status="success",
            output={
                "agent": "chat",
                "response": "Chat agent 响应 (Demo)",
                "data": req.input,
            },
        )
    elif req.agent_type == "rag":
        return AgentRunResponse(
            status="success",
            output={
                "agent": "rag",
                "query": req.input.get("query", ""),
                "answer": f"RAG 检索结果 (Demo): 基于知识库的答案",
                "sources": [],
            },
        )
    elif req.agent_type == "workflow":
        return AgentRunResponse(
            status="success",
            output={
                "agent": "workflow",
                "steps_completed": len(req.config.get("steps", [])),
                "results": [{"step": s, "status": "done"} for s in req.config.get("steps", [])],
            },
        )
    else:
        raise HTTPException(status_code=400, detail=f"未知 Agent 类型: {req.agent_type}")

@app.get("/agents")
def list_agents():
    """列出可用 Agent 模板"""
    return {
        "agents": [
            {"id": "chat", "name": "Chat Agent", "description": "通用对话 Agent"},
            {"id": "rag", "name": "RAG Agent", "description": "知识库问答 Agent"},
            {"id": "workflow", "name": "Workflow Agent", "description": "工作流自动化 Agent"},
        ],
        "llm_configured": bool(os.getenv("OPENAI_API_KEY")),
    }
