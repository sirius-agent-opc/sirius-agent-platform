# Workflow Agent 模板

多步骤工作流 Agent，支持链式处理。

## 快速开始

```python
from agents.templates.workflow.agent import WorkflowAgent

agent = WorkflowAgent()
result = agent.run({"input": "处理这份数据..."})
print(result["final_output"])
```

## 配置

编辑 `config.yaml` 定义工作流步骤。
