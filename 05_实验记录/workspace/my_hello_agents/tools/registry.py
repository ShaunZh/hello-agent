
from typing import Callable, Dict, Any
from my_hello_agents.tools.base import Tool

class ToolRegistry:
    """工具注册表"""

    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        self._functions: Dict[str, Dict[str, Any]] = {}

    def register_tool(self, tool: Tool): 
        """注册Tool对象""" 
        if tool.name in self._tools: 
            print(f"⚠️ 警告：工具 '{tool.name}' 已存在，将被覆盖。")
        self._tools[tool.name] = tool
        print(f"✅ 工具 '{tool.name}' 已注册。")
    
    def register_function(self, name: str, description: str, func: Callable[[str], str]):
        """
        直接注册函数作为工具(简单方法)

           Args:
            name: 工具名称
            description: 工具描述
            func: 工具函数，接受字符串参数，返回字符串结果
        """
        if name in self._functions:
            print(f"⚠️ 警告：工具 {name} 已存在，将被覆盖。")
        
        self._functions[name] = {
            "description": description,
            "func": func,
        }

        print(f"✅ 工具 '{name}' 已注册。")
    
    def get_tools_description(self) -> str:
        """获取所有工具的的描述"""
        descriptions = []

        for tool in self._tools.values():
            descriptions.append(f"- {tool.name}: {tool.description}")

        for name, info in self._functions.items():
            descriptions.append(f"- {name}: {info['description']}")
        
        return "\n".join(descriptions) if descriptions else "暂无可用工具"

    def execute_tool(self, name: str, input_text: str) -> str:
        """
        执行工具
        """

        if name in self._tools:
            tool = self._tools[name]
            try:
                return tool.run({"input_text": input_text})
            except Exception as e:
                return f"错误：执行工具 '{name}' 时发生异常: {str(e)}"
        
        if name in self._functions:
            func = self._functions[name]["func"]
            try:
                return func(input_text)
            except Exception as e:
                return f"错误：执行工具 '{name}' 时发生异常: {str(e)}"




    
    



