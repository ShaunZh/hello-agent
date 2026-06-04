---
type: architecture-card
course: Hello-Agents
status: draft
created: 2026-06-04
updated: 2026-06-04
tags:
  - hello-agents
  - architecture
  - rag
---

# RAGTool（检索增强生成工具）

## 组件职责

将任意格式的文档（PDF/Word/图片/音频等）处理为可检索的知识库，并提供智能问答能力。封装为 Tool，Agent 可随时调用。

## 为什么需要它？

Agent 需要回答"这个文档里说了什么"但 LLM 训练时没见过这个文档。RAGTool 在 LLM "发言"前先查资料，把相关段落注入 Prompt。

## 处理链路

```mermaid
flowchart LR
    D[任意格式文档] --> M[MarkItDown: 统一转Markdown]
    M --> C[智能分块: 标题感知+Token估算]
    C --> E[Embedding: 文本→向量]
    E --> Q[(Qdrant向量库)]
    Q --> S[检索: 基础/MQE/HyDE]
    S --> P[注入Prompt]
    P --> L[LLM生成答案]
```

## 核心操作

| action | 功能 |
|--------|------|
| `add_document` | 添加文档（完整 pipeline：MarkItDown → 分块 → 向量化 → 存储） |
| `add_text` | 直接添加文本（跳过文档解析） |
| `search` | 搜索知识库 |
| `ask` | 智能问答（检索 + LLM 生成） |
| `stats` | 知识库统计 |

## 检索策略对比

| 策略 | 原理 | 适用场景 | 召回率 |
|------|------|---------|--------|
| 基础检索 | 问题向量直接检索 | 简单精确查询 | 基准 |
| MQE | LLM 生成多样化查询，并行检索合并 | 用词差异大 | +30~50% |
| HyDE | 先写假设答案，用答案向量检索 | 专业领域，语义鸿沟 | +20~40% |

## 智能分块

- 利用 Markdown 标题层次 `#/##/###` 确定语义边界
- 中英文混合 Token 估算：CJK 字符 ≈ 1 token
- 分块重叠（overlap_tokens）保证信息连续性

## 我的理解

RAGTool 的"五层七步"设计本质是一组规则化的 ETL + 检索 pipeline。最值得关注的是 MQE 和 HyDE 策略——它们不改变底层存储，只是换了一种"问法"，就能显著提升召回率。这说明 RAG 的瓶颈往往不在向量化本身，而在**查询和文档之间的语义对齐**。

## 相关章节

- [[Ch08_记忆与检索]]
