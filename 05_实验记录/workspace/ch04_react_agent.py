"""
Ch04 ReAct Agent - 空白骨架版
用途：自己动手编写 ReAct Agent，理解 "思考-行动-观察" 循环

原始参考：00_Source/hello-agents/code/chapter4/ReAct.py
相关组件：llm_client.py（LLM调用封装）, tools.py（ToolExecutor）

依赖：pip install openai python-dotenv google-search-results
"""
import os
from datetime import date
import re
from textwrap import indent
from dotenv import load_dotenv
from typing import List, Dict, Any
from llm_client import HelloAgentsLLM
load_dotenv()

# ============================================================
# 🛠️ 工具 1：网页搜索（SerpApi）
# 提示：使用 serpapi 库调用 Google 搜索
# 需要 SERPAPI_API_KEY 环境变量
# 优先返回 answer_box / knowledge_graph / organic_results
# ============================================================
from serpapi import SerpApiClient

def search(query: str) -> str:
    """网页搜索引擎工具"""
    print(f"🔍 正在执行 [SerpApi] 网页搜索: {query}")
    # 获取 SERPAPI_API_KEY
    try:
        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            return "错误：SERPAPI_API_KEY 未在 .env 文件中配置。"

        # 构建搜索参数
        params = {
            "engine": "google",
            "q": query,
            "api_key": api_key,
            "gl": "cn",
            "hl": "zh-cn",
            "num": 5
        }
        # 调用 SerpApiClient，获取结果
        client = SerpApiClient(params)
        results = client.get_dict()

        # 智能解析：优先 answer_box_list -> answer_box → knowledge_graph → organic_results
        if "answer_box_list" in results:
            return "\n".join(results["answer_box_list"])
        if "answer_box" in results and "answer" in results["answer_box"]:
            return results["answer_box"]["answer"]
        if "knowledge_graph" in results and "description" in results["knowledge_graph"]:
            return results["knowledge_graph"]["description"]
        if "organic_results" in results and results["organic_results"]:
            # 如果没有直接答案，则返回前三个有机结果的摘要
            snippets = [
                f"[{i+1}] {res.get('title', '')}\n{res.get('snippet', '')}" 
                for i, res in enumerate(results["organic_results"][:5])
            ]
            return "\n\n".join(snippets)
        return f"对不起，没有找到关于 '{query}' 的信息。"
    except Exception as e:
        return f"搜索时发生错误：{e}"

# ============================================================
# 🔗 工具执行器（ToolExecutor）
# 管理工具注册、查找和执行
# ============================================================
class ToolExecutor:
    """工具执行器"""
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}  # name → {description, func}

    def registerTool(self, name: str, description: str, func: callable):
        """
        向工具箱中注册一个新工具。
        """
        if name in self.tools:
            print(f"警告：工具'{name}' 已存在，将被覆盖。")
        self.tools[name] = {"description": description, "func": func}
        print(f"工具 '{name}' 已注册。")

    def getTool(self, name: str):
        """根据名称获取工具函数"""
        # 从字典中查找并返回
        return self.tools.get(name, {}).get("func")

    def getAvailableTools(self) -> str:
        """返回所有工具的格式化描述（用于插入 Prompt）"""
        return "\n".join([
            f"- {name}: {info['description']}"
            for name, info in self.tools.items()
        ])

# ============================================================
# 📋 ReAct 提示词模板，定义了智能体与LLM之间交互的规范
# - 角色定义： 定义 LLM 的角色
# - 工具清单(tools): 告诉LLM，它有哪些可用的“手脚”
# - 格式规约（`Thought`/`Action`）：这是最重要的部分，它强制LLM的输出具有结构性，使我们能够使用代码精确解析其意图
# - 动态上下文（`{question}`/`{history}`)：将用户的原始问题和不断累积的交互历史注入，让LLM基于完整的上下文进行决策。
# ============================================================
REACT_PROMPT_TEMPLATE = """
你是一个有能力调用外部工具的智能助手。

当前日期：{current_date}

可用工具如下：
{tools}

请严格按照以下格式进行回应。每次回应只包含一组 Thought 和 Action，不要输出多轮。

Thought: 你的思考过程，用于分析问题、拆解任务和规划下一步行动。
Action: 你决定采取的行动，必须是以下格式之一:
- `{{tool_name}}[{{tool_input}}]`: 调用一个可用工具
- `Finish[最终答案]`: 当你认为已经获得最终答案时。

重要约束：
1. 每次只输出一组 Thought + Action，不要自己编造 Observation。
2. Observation 会由系统在工具执行后提供，你不需要自己生成。
3. 当你收集到足够的信息时，使用 Finish[最终答案] 输出最终答案。

现在，请开始解决以下问题:
Question: {question}
History: {history}
"""

# ============================================================
# 🔄 ReAct Agent - 核心循环
# 这是本章最重要的代码！
# ============================================================
class ReActAgent:
    """ReAct 智能体：思考-行动-观察循环"""
    def __init__(self, llm_client: HelloAgentsLLM, tool_executor: ToolExecutor, max_steps=5):
        self.llm_client = llm_client
        self.tool_executor = tool_executor
        self.max_steps = max_steps
        self.history = []

    def run(self, question: str):
        """运行 ReAct 主循环"""
        self.history = []
        current_step = 0

        while current_step < self.max_steps:
            current_step += 1
            print(f"\n--- 第 {current_step} 步 ---")

            # Step 1: 构建 Prompt
            # 获取工具描述、历史字符串
            tools_desc = self.tool_executor.getAvailableTools()
            history_str = '\n'.join(self.history)
            # 用 REACT_PROMPT_TEMPLATE.format() 格式化
            prompt = REACT_PROMPT_TEMPLATE.format(
                current_date=date.today().isoformat(),
                tools=tools_desc,
                question=question,
                history=history_str
            )

            # Step 2: 调用 LLM 思考
            # 构建 messages，调用 llm_client.think()
            messages = [{"role": "user", "content": prompt}]
            response_text = self.llm_client.think(messages=messages)
            # 如果返回 None，中断循环
            if not response_text:
                print("错误：LLM未能返回有效相应")
                break

            #  解析 LLM 输出（提取 Thought 和 Action）
            thought, action = self._parse_output(response_text)
            if thought:
                print(f"思考：{thought}")
            
            if not action:
                print("警告：未能解析出有效的Action，流程终止。")
                break

            # Step 4: 检查 Action 是否为 Finish
            # 如果 Action 以 "Finish" 开头，提取答案并 return
            if action.startswith("Finish"):
                final_answer = re.match(r"Finish\[(.*)\]", action).group(1)
                print(f"🎉 最终答案: {final_answer}")
                return final_answer

            # Step 5: 解析工具名称和输入
            # 用正则匹配 tool_name[input] 格式
            tool_name, tool_input = self._parse_action(action)
            if not tool_name or not tool_input:
                # ... 处理无效Action格式
                continue

            # 从 ToolExecutor 获取工具函数并执行
            print(f"🎬 行动: {tool_name}[{tool_input}]")
            tool_function = self.tool_executor.getTool(tool_name)
            if not tool_function:
                observation = f"错误：未找到名为 '{tool_name}' 的工具。"
            else:
                # 调用工具 
                observation = tool_function(tool_input)
            # Step 6: 记录观察，进入下一轮
            print(f"👀 观察: {observation}")
            # 将 Action 和 Observation 追加到 self.history
            self.history.append(f"Action: {action}")
            self.history.append(f"Observation: {observation}")

        print("已达到最大步数，流程终止。")
        return None

    def _parse_output(self, text: str):
        """从 LLM 响应中提取 Thought 和 Action"""
        # 正则拆解：r"Thought:\s*(.*?)(?=\nAction:|$)"
        #   Thought:    字面文本，匹配 "Thought:"
        #   \s*         0个或多个空白字符
        #   (.*?)       捕获组：非贪婪匹配任意字符（尽可能少匹配）
        #   (?=         先行断言：判断右边是什么，不消费字符
        #     \nAction:   右边是 "\nAction:"
        #     |           或者
        #     $           字符串末尾
        #   )           断言结束
        thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|$)", text, re.DOTALL)

        # 正则拆解：r"Action:\s*(.*?)$"
        #   Action:     字面文本，匹配 "Action:"
        #   \s*         0个或多个空白字符
        #   (.*?)       捕获组：非贪婪匹配任意字符
        #   $           字符串末尾位置
        action_match = re.search(r"Action:\s*(.*?)$", text, re.DOTALL)
        thought = thought_match.group(1).strip() if thought_match else None
        action = action_match.group(1).strip() if action_match else None

        return thought, action

    def _parse_action(self, action_text: str):
        """从 Action 文本中提取工具名和输入（格式：tool_name[input]）"""
        # 正则拆解：r"(\w+)\[(.*)\]"
        #   (\w+)       捕获组1：匹配工具名（字母、数字、下划线，至少1个字符）
        #   \[          字面文本 "["（需要转义）
        #   (.*)        捕获组2：贪婪匹配任意字符（工具输入内容）
        #   \]          字面文本 "]"（需要转义）
        match = re.match(r"(\w+)\[(.*)\]", action_text, re.DOTALL)
        if match:
            return match.group(1), match.group(2)
        return None, None

def testLlmClient(llmClient: HelloAgentsLLM):
    try:

        exampleMessages = [
            {"role": "system", "content": "You are a helpful assistan that writes Python code."},
            {"role": "user", "content": "写一个快速排序算法"}
        ]
        print("--- 调用LLM ---")
        responseText = llmClient.think(exampleMessages)
        if responseText:
            print("\n\n----- 完整模型响应 ------")
            print(responseText)
    except ValueError as e:
        print(e)

def testToolExcutor():
    toolExecutor = ToolExecutor()

    toolExecutor.registerTool("Search", "一个网页搜索引擎。当你需要回答关于时事、事实以及在你的知识库中找不到的信息时，应使用此工具。", search)

    print('\n-----打印可用的工具------\n')
    print(toolExecutor.getAvailableTools())

    print("\n--- 执行 Action: Search['英伟达最新的GPU型号是什么'] ---")
    tool_name = "Search"
    tool_input = "英伟达最新的GPU型号是什么"
    tool_function = toolExecutor.getTool(tool_name)
    
    if tool_function:
        observation = tool_function(tool_input)
        print("---- 观察（Observation）----")
        print(observation)
    else:
        print(f"错误：未找到名为 '{tool_name}' 的工具。")

    
# ============================================================
# 🚀 启动入口
# ============================================================
if __name__ == "__main__":
    print("🤖 Ch04 ReAct Agent")
    
    # 初始化 LLM 客户端
    llmClient = HelloAgentsLLM()
    # testLlmClient(llmClient=llmClient)
    # testToolExcutor()
    
    # 初始化 ToolExecutor，注册 Search 工具
    toolExecutor = ToolExecutor()
    toolExecutor.registerTool("Search", "一个网页搜索引擎。当你需要回答关于时事、事实以及在你的知识库中找不到的信息时，应使用此工具。", search)

    # 创建 ReActAgent 实例
    agent = ReActAgent(llm_client=llmClient, tool_executor=toolExecutor, max_steps=5)
    # 运行 agent.run("华为最新的手机是哪一款？它的主要卖点是什么？")
    agent.run("华为最新的手机是哪一款？它的主要卖点是什么？")
