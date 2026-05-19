---
type: experiment-log
course: Hello-Agents
chapter: Ch04
status: draft
created: 2026-05-09
updated: 2026-05-09
tags:
  - hello-agents
  - experiment
  - react
  - chapter4
---

# Ch04 ReAct 实验记录

## 1. 实验目标

从零编写一个 ReAct Agent，验证 Thought-Action-Observation 循环能正确调用外部工具（搜索引擎）回答需要实时信息的问题。

## 2. 运行环境

- 操作系统：macOS
- Python 版本：3.14.3
- 依赖安装：`pip install openai python-dotenv google-search-results`
- 需要准备：LLM API KEY / SerpApi KEY

## 3. 相关文件

- 原始教程代码：`00_Source/hello-agents/code/chapter4/ReAct.py`
- LLM 封装：`00_Source/hello-agents/code/chapter4/llm_client.py`
- 工具定义：`00_Source/hello-agents/code/chapter4/tools.py`
- **我的工作副本**：`05_实验记录/workspace/ch04_react_agent.py`（空白骨架，待编写）
- Plan-and-Solve 参考：`00_Source/hello-agents/code/chapter4/Plan_and_solve.py`
- Reflection 参考：`00_Source/hello-agents/code/chapter4/Reflection.py`

## 4. 编写步骤

```text
步骤 1: HelloAgentsLLM    → LLM 调用封装（流式输出）
步骤 2: search()          → SerpApi 搜索工具
步骤 3: ToolExecutor      → 工具注册与调度
步骤 4: REACT_PROMPT      → 提示词模板设计
步骤 5: ReActAgent.run()  → 核心循环
步骤 6: _parse_output     → 正则解析 Thought/Action
步骤 7: 测试运行           → 问一个需要实时信息的问题
```

## 5. 预期输出

```
--- 第 1 步 ---
🧠 正在调用 xxx 模型...
Thought: 我需要搜索华为最新手机信息
Action: Search[华为最新手机型号及卖点]
🔍 正在执行搜索...
👀 观察: [1] 华为 Mate 70...

--- 第 2 步 ---
🧠 正在调用 xxx 模型...
Thought: 根据搜索结果，最新型号是 Mate 70
Action: Finish[华为最新手机是 Mate 70...]
🎉 最终答案: 华为最新手机是 Mate 70...
```

## 6. 后续实验建议

### 实验 A：添加计算器工具
为 ReAct Agent 添加一个 `Calculator[expr]` 工具，让它能回答数学问题。

### 实验 B：Plan-and-Solve
参考 `Plan_and_solve.py`，实现 Planner + Executor 两阶段架构。

### 实验 C：Reflection
参考 `Reflection.py`，实现代码生成 + 反思 + 优化的迭代循环。

### 实验 D：范式对比
用同一个问题分别运行三种范式，对比：
- LLM 调用次数
- 总耗时
- 答案质量
- 是否出错

## 7. 这个实验说明我理解了什么？

（运行后填写）

## 8. 后续问题

- [ ] 正则解析在什么情况下会失败？
- [ ] 如果 LLM 不遵循格式怎么办？
- [ ] 工具数量很多时，Prompt 会太长吗？
