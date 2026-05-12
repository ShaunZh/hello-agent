"""
Ch01 智能旅行助手 - 实验版本（空白骨架）
用途：自己动手编写代码，理解 Agent 的 Thought-Action-Observation 循环

原始参考：00_Source/hello-agents/code/chapter1/FirstAgentTest.py
"""
import os
from dotenv import load_dotenv
load_dotenv()

# ============================================================
# 📋 系统指令 - 告诉 LLM 角色、工具、输出格式
# ============================================================
AGENT_SYSTEM_PROMPT = """
你是一个智能旅行助手。你的任务是分析用户的请求，并使用可用工具一步步地解决问题。

# 可用工具:
- `get_weather(city: str)`: 查询指定城市的实时天气。
- `get_attraction(city: str, weather: str)`: 根据城市和天气搜索推荐的旅游景点。

# 输出格式要求:
你的每次回复必须严格遵循以下格式，包含一对Thought和Action：

Thought: [你的思考过程和下一步计划]
Action: [你要执行的具体行动]

Action的格式必须是以下之一：
1. 调用工具：function_name(arg_name="arg_value")
2. 结束任务：Finish[最终答案]

# 重要提示:
- 每次只输出一对Thought-Action
- Action必须在同一行，不要换行
- 当收集到足够信息可以回答用户问题时，必须使用 Action: Finish[最终答案] 格式结束

请开始吧！
"""

# ============================================================
# 🛠️ 工具 1：天气查询
# 提示：使用 requests 库调用 wttr.in 免费 API
# API: https://wttr.in/{city}?format=j1
# 需要提取: current_condition[0] 中的天气描述和温度
# ============================================================
import requests

def get_weather(city: str) -> str:
    """查询指定城市的实时天气"""
    # TODO: 构建 API URL: 调用wttr.in 查询真实的天气信息
    url = f"https://wttr.in/{city}?format=j1"
    # TODO: 发起 GET 请求
    try:
        # 发起请求: requests.get是同步阻塞的。 它会等待服务器响应后才返回，期间当前线程被阻塞。如果需要非阻塞 HTTP 请求，可以用 aiohttp（异步）或把 requests 放到线程池里。
        response = requests.get(url)
        # 判断非 2xx 状态码并抛异常的简写。 它不是只判断 200，而是判断整个 2xx 范围（200-299 都算成功）。如果状态码是 4xx 或 5xx，它会抛出 requests.exceptions.HTTPError。
        response.raise_for_status()
        # 解析返回的JSON数据
        data = response.json()

        # 提取当前天气状况
        current_condition = data['current_condition'][0]
        weather_desc = current_condition['weatherDesc'][0]['value']
        temp_c = current_condition['temp_C']

        # 格式化成自然语言
        return f"{city}当前天气: {weather_desc}，气温: {temp_c}摄氏度"

    # 捕获网络请求异常，这是网络请求异常的基类
    except requests.exceptions.RequestException as e:
        # 处理网络错误
        return f"错误：查询天气时遇到网络问题 - {e}"
    # KeyError: 捕获字典（Python 的 map）取了不存在的键；IndexError: 数组列表的越界访问异常；
    # 如果是不确定会产生什么异常，可以直接使用异常的基类来代替：`except Exception as e: `
    except (KeyError, IndexError) as e:
        # 处理数据解析错误
        return f"错误：解析天气数据失败，可能是城市名称无效 - {e}"

# ============================================================
# 🛠️ 工具 2：景点推荐
# 提示：使用 tavily-python 库调用 Tavily 搜索 API: https://docs.tavily.com/welcome
# 需要先 pip install tavily-python
# 需要 TAVILY_API_KEY 环境变量
# ============================================================
import os
from tavily import TavilyClient

def get_attraction(city: str, weather: str) -> str:
    """根据城市和天气搜索推荐景点"""
    # 从环境变量获取 TAVILY_API_KEY
    api_key = os.environ.get('TAVILY_API_KEY')
    if not api_key:
        return "错误：未配置TAVILY_API_KEY环境变量"
    # 初始化 TavilyClient
    tavily = TavilyClient(api_key=api_key)

    # 构造搜索查询（包含城市和天气）
    query = f"'{city}' 在 '{weather}' 天气下最值得去的旅游景点推荐及理由"

    # 调用 tavily.search()，获取结果
    try:
        response = tavily.search(query=query, search_depth="basic", include_answer=True)

        # Tavily返回的结果已经非常干净，可以直接使用
        # response['answer'] 是一个基于所有搜索结果的总结性回答
        if response.get("answer"):
            return response["answer"]
        
        formatted_results = []
        for result in response.get("results", []):
            formatted_results.append(f"- {result['title']}: {result['content']}")
        if not formatted_results:
            return "抱歉，没有找到相关的旅游景点推荐。"
        return "根据搜索，为您找到以下信息：\n " + "\n".join(formatted_results)
    except Exception as e:
        return f"错误：执行Tavily搜索时出现问题 - {e}"

# ============================================================
# 🔗 工具注册表 - 把工具函数放进字典，方便主循环调用
# ============================================================
# 创建 available_tools 字典，映射工具名到函数
available_tools = {
    "get_weather": get_weather,
    "get_attraction": get_attraction,
}

# ============================================================
# 🧠 LLM 客户端 - 调用大语言模型
# 提示：使用 openai 库，兼容任何 OpenAI 格式的 API
# ============================================================
from openai import OpenAI

class OpenAICompatibleClient:
    """兼容 OpenAI 接口的 LLM 客户端"""
    def __init__(self, model: str, api_key: str, base_url: str):
        # 初始化 OpenAI 客户端
        self.model = model
        self.client = OpenAI(api_key = api_key, base_url = base_url)

    def generate(self, prompt: str, system_prompt: str) -> str:
        """调用 LLM 生成回应"""
        # 构建 messages（system + user）
        print("正在调用大语言模型...")
        try:
            messages = [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt}
            ]

            # 调用 chat.completions.create
            response = self.client.chat.completions.create(
                model = self.model,
                messages = messages,
                stream = False
            )
            answer = response.choices[0].message.content
            print("大语言模型响应成功。")
            return answer
        except Exception as e: 
            print(f"调用LLM API时发生错误: {e}")
            return "错误：调用语言模型服务时出错。"

# ============================================================
# 🔄 Agent 主循环 - Thought → Action → Observation
# 提示：这是 Agent 的核心！理解这个循环是本章最重要的事
# ============================================================
import re

def run_agent(user_prompt, max_loops: int = 5):
    """运行 Agent 主循环"""
    # TODO: 设置环境变量
    API_KEY = os.environ.get("DEEPSEEK_API_KEY")
    BASE_URL = os.environ.get("BASE_URL")
    MODEL_ID = os.environ.get("MODEL_ID")

    # 初始化 LLM 客户端
    llm = OpenAICompatibleClient(
        model=MODEL_ID, 
        api_key=API_KEY, 
        base_url=BASE_URL
    )

    # 初始化 prompt_history，放入用户请求
    # 打印用户输入
    prompt_history = [f"用户请求： {user_prompt}"]

    print(f"用户输入：{user_prompt}\n" + "="*40)

    for i in range(max_loops):
        print(f"---- 循环 {i + 1} ----\n")
        # Step 1: 构建 Prompt
        full_prompt = "\n".join(prompt_history)

        # Step 2: 调用 LLM 思考
        llm_output = llm.generate(full_prompt, system_prompt=AGENT_SYSTEM_PROMPT)

        #  用正则截断多余的 Thought-Action 对
        match = re.search(r'(Thought:.*?Action:.*?)(?=\n\s*(?:Thought:|Action:|Observation:)|\Z)',
        llm_output, re.DOTALL)

        if match:
            truncated = match.group(1).strip()
            if truncated != llm_output.strip():
                llm_output = truncated
                print("已截断多余的 Thought-Action 对")
        print(f"模型输出: \n{llm_output}\n")
        prompt_history.append(llm_output)

        # Step 3: 解析 Action
        action_match = re.search(r"Action: (.*)", llm_output, re.DOTALL)
        if not action_match:
            observation = "错误: 未能解析到 Action 字段。请确保你的回复严格遵循'Thought: ... Action: ...' 的格式。"
            observation_str = f"Observation: {observation}"
            print(f"{observation_str}\n" + "="*40)
            prompt_history.append(observation_str)
            continue
        action_str = action_match.group(1).strip()

        if action_str.startswith("Finish"):
            final_answer = re.match(r"Finish\[(.*)\]", action_str).group(1)
            print(f"任务完成，最终答案: {final_answer}")
            break
        tool_name = re.search(r"(\w+)\(", action_str).group(1)
        args_str = re.search(r"\((.*)\)", action_str).group(1)
        kwargs = dict(re.findall(r'(\w+)="([^"]*)"', args_str))

        if tool_name in available_tools:
            observation = available_tools[tool_name](**kwargs)
        else:
            observation = f"错误:未定义的工具 '{tool_name}'"
        
        # 记录观察结果
        observation_str = f"Observation: {observation}"
        print(f"{observation_str}\n" + "="*40)
        prompt_history.append(observation_str)
    # print("⚠️ 达到最大循环次数，任务未自动结束。")
    # return None

# ============================================================
# 🚀 启动入口
# ============================================================
from prompt_toolkit import prompt
if __name__ == "__main__":
    print("🌍 Ch01 智能旅行助手")
    # user_prompt = "你好，请帮我查询一下今天北京的天气，然后根据天气推荐一个合适的旅游景点。"
    user_prompt = prompt("请输入你的旅行需求：")

    run_agent(user_prompt=user_prompt)
