"""
聊天型 Agent — 标准对话交互
"""
from agents.core.agent_base import BaseAgent

class ChatAgent(BaseAgent):
    """通用聊天 Agent"""
    
    async def run(self, input_data):
        messages = input_data.get("messages", [])
        system_prompt = self.ctx.config.get("system_prompt", "You are a helpful assistant.")
        # 集成 LLM 调用
        return {"response": "Agent response placeholder", "messages": messages}
