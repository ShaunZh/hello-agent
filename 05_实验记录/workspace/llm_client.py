
# ============================================================
# 🧠 LLM 客户端（可复用 Ch01 的实现，或参考 llm_client.py）
# ============================================================
import os
from openai import OpenAI
from typing import List, Dict

class HelloAgentsLLM:
    """LLM 客户端，支持流式输出"""
    def __init__(self, model=None, apiKey=None, baseUrl=None, timeout=None):
        # 从参数或环境变量初始化
        self.model = model or os.getenv("MODEL_ID")
        apiKey = apiKey or os.getenv("DEEPSEEK_API_KEY")
        baseUrl = baseUrl or os.getenv("BASE_URL")
        timeout = timeout or int(os.getenv("LLM_TIMEOUT", 60))

        if not all([self.model, apiKey, baseUrl]):
            raise ValueError("模型ID、API秘钥和服务地址必须被提供在.env文件中定义。")
        
        self.client = OpenAI(api_key=apiKey, base_url=baseUrl, timeout=timeout)

    def think(self, messages: List[Dict[str, str]], temperature: float=0):
        """调用 LLM，返回响应文本"""
        try:
            # 调用 chat.completions.create
            print(f"🧠 正在调用 {self.model} 模型...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=True
            )
            # print(f"--------大语言模型响应成功原始输出---------\n")
            # 处理流式响应（stream=True），收集内容后返回
            print(f"✅ 大语言模型响应成功:")
            collected_content = []
            for chunk in response:
                if not chunk.choices:
                    continue
                content = chunk.choices[0].delta.content or ""
                print(content, end = "", flush=True)
                collected_content.append(content)
            # 在流式输出结束后换行
            print()
            return "".join(collected_content)
        except Exception as e:
            print(f"❌ 调用LLM API时发生错误: {e}")
            return None