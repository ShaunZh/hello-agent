# my_llm.py
import os
from typing import Optional
from openai import OpenAI
from hello_agents import HelloAgentsLLM

class MyLLM(HelloAgentsLLM):
    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        provider: Optional[str] = "auto",
        **kwargs
    ):
        # 检查provider是否为我们想处理的'modulescope'
        if provider == "modulescope":
            print("正在使用自定义的 Modulescope Provider")
            self.provider = "modulescope" 

            # 解析 ModuleScope 的凭证
            self.api_key = api_key or os.getenv("MODULESCOPE_API_KEY")
            self.base_url = base_url or "https://api-inference.modelscope.cn/v1/"

            # 验证凭证是否存在
            if not api_key:
                raise ValueError("ModelScope API key not found. Please set MODELSCOPE_API_KEY environment variable.")

            # 设置默认模型和其他参数
            self.model = model or os.getenv("LLM_MODEL_ID") or "deepseek-v4-flash"
            self.temperature = kwargs.get('temperature', 0.7)
            self.max_tokens = kwargs.get('max_tokens')
            self.timeout = kwargs.get('timeout', 60)

            # 使用获取的参数创建OpeanAI客户端实例
            self._client = OpenAI(
                api_key=self.api_key, 
                base_url=self.base_url,
                timeout=self.timeout
            )
        else:
            # 如果不是 ModuleScope，则完全使用父类的原始逻辑处理
            super().__init__(
                api_key=self.api_key,
                model=self.model,
                base_url=self.base_url,
                provider=provider,
                **kwargs
            )

