"""
Agent 基类 — 所有 Agent 的通用接口
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class AgentContext:
    """Agent 运行上下文"""
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.state: Dict[str, Any] = {}

class BaseAgent(ABC):
    """所有 Agent 的基类"""
    
    def __init__(self, name: str, config: Optional[Dict] = None):
        self.name = name
        self.ctx = AgentContext(config or {})
    
    @abstractmethod
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行 Agent 的核心逻辑"""
        pass
    
    def log(self, msg: str):
        print(f"[{self.name}] {msg}")
