"""
Chat Agent — 通用对话型 Agent

用法:
    from agents.templates.chat.agent import ChatAgent
    agent = ChatAgent(config_path="config.yaml")
    result = agent.run({"messages": [{"role": "user", "content": "你好"}]})
"""
import os, yaml
from openai import OpenAI

class ChatAgent:
    def __init__(self, config_path: str = None, api_key: str = None):
        self.config = self._load_config(config_path)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com/v1")
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url) if self.api_key else None

    def _load_config(self, path):
        if path and os.path.exists(path):
            with open(path) as f:
                return yaml.safe_load(f)
        return {
            "model": {"provider": "openai", "model": "deepseek-chat", "temperature": 0.7},
            "system_prompt": "你是一个有用的 AI 助手。",
        }

    def run(self, input_data: dict) -> dict:
        messages = input_data.get("messages", [])
        system = input_data.get("system_prompt", self.config.get("system_prompt", ""))
        
        if not self.client:
            return {"reply": "[配置 OPENAI_API_KEY 环境变量以启用]", "model": "mock"}
        
        msgs = [{"role": "system", "content": system}] + messages
        model = input_data.get("model", self.config["model"]["model"])
        temp = input_data.get("temperature", self.config["model"]["temperature"])
        
        resp = self.client.chat.completions.create(
            model=model, messages=msgs, temperature=temp,
        )
        return {"reply": resp.choices[0].message.content, "model": model}

    def __call__(self, message: str) -> str:
        return self.run({"messages": [{"role": "user", "content": message}]})["reply"]
