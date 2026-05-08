"""
RAG 型 Agent — 检索增强生成
"""
from agents.core.agent_base import BaseAgent

class RAGAgent(BaseAgent):
    """RAG Agent — 知识库问答"""
    
    async def run(self, input_data):
        query = input_data.get("query", "")
        knowledge_base = self.ctx.config.get("knowledge_base", [])
        # 检索 + 生成
        return {"query": query, "answer": "RAG response placeholder"}
