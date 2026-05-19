---
type: log
course: Hello-Agents
created: 2026-05-09
updated: 2026-05-09
tags:
  - hello-agents
  - log
---

# Hello-Agents 学习日志

## 2026-05-09 17:55

操作：初始化 Hello-Agents Obsidian 学习库

创建：
- 全部目录结构（00-99）
- 系统文件：index、学习进度、问题清单、实验问题清单、log
- 学习地图：Hello-Agents 学习地图、推荐学习路线
- 模板文件：章节笔记、概念卡片、范式卡片、架构卡片、实验记录、阶段复盘、项目实践

更新：
- 无（首次创建）

发现的问题：
- 无

下一步建议：
- 使用 `/chapter Ch01 初识智能体` 开始第一章学习

## 2026-05-09 (第二次操作)

操作：`/chapter Ch04 智能体经典范式构建`

创建：
- [[Ch04_智能体经典范式构建]] — 章节笔记
- [[ReAct]] — 范式卡片
- [[Plan-and-Solve]] — 范式卡片
- [[Reflection]] — 范式卡片
- [[ToolExecutor]] — 架构卡片
- [[Memory_Reflection]] — 架构卡片
- [[Ch04_ReAct实验记录]] — 实验记录
- `05_实验记录/workspace/ch04_react_agent.py` — ReAct 空白骨架代码

更新：
- [[99_System/学习进度]] — Ch04 标记为"已有笔记"，统计更新为 2/16 章
- [[99_System/问题清单]] — 添加 4 个 Ch04 相关问题

发现的问题：
- 三种范式都依赖正则解析 LLM 输出，这是脆弱的
- SerpApi 需要付费注册，实验中可能需要替代方案

下一步建议：
- 编写 ch04_react_agent.py 的空白骨架
- 运行 ReAct 实验验证 Thought-Action-Observation 循环
- 可选：继续实现 Plan-and-Solve 或 Reflection 范式
