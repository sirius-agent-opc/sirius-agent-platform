"""
Workflow Agent — 多步骤工作流 Agent
"""
import os, yaml
from openai import OpenAI

class WorkflowAgent:
    def __init__(self, config_path: str = None, api_key: str = None):
        self.config = self._load_config(config_path)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com/v1")
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url) if self.api_key else None

    def _load_config(self, path):
        if path and os.path.exists(path):
            with open(path) as f:
                return yaml.safe_load(f)
        return {"steps": [{"id": "default", "prompt": "处理：{input}"}]}

    def _call_llm(self, prompt: str, model: str = "deepseek-chat") -> str:
        if not self.client:
            return f"[模拟] {prompt[:50]}..."
        resp = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content

    def run(self, input_data: dict) -> dict:
        user_input = input_data.get("input", "")
        steps = input_data.get("steps", self.config.get("steps", []))
        model = input_data.get("model", self.config.get("model", {}).get("model", "deepseek-chat"))
        
        ctx = {"input": user_input}
        results = []
        
        for step in steps:
            prompt = step["prompt"].format(**ctx)
            output = self._call_llm(prompt, model)
            ctx[step["id"]] = {"output": output}
            results.append({"step": step["id"], "name": step.get("name", step["id"]), "output": output[:100]})
        
        return {"results": results, "final_output": results[-1]["output"] if results else ""}
