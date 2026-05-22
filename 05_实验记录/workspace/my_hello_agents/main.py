from dotenv import load_dotenv
from my_hello_agents.core.my_llm import MyLLM

# 加载环境变量
load_dotenv()

# 实例化我们重写的客户端，并指定provider
llm = MyLLM(provider = "modulescope")

# 准备消息
messages = [{"role": "user", "content": "你好，请介绍一下你自己。"}]

# 发起调用
response_stream = llm.think(messages=messages)

# 打印响应
print("ModuelScope Responses: ")
for chunk in response_stream:
    pass