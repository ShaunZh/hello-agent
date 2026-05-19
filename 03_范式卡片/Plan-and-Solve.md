---
type: paradigm-card
course: Hello-Agents
status: draft
created: 2026-05-09
updated: 2026-05-09
tags:
  - hello-agents
  - paradigm
  - plan-and-solve
---

# Plan-and-Solve

## 它解决什么问题？

解决"复杂多步推理任务中，Chain-of-Thought 容易偏离轨道"的问题。当任务需要很多步骤时，LLM 容易在中间迷失。Plan-and-Solve 通过"先规划蓝图，再按步骤施工"的方式，让智能体始终保持目标一致性。

由 Lei Wang 于 2023 年提出。核心思想是将任务**解耦为两个独立阶段**：规划（Planning）和执行（Solving）。

## 基本循环

```mermaid
flowchart LR
    Q[用户问题] --> P[Planner: 生成计划]
    P -->|步骤列表| E1[Executor: 执行步骤1]
    E1 -->|结果作为上下文| E2[Executor: 执行步骤2]
    E2 -->|结果作为上下文| E3[Executor: 执行步骤3...]
    E3 --> Ans[最终答案]
```

形式化表达：

```
Plan:  P = π_plan(q)                        // 生成计划
Solve: s_i = π_solve(q, P, s_1...s_{i-1})  // 逐步执行
```

## 适合场景

- **多步数学应用题**：需要先列出计算步骤，再逐一求解
- **需要整合多个信息源的报告**：先规划结构，再逐一填充
- **代码生成任务**：先设计函数/模块结构，再逐一实现
- 任何"可以提前规划好所有步骤"的任务

## 不适合场景

- **需要动态调整的任务**：计划生成后无法根据中间结果修改（静态计划）
- **需要外部工具的任务**：标准 Plan-and-Solve 不直接调用工具
- **环境不确定的任务**：如旅行规划（机票可能售罄），需要 ReAct 的灵活性

## 关键 Prompt / 伪代码

```python
# 规划器提示词
PLANNER_PROMPT = """
你是顶级AI规划专家。将复杂问题分解成简单步骤。
输出必须是Python列表格式：
```python
["步骤1", "步骤2", "步骤3", ...]
```
问题: {question}
"""

# 执行器提示词
EXECUTOR_PROMPT = """
你是AI执行专家。严格按照计划，专注解决当前步骤。
原始问题: {question}
完整计划: {plan}
历史结果: {history}
当前步骤: {current_step}
请仅输出当前步骤的答案。
"""

# 伪代码
plan = planner.plan(question)        # 阶段1: 规划
for step in plan:                    # 阶段2: 执行
    result = executor.solve(step, question, plan, history)
    history.append(result)
return history[-1]                   # 最后一步的结果 = 最终答案
```

## 核心组件

| 组件 | 职责 |
|------|------|
| **Planner** | 接收问题，输出结构化步骤列表（Python list 格式） |
| **Executor** | 逐步骤执行，每步将历史结果作为上下文传入下一步 |
| **PlanAndSolveAgent** | 协调者（Orchestrator），组合 Planner + Executor |

## 最小例子

```
问题: 周一卖了15个苹果。周二是周一的2倍。周三比周二少5个。三天总共？

规划阶段:
["计算周一销量: 15个",
 "计算周二销量: 15×2=30个",
 "计算周三销量: 30-5=25个",
 "计算总销量: 15+30+25=70个"]

执行阶段:
步骤1 → 15
步骤2 → 30  (历史: 周一=15)
步骤3 → 25  (历史: 周一=15, 周二=30)
步骤4 → 70  (历史: 周一=15, 周二=30, 周三=25)

最终答案: 70
```

## 与 ReAct 的对比

| 维度 | ReAct | Plan-and-Solve |
|------|-------|----------------|
| 决策方式 | 走一步看一步 | 先画蓝图再施工 |
| 工具调用 | 动态调用外部工具 | 不直接调用工具 |
| 计划灵活性 | 每步可调整 | 计划固定不变 |
| 适用任务 | 探索性、需要外部信息 | 结构化、可提前规划 |
| LLM 调用次数 | 不确定（取决于复杂度） | 确定（1次规划 + N次执行） |

## 我自己的理解

Plan-and-Solve 的精妙之处在于"解耦"。把"想"和"做"完全分开：Planner 专注全局规划（类似架构师画蓝图），Executor 专注局部执行（类似工人按图纸施工）。这种分工让每个组件更专注、更简单。

但它最大的短板是"计划不可变"。如果执行步骤2时发现步骤1的结果有问题，或者环境变了，整个计划就废了。这也是为什么实际应用中常常需要结合 ReAct 的动态调整能力。

## 相关实验

- [[Ch04_ReAct实验记录]]（对比 ReAct 与 Plan-and-Solve 的效果差异）

## 相关概念

- [[Agent]]：Plan-and-Solve 是 Agent 的一种规划范式
- [[ReAct]]：Plan-and-Solve 的对立面——ReAct 不做预先规划

## 来源章节

- [[Ch04_智能体经典范式构建]]
