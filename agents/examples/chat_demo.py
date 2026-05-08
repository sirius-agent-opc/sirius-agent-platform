"""Chat Agent 使用示例"""
import sys; sys.path.insert(0, ".")
from agents.templates.chat.agent import ChatAgent

agent = ChatAgent()
resp = agent.run({"messages": [{"role": "user", "content": "给我推荐三个南京适合一人工作的咖啡馆"}]})
print(f"🤖 {resp['reply']}")
