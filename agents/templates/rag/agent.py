"""
RAG Agent — 检索增强生成型 Agent

用法:
    agent = RAGAgent(config_path="config.yaml")
    result = agent.run({"query": "公司的产品有哪些？"})
"""
import os, yaml, json
from pathlib import Path
from openai import OpenAI

class RAGAgent:
    def __init__(self, config_path: str = None, api_key: str = None):
        self.config = self._load_config(config_path)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com/v1")
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url) if self.api_key else None
        self._knowledge = []

    def _load_config(self, path):
        if path and os.path.exists(path):
            with open(path) as f:
                return yaml.safe_load(f)
        return {"model": {"model": "deepseek-chat", "temperature": 0.3}, "retrieval": {"top_k": 3}}

    def load_knowledge(self, texts: list[str]):
        """加载知识库"""
        self._knowledge = texts

    def load_from_dir(self, dir_path: str):
        """从目录加载文档"""
        p = Path(dir_path)
        texts = []
        for f in p.glob("*.txt") or p.glob("*.md"):
            texts.append(f.read_text(encoding="utf-8"))
        self._knowledge = texts

    def _retrieve(self, query: str, top_k: int = 3) -> list[str]:
        """简单关键词检索（生产环境可替换为向量检索）"""
        if not self._knowledge:
            return []
        query_lower = query.lower()
        scored = []
        for i, doc in enumerate(self._knowledge):
            score = sum(1 for word in query_lower.split() if word in doc.lower())
            scored.append((score, i, doc[:200]))
        scored.sort(reverse=True)
        return [doc for _, _, doc in scored[:top_k]]

    def run(self, input_data: dict) -> dict:
        query = input_data.get("query", "")
        
        if not self.client:
            return {"answer": "[配置 OPENAI_API_KEY 以启用]", "sources": []}

        # 检索
        top_k = input_data.get("top_k", self.config["retrieval"]["top_k"])
        contexts = self._retrieve(query, top_k)
        
        # 生成
        context = "\n\n".join(contexts) if contexts else "未找到相关信息。"
        system = f"基于以下内容回答问题：\n\n{context}\n\n如果无法从内容中找到答案，请如实告知。"
        
        resp = self.client.chat.completions.create(
            model=input_data.get("model", self.config["model"]["model"]),
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": query},
            ],
            temperature=self.config["model"]["temperature"],
        )
        return {"answer": resp.choices[0].message.content, "sources": contexts}
