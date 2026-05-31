# my_plan_and_solve_agent.py

# 默认规划器提示词模板
DEFAULT_PLANNER_PROMPT = """
你是一个顶级的AI规划专家。你的任务是将用户提出的复杂问题分解成一个由多个简单步骤组成的行动计划。
请确保计划中的每个步骤都是一个独立的、可执行的子任务，并且严格按照逻辑顺序排列。
你的输出必须是一个Python列表，其中每个元素都是一个描述子任务的字符串。

问题: {question}

请严格按照以下格式输出你的计划:
```python
["步骤1", "步骤2", "步骤3", ...]
```
"""

# 默认执行器提示词模板
DEFAULT_EXECUTOR_PROMPT = """
你是一位顶级的AI执行专家。你的任务是严格按照给定的计划，一步步地解决问题。
你将收到原始问题、完整的计划、以及到目前为止已经完成的步骤和结果。
请你专注于解决"当前步骤"，并仅输出该步骤的最终答案，不要输出任何额外的解释或对话。

# 原始问题:
{question}

# 完整计划:
{plan}

# 历史步骤与结果:
{history}

# 当前步骤:
{current_step}

请仅输出针对"当前步骤"的回答:
"""

import ast
from hello_agents import HelloAgentsLLM, PlanAndSolveAgent

from typing import Optional, Dict, List
from my_hello_agents.core.config import Config
from my_hello_agents.core.memory import Memory
from my_hello_agents.core.message import Message


class Planner:
    def __init__(self, llm_clinet: HelloAgentsLLM, prompt_template: Optional[str] = None):
        self.llm_client = llm_clinet
        self.prompt_template = prompt_template if prompt_template else DEFAULT_PLANNER_PROMPT
    
    def plan(self, question: str, **kwargs) -> List[str]:
        """
        生成执行计划

        Args:
            questions: 要解决的问题
            **kwargs: 传递给llm的参数
        
        Returns:
            步骤列表
        """
        prompt = self.prompt_template.format(question=question)
        messages = [{"role": "user", "content": prompt}]

        print("--- 正在生成计划 ---")
        response_text = self.llm_client.invoke(messages=messages, **kwargs) or ""
        print(f"\n计划已生成:\n{response_text} ")

        try:
            # 获取生成Python代码
            plan_str = response_text.split("```python")[1].split("```")[0].strip()
            # ast.literal_eval()是用于将字符串安全的转换为Python字面量
            plan = ast.literal_eval(plan_str)
            return plan if isinstance(plan, list) else []
        except (ValueError, IndexError, SyntaxError) as e:
            print(f"\n❌ 解析计划时出错:{e}")
            print(f"\n原始相应:{response_text}")
            return []
        except Exception as e:
            print(f"\n❌ 解析计划时发生未知错误:{e}")
            return []

class Executor:
    def __init__(self, llm_client: HelloAgentsLLM, prompt_template: Optional[str]=None) -> None:
        self.llm_client = llm_client
        self.prompt_template = prompt_template if prompt_template else DEFAULT_EXECUTOR_PROMPT
    
    def executor(self, question: str, plan: List[str], **kwargs) -> str:
        """
        按计划执行步骤

        Args:
            question: 问题
            plan: 执行计划的步骤
            **kwargs: 调用LLM的参数
        
        Returns:
            答案
        """
        history = ""
        final_answer = ""

        print("\n--- 正在执行计划 ---")
        for i, step in enumerate(plan, 1): 
            print(f"\n-> 正在执行步骤 {i}/{len(plan)}: {step}")
            prompt = self.prompt_template.format(
                question=question,
                plan=plan,
                history=history,
                current_step=i
            )
            messages = [{"role": "user", "content": prompt}]
            response_text = self.llm_client.invoke(messages, **kwargs) or ""

            history += f"步骤 {1}: {step}\n结果:{response_text}\n\n"
            final_answer = response_text
            print(f"✅ 步骤 {i} 已完成，结果: {final_answer}")
        
        return final_answer


class MyPlanAndSolveAgent(PlanAndSolveAgent):
    def __init__(
        self, 
        name: str, 
        llm: HelloAgentsLLM, 
        system_prompt: Optional[str] = None,
        config: Optional[Config] = None, 
        custom_prompts: Optional[Dict[str, str]] = None
    ):
        """
        Args:
            name: Agent名称
            llm: LLM实例
            system_prompt: 系统提示词
            config: 配置对象
            custom_prompts: 自定义提示词模板 {"planner": "", "executor": ""}
        """
        super().__init__(name, llm, system_prompt, config, custom_prompts)

        if custom_prompts:
            planner_prompt = custom_prompts.get("planner_prompt")
            executor_prompt = custom_prompts.get("executor_prompt")
        else:
            planner_prompt = None
            executor_prompt = None
        self.planner = Planner(self.llm, planner_prompt)
        self.executor = Executor(self.llm, executor_prompt)
    
    def run(self, input_text: str, **kwargs) -> str:
        """
        运行Plan and Solve Agent
        
        Args:
            input_text: 要解决的问题
            **kwargs: 其他参数
            
        Returns:
            最终答案
        """
        print(f"\n🤖 {self.name} 开始处理问题: {input_text}")
        
        # 1. 生成计划
        plan = self.planner.plan(input_text, **kwargs)
        if not plan:
            final_answer = "无法生成有效的行动计划，任务终止。"
            print(f"\n--- 任务终止 ---\n{final_answer}")

            self.add_message(Message(input_text, "user"))
            self.add_message(Message(final_answer, "assistant"))

            return final_answer

        # 2. 执行计划
        final_answer = self.executor.executor(input_text, plan, **kwargs)
        print(f"\n--- 任务完成 ---\n最终答案: {final_answer}")

        # 保存到历史记录
        self.add_message(Message(input_text, "user"))
        self.add_message(Message(final_answer, "assistant"))

        return final_answer




    