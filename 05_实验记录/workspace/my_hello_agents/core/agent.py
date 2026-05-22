"""
Agent基类
整个框架的顶层抽象。它定义了一个智能体应该具备的通用行为和属性，但并不关心具体的实现方式
"""
from abc import ABC, abstractmethod
from typing import Optional, Any
from hello_agents import HelloAgentsLLM
from my_hello_agents.core.message import Message
from my_hello_agents.core.config import Config

class Agent(ABC):
    def __init__(
        self,
        name: str,
        llm: HelloAgentsLLM,
        system_prompt: Optional[str] = None,
        config: Optional[Config] = None
    ):
        self.name = name
        self.llm = llm
        self.system_prompt = system_prompt
        self.config = config or Config()
        self._history: list[Message] = []

    @abstractmethod
    def run(self, input_text: str, **kwargs) -> str:
        """运行Agent"""
        pass

    def add_message(self, message: Message):
        self._history.append(message)
    
    def clear_history(self):
        self._history.clear()

    def get_history(self) -> list[Message]:
        return self._history
    
    def __str__(self) -> str:
        return f"Agent(name={self.name}, provider={self.llm.provider})"