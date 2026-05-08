# RAG Agent 模板

知识库问答 Agent，支持文档检索 + LLM 生成。

## 快速开始

```python
from agents.templates.rag.agent import RAGAgent

agent = RAGAgent()
agent.load_knowledge(["公司成立于2024年，主营AI Agent开发。"])
result = agent.run({"query": "公司做什么的？"})
print(result["answer"])
```

## 配置

编辑 `config.yaml` 修改检索参数和模型。
