"""
Ch08 记忆与检索 - 实验体验版
用途：快速体验 MemoryTool 和 RAGTool 的基本功能

使用前：
1. pip install "hello-agents[all]==0.2.0"
2. 在 .env 中配置 Qdrant、Neo4j、Embedding API
3. 或在代码中切换为本地 Embedding / 内存存储

原始参考：00_Source/hello-agents/code/chapter8/
"""

# ============================================================
# 实验 1：MemoryTool 基础操作
# 体验 add / search / summary / forget / consolidate
# ============================================================
from hello_agents.tools import MemoryTool

def test_memory_basic():
    """测试记忆系统的基本操作"""
    # TODO: 创建 MemoryTool 实例
    # TODO: 添加三种类型的记忆（working / episodic / semantic）
    # TODO: 搜索记忆
    # TODO: 获取摘要和统计
    # TODO: 执行遗忘和整合
    pass

# ============================================================
# 实验 2：RAGTool 文档处理
# 体验 add_document / add_text / search / ask
# ============================================================
from hello_agents.tools import RAGTool

def test_rag_basic():
    """测试 RAG 系统的基本操作"""
    # TODO: 创建 RAGTool 实例
    # TODO: 添加文本知识（不必是真正的 PDF）
    # TODO: 搜索知识库
    # TODO: 智能问答（检索 + LLM 生成）
    pass

# ============================================================
# 实验 3：Agent + Memory + RAG 集成
# 验证 "万物皆为工具" 的设计理念
# ============================================================
from hello_agents import SimpleAgent, HelloAgentsLLM, ToolRegistry

def test_agent_integration():
    """测试 Agent 集成 Memory 和 RAG 工具"""
    # TODO: 创建 LLM 实例
    # TODO: 创建 SimpleAgent
    # TODO: 创建 ToolRegistry，注册 MemoryTool 和 RAGTool
    # TODO: 为 Agent 配置工具
    # TODO: 运行对话，验证 Agent 能正确使用两个工具
    pass

if __name__ == "__main__":
    print("🔬 Ch08 记忆与检索实验")
    print("请选择实验：")
    print("1. MemoryTool 基础操作")
    print("2. RAGTool 文档处理")
    print("3. Agent + Memory + RAG 集成")

    # 由于外部服务依赖，建议逐项运行
    test_memory_basic()
    # test_rag_basic()
    # test_agent_integration()
