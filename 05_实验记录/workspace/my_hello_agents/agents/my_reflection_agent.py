# my_reflection_agent.py
DEFAULT_PROMPTS = {
    "initial": """
        请根据以下要求完成任务：

        任务: {task}

        请提供一个完整、准确的回答。
    """,
    "reflect": """
        请仔细审查以下回答，并找出可能的问题或改进空间: 

        # 原始任务:
        {task}

        # 当前回答:
        {content}

        请分析这个回答的质量，指出不足之处，并提出具体的改进建议。如果回答已经很好，请回答"无需改进"。
    """,
    "refine": """
    请根据反馈意见改进你的回答:

    # 原始任务
    {task}

    # 上一轮回答:
    {last_attempt}

    # 反馈意见:
    {feedback}

    请提供一个改进后的回答。
    """
}

from mimetypes import init
from typing import Optional, Dict
from hello_agents import ReflectionAgent, HelloAgentsLLM
from my_hello_agents.core.config import Config
from my_hello_agents.core.message import Message
from my_hello_agents.core.memory import Memory

class MyReflectionAgent(ReflectionAgent):
    def __init__(
        self, 
        name: str, 
        llm: HelloAgentsLLM, 
        system_prompt: Optional[str] = None, 
        config: Optional[Config] = None, 
        max_iterations: int = 3, 
        custom_prompts: Optional[Dict[str, str]] = None
    ):
        super().__init__(name, llm, system_prompt, config, max_iterations, custom_prompts)
        print(f"✅ 初始化完，最大步数：{max_iterations} 步")
        self.memory = Memory()

    def run(self, input_text: str, **kwargs) -> str:
        print(f"\n--- 开始处理任务 ---\n任务：{input_text}")

        # --- 1. 初始执行 ---
        print("\n--- 正在进行初始尝试 ---")
        initial_prompt = DEFAULT_PROMPTS['initial'].format(task=input_text)
        initial_result = self._get_llm_response(initial_prompt, **kwargs)
        self.memory.add_record("execution", initial_result)

        for i in range(self.max_iterations):
            print(f"\n--- 第 {i+1}/{self.max_iterations} 轮迭代 ---")

            # a. 反思
            print("\n-> 正在进行反思...")
            # --- 2. reflect ---
            last_execution_result = self.memory.get_last_execution()
            reflect_prompt = DEFAULT_PROMPTS["reflect"].format(
                task=input_text,
                content=last_execution_result
            )
            feedback = self._get_llm_response(reflect_prompt)
            self.memory.add_record("reflection", feedback)

            if "无需改进" in feedback:
                print("\n✅ 反思认为结果已无需改进，任务完成。")
                break

            # --- 3. refine ---
            print("\n-> 正在进行优化...")
            refine_prompt = DEFAULT_PROMPTS["refine"].format(
                task={input_text},
                last_attempt=last_execution_result,
                feedback=feedback
            )
            refined_result = self._get_llm_response(refine_prompt)
            self.memory.add_record("execution", refined_result)

        final_result = self.memory.get_last_execution()
        print(f"\n--- 任务完成 ---\n最终结果:\n{final_result}")

    def _get_llm_response(self, prompt: str, **kwargs):
        messages = [{"role": "user", "content": prompt}]
        return self.llm.invoke(messages, **kwargs)

         
        
