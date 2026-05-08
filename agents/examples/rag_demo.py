"""RAG Agent 使用示例"""
import sys; sys.path.insert(0, ".")
from agents.templates.rag.agent import RAGAgent

agent = RAGAgent()
agent.load_knowledge([
    "Sirius Agent Solutions 成立于2026年，专注 AI Agent 定制开发。",
    "提供服务：智能客服 Agent、RAG 知识库问答、工作流自动化。",
    "联系邮箱：sirius.nrly@gmail.com",
])
resp = agent.run({"query": "公司提供哪些服务？"})
print(f"📚 {resp['answer']}")
