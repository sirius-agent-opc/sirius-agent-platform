"""
示例: 最简单的 OpenAI Agent

用法:
    OPENAI_API_KEY=sk-xxx python agents/examples/hello_agent.py
"""
import os
from openai import OpenAI

def run(query: str) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": query}]
    )
    return resp.choices[0].message.content

if __name__ == "__main__":
    print(run("Hello, what can you do?"))
