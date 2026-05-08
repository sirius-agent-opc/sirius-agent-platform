"""Workflow Agent 使用示例"""
import sys; sys.path.insert(0, ".")
from agents.templates.workflow.agent import WorkflowAgent

agent = WorkflowAgent()
resp = agent.run({"input": "南京一人公司注册流程"})
print(f"🔄 工作流完成，共 {len(resp['results'])} 步")
