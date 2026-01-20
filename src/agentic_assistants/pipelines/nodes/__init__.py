"""
Pipeline nodes for Agentic Assistants.

This module provides reusable pipeline nodes for common operations
like vector store operations, embedding generation, and data processing.

Includes flow nodes for:
- RAG: Retriever, Reranker, Embedding, VectorStore
- LLM: LLM, PromptTemplate, ChatModel
- Evaluation: LLMJudge, Faithfulness, Relevance
- Human-in-the-Loop: HumanReview, ApprovalGate, Feedback
- Tools: Tool, APICall, CodeExecutor
- Data: DataSource, DataSink, Transform

Example:
    >>> from agentic_assistants.pipelines.nodes import vectorstore_upsert_node
    >>> from agentic_assistants.pipelines import Pipeline, node
    >>> 
    >>> pipeline = Pipeline([
    ...     node(process_documents, inputs="raw_docs", outputs="processed"),
    ...     node(vectorstore_upsert_node, inputs=["processed", "config"], outputs="result"),
    ... ])
"""

from agentic_assistants.pipelines.nodes.vectorstore import (
    vectorstore_upsert_node,
    vectorstore_delete_node,
    vectorstore_search_node,
    vectorstore_create_collection_node,
    vectorstore_count_node,
    VectorStoreOutputConfig,
    create_vectorstore_sink_node,
)

# Base classes
from agentic_assistants.pipelines.nodes.base import (
    BaseFlowNode,
    NodeConfig,
    NodeExecutionResult,
    create_node_factory,
)

# RAG nodes
from agentic_assistants.pipelines.nodes.rag_nodes import (
    RetrieverNode,
    RetrieverConfig,
    RerankerNode,
    RerankerConfig,
    EmbeddingNode,
    EmbeddingConfig,
    VectorStoreNode,
    VectorStoreConfig,
)

# LLM nodes
from agentic_assistants.pipelines.nodes.llm_nodes import (
    LLMNode,
    LLMConfig,
    PromptTemplateNode,
    PromptTemplateConfig,
    ChatModelNode,
    ChatModelConfig,
)

# Evaluation nodes
from agentic_assistants.pipelines.nodes.eval_nodes import (
    LLMJudgeNode,
    LLMJudgeConfig,
    FaithfulnessNode,
    FaithfulnessConfig,
    RelevanceNode,
    RelevanceConfig,
)

# Human-in-the-Loop nodes
from agentic_assistants.pipelines.nodes.hitl_nodes import (
    HumanReviewNode,
    HumanReviewConfig,
    ApprovalGateNode,
    ApprovalGateConfig,
    FeedbackNode,
    FeedbackConfig,
    get_hitl_store,
)

# Tool nodes
from agentic_assistants.pipelines.nodes.tool_nodes import (
    ToolNode,
    ToolConfig,
    APICallNode,
    APICallConfig,
    CodeExecutorNode,
    CodeExecutorConfig,
    get_tool_registry,
)

# Data nodes
from agentic_assistants.pipelines.nodes.data_nodes import (
    DataSourceNode,
    DataSourceConfig,
    DataSinkNode,
    DataSinkConfig,
    TransformNode,
    TransformConfig,
)

__all__ = [
    # Base classes
    "BaseFlowNode",
    "NodeConfig",
    "NodeExecutionResult",
    "create_node_factory",
    
    # Vector store nodes (legacy)
    "vectorstore_upsert_node",
    "vectorstore_delete_node",
    "vectorstore_search_node",
    "vectorstore_create_collection_node",
    "vectorstore_count_node",
    "VectorStoreOutputConfig",
    "create_vectorstore_sink_node",
    
    # RAG nodes
    "RetrieverNode",
    "RetrieverConfig",
    "RerankerNode",
    "RerankerConfig",
    "EmbeddingNode",
    "EmbeddingConfig",
    "VectorStoreNode",
    "VectorStoreConfig",
    
    # LLM nodes
    "LLMNode",
    "LLMConfig",
    "PromptTemplateNode",
    "PromptTemplateConfig",
    "ChatModelNode",
    "ChatModelConfig",
    
    # Evaluation nodes
    "LLMJudgeNode",
    "LLMJudgeConfig",
    "FaithfulnessNode",
    "FaithfulnessConfig",
    "RelevanceNode",
    "RelevanceConfig",
    
    # Human-in-the-Loop nodes
    "HumanReviewNode",
    "HumanReviewConfig",
    "ApprovalGateNode",
    "ApprovalGateConfig",
    "FeedbackNode",
    "FeedbackConfig",
    "get_hitl_store",
    
    # Tool nodes
    "ToolNode",
    "ToolConfig",
    "APICallNode",
    "APICallConfig",
    "CodeExecutorNode",
    "CodeExecutorConfig",
    "get_tool_registry",
    
    # Data nodes
    "DataSourceNode",
    "DataSourceConfig",
    "DataSinkNode",
    "DataSinkConfig",
    "TransformNode",
    "TransformConfig",
]
