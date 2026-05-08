"""
工作流型 Agent — 多步骤任务执行
"""
from agents.core.agent_base import BaseAgent

class WorkflowAgent(BaseAgent):
    """工作流 Agent"""
    
    async def run(self, input_data):
        steps = self.ctx.config.get("steps", [])
        results = []
        for step in steps:
            # 执行每一步
            results.append({"step": step, "status": "pending"})
        return {"results": results}
