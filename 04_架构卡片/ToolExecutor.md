---
type: architecture-card
course: Hello-Agents
status: draft
created: 2026-05-09
updated: 2026-05-09
tags:
  - hello-agents
  - architecture
  - tool-executor
---

# ToolExecutor（工具执行器）

## 组件职责

统一管理 Agent 可用的所有工具（注册、查找、执行），是 Agent 与外部世界交互的"手脚"。

## 为什么需要它？

Agent 可能需要调用多个不同的工具（搜索、计算、数据库查询等）。如果没有统一的管理器，代码中会散落着各种 if-elif 判断。ToolExecutor 提供了一个干净的注册-调度机制：
- 工具提供者只需 `registerTool(name, description, func)`
- Agent 只需根据名称调用，不需要知道工具内部实现

## 输入

- `registerTool(name, description, func)` — 注册一个工具
  - `name`: 工具名称（如 "Search"）
  - `description`: 工具描述（**最关键**：LLM 依赖描述决定何时使用）
  - `func`: 可调用函数

## 处理过程

- `getTool(name)` — 根据名称返回工具函数
- `getAvailableTools()` — 返回所有工具的格式化描述字符串（用于插入 Prompt）

## 输出

- 工具函数的返回值（字符串格式的 Observation）
- 所有工具的文本描述（嵌入到 Agent 的系统提示词中）

## 与其他组件的关系

```mermaid
flowchart TD
    A[Agent] -->|Action: Search[query]| TE[ToolExecutor]
    TE -->|查找名称| T1[search工具]
    TE -->|查找名称| T2[计算器工具]
    TE -->|查找名称| T3[...其他工具]
    T1 -->|返回结果| A
    T2 -->|返回结果| A
    T3 -->|返回结果| A
```

## 关键代码位置

- 文件：`00_Source/hello-agents/code/chapter4/tools.py`
- 类：`ToolExecutor`
- 方法：`registerTool()`, `getTool()`, `getAvailableTools()`

## 设计要点

**工具描述是最关键的环节**。LLM 不会读代码，它只看 description 来决定是否使用这个工具。描述不好 → LLM 选错工具 → 整个流程失败。

好的描述示例：
```python
"一个网页搜索引擎。当你需要回答关于时事、事实以及在知识库中找不到的信息时使用。"
```

差的描述示例：
```python
"搜索工具。"  # 太模糊，LLM 不知道什么场景该用
```

## 我的理解

ToolExecutor 的本质就是一个**字典映射** `name → {description, func}`。但它的设计精妙之处在于把"描述"也作为一等公民——因为描述是给 LLM 看的，而 LLM 是 Agent 的大脑。这体现了 Agent 工程的一个核心原则：**Prompt 就是接口**。

## 相关章节

- [[Ch04_智能体经典范式构建]]
- [[Ch01_初识智能体]]（工具的概念基础）
