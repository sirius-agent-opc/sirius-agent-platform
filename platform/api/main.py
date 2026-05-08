"""
FastAPI 服务入口
"""
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Sirius Agent Platform API")

class AgentRequest(BaseModel):
    agent_type: str
    input: dict

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/agents/run")
async def run_agent(req: AgentRequest):
    return {"status": "running", "agent": req.agent_type}
