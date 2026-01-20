/**
 * Flow Editor Node Types Registry
 *
 * This module exports all custom node types for the flow editor.
 * Node types are organized by category:
 * - Flow Control: Start, End, Conditional, Loop
 * - RAG: Retriever, Reranker, Embedding, VectorStore
 * - LLM: LLM, PromptTemplate, ChatModel
 * - Evaluation: LLMJudge, Faithfulness, Relevance
 * - Human-in-the-Loop: HumanReview, ApprovalGate, Feedback
 * - Tools: Tool, APICall, CodeExecutor
 * - Data: DataSource, DataSink, Transform
 * - Orchestration: PrefectTask, Parallel
 */

import { NodeTypes } from "@xyflow/react";

// Import all node components
import { StartNode, EndNode } from "./StartEndNodes";
import { ConditionalNode, LoopNode, ParallelNode } from "./ControlNodes";
import { RetrieverNode, RerankerNode, EmbeddingNode, VectorStoreNode } from "./RAGNodes";
import { LLMNode, PromptTemplateNode, ChatModelNode } from "./LLMNodes";
import { LLMJudgeNode, FaithfulnessNode, RelevanceNode } from "./EvalNodes";
import { HumanReviewNode, ApprovalGateNode, FeedbackNode } from "./HITLNodes";
import { ToolNode, APICallNode, CodeExecutorNode } from "./ToolNodes";
import { DataSourceNode, DataSinkNode, TransformNode } from "./DataNodes";
import { PrefectTaskNode } from "./OrchestrationNodes";

// Type definition for flow node data
export interface FlowNodeData {
  label: string;
  nodeType: string;
  config: Record<string, unknown>;
  description?: string;
  status?: "idle" | "running" | "success" | "error";
  metrics?: Record<string, number>;
}

// Node category definitions for the palette
export interface NodeCategory {
  id: string;
  name: string;
  description: string;
  color: string;
  nodes: NodeDefinition[];
}

export interface NodeDefinition {
  type: string;
  label: string;
  description: string;
  icon: string;
  defaultConfig: Record<string, unknown>;
}

// Register all node types with React Flow
export const flowNodeTypes: NodeTypes = {
  // Flow Control
  startNode: StartNode,
  endNode: EndNode,
  conditionalNode: ConditionalNode,
  loopNode: LoopNode,
  parallelNode: ParallelNode,

  // RAG Components
  retrieverNode: RetrieverNode,
  rerankerNode: RerankerNode,
  embeddingNode: EmbeddingNode,
  vectorStoreNode: VectorStoreNode,

  // LLM Components
  llmNode: LLMNode,
  promptTemplateNode: PromptTemplateNode,
  chatModelNode: ChatModelNode,

  // Evaluation Components
  llmJudgeNode: LLMJudgeNode,
  faithfulnessNode: FaithfulnessNode,
  relevanceNode: RelevanceNode,

  // Human-in-the-Loop
  humanReviewNode: HumanReviewNode,
  approvalGateNode: ApprovalGateNode,
  feedbackNode: FeedbackNode,

  // Tool Components
  toolNode: ToolNode,
  apiCallNode: APICallNode,
  codeExecutorNode: CodeExecutorNode,

  // Data Components
  dataSourceNode: DataSourceNode,
  dataSinkNode: DataSinkNode,
  transformNode: TransformNode,

  // Orchestration
  prefectTaskNode: PrefectTaskNode,
};

// Node categories for the palette
export const nodeCategories: NodeCategory[] = [
  {
    id: "flow-control",
    name: "Flow Control",
    description: "Control flow execution",
    color: "from-slate-500 to-slate-600",
    nodes: [
      {
        type: "startNode",
        label: "Start",
        description: "Flow entry point",
        icon: "Play",
        defaultConfig: {},
      },
      {
        type: "endNode",
        label: "End",
        description: "Flow exit point",
        icon: "Square",
        defaultConfig: {},
      },
      {
        type: "conditionalNode",
        label: "Conditional",
        description: "Branch based on condition",
        icon: "GitBranch",
        defaultConfig: { condition: "" },
      },
      {
        type: "loopNode",
        label: "Loop",
        description: "Repeat execution",
        icon: "Repeat",
        defaultConfig: { maxIterations: 10 },
      },
      {
        type: "parallelNode",
        label: "Parallel",
        description: "Execute branches in parallel",
        icon: "GitMerge",
        defaultConfig: {},
      },
    ],
  },
  {
    id: "rag",
    name: "RAG Components",
    description: "Retrieval-Augmented Generation",
    color: "from-blue-500 to-cyan-500",
    nodes: [
      {
        type: "retrieverNode",
        label: "Retriever",
        description: "Retrieve relevant documents",
        icon: "Search",
        defaultConfig: { topK: 5, minScore: 0.7 },
      },
      {
        type: "rerankerNode",
        label: "Reranker",
        description: "Rerank retrieved documents",
        icon: "ArrowUpDown",
        defaultConfig: { model: "cross-encoder", topN: 3 },
      },
      {
        type: "embeddingNode",
        label: "Embedding",
        description: "Generate text embeddings",
        icon: "Binary",
        defaultConfig: { model: "nomic-embed-text" },
      },
      {
        type: "vectorStoreNode",
        label: "Vector Store",
        description: "Store and query vectors",
        icon: "Database",
        defaultConfig: { collection: "default" },
      },
    ],
  },
  {
    id: "llm",
    name: "LLM Components",
    description: "Language model operations",
    color: "from-violet-500 to-purple-500",
    nodes: [
      {
        type: "llmNode",
        label: "LLM",
        description: "Generate text with LLM",
        icon: "Brain",
        defaultConfig: { model: "llama3.2", temperature: 0.7 },
      },
      {
        type: "promptTemplateNode",
        label: "Prompt Template",
        description: "Format prompts with variables",
        icon: "FileText",
        defaultConfig: { template: "" },
      },
      {
        type: "chatModelNode",
        label: "Chat Model",
        description: "Conversational LLM",
        icon: "MessageSquare",
        defaultConfig: { model: "llama3.2", systemPrompt: "" },
      },
    ],
  },
  {
    id: "evaluation",
    name: "Evaluation",
    description: "Quality assessment",
    color: "from-amber-500 to-orange-500",
    nodes: [
      {
        type: "llmJudgeNode",
        label: "LLM Judge",
        description: "Evaluate output quality",
        icon: "Scale",
        defaultConfig: { criteria: [], scoreRange: [1, 5] },
      },
      {
        type: "faithfulnessNode",
        label: "Faithfulness",
        description: "Check answer faithfulness",
        icon: "CheckCircle",
        defaultConfig: { threshold: 0.8 },
      },
      {
        type: "relevanceNode",
        label: "Relevance",
        description: "Check answer relevance",
        icon: "Target",
        defaultConfig: { threshold: 0.7 },
      },
    ],
  },
  {
    id: "hitl",
    name: "Human-in-the-Loop",
    description: "Human intervention points",
    color: "from-green-500 to-emerald-500",
    nodes: [
      {
        type: "humanReviewNode",
        label: "Human Review",
        description: "Queue for human review",
        icon: "User",
        defaultConfig: { assignee: "", timeout: 3600 },
      },
      {
        type: "approvalGateNode",
        label: "Approval Gate",
        description: "Require human approval",
        icon: "ShieldCheck",
        defaultConfig: { approvers: [], minApprovals: 1 },
      },
      {
        type: "feedbackNode",
        label: "Feedback",
        description: "Collect human feedback",
        icon: "ThumbsUp",
        defaultConfig: { feedbackType: "rating" },
      },
    ],
  },
  {
    id: "tools",
    name: "Tools",
    description: "External tool integrations",
    color: "from-rose-500 to-pink-500",
    nodes: [
      {
        type: "toolNode",
        label: "Tool",
        description: "Execute a tool",
        icon: "Wrench",
        defaultConfig: { toolName: "", toolArgs: {} },
      },
      {
        type: "apiCallNode",
        label: "API Call",
        description: "Make HTTP API request",
        icon: "Globe",
        defaultConfig: { url: "", method: "GET", headers: {} },
      },
      {
        type: "codeExecutorNode",
        label: "Code Executor",
        description: "Execute code snippet",
        icon: "Code",
        defaultConfig: { language: "python", code: "" },
      },
    ],
  },
  {
    id: "data",
    name: "Data",
    description: "Data sources and sinks",
    color: "from-teal-500 to-cyan-600",
    nodes: [
      {
        type: "dataSourceNode",
        label: "Data Source",
        description: "Read from data source",
        icon: "Download",
        defaultConfig: { sourceId: "", query: "" },
      },
      {
        type: "dataSinkNode",
        label: "Data Sink",
        description: "Write to destination",
        icon: "Upload",
        defaultConfig: { sinkId: "", format: "json" },
      },
      {
        type: "transformNode",
        label: "Transform",
        description: "Transform data",
        icon: "Shuffle",
        defaultConfig: { transformType: "map", expression: "" },
      },
    ],
  },
  {
    id: "orchestration",
    name: "Orchestration",
    description: "Workflow orchestration",
    color: "from-indigo-500 to-blue-600",
    nodes: [
      {
        type: "prefectTaskNode",
        label: "Prefect Task",
        description: "Prefect workflow task",
        icon: "Workflow",
        defaultConfig: { taskName: "", retries: 3, retryDelay: 30 },
      },
    ],
  },
];

// Helper to get node definition by type
export function getNodeDefinition(type: string): NodeDefinition | undefined {
  for (const category of nodeCategories) {
    const node = category.nodes.find((n) => n.type === type);
    if (node) return node;
  }
  return undefined;
}

// Helper to get category by node type
export function getNodeCategory(type: string): NodeCategory | undefined {
  return nodeCategories.find((cat) => cat.nodes.some((n) => n.type === type));
}

// Export all node components for direct use
export {
  StartNode,
  EndNode,
  ConditionalNode,
  LoopNode,
  ParallelNode,
  RetrieverNode,
  RerankerNode,
  EmbeddingNode,
  VectorStoreNode,
  LLMNode,
  PromptTemplateNode,
  ChatModelNode,
  LLMJudgeNode,
  FaithfulnessNode,
  RelevanceNode,
  HumanReviewNode,
  ApprovalGateNode,
  FeedbackNode,
  ToolNode,
  APICallNode,
  CodeExecutorNode,
  DataSourceNode,
  DataSinkNode,
  TransformNode,
  PrefectTaskNode,
};
