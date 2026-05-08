# Chat Agent 模板

通用对话型 Agent，支持系统提示词、模型选择、温度控制。

## 快速开始

```python
from agents.templates.chat.agent import ChatAgent

agent = ChatAgent()
reply = agent("你好")
print(reply)
```

## 配置

编辑 `config.yaml` 修改模型、提示词等参数。
