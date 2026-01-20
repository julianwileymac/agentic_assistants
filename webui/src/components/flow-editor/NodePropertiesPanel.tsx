"use client";

import * as React from "react";
import { Node } from "@xyflow/react";
import { Trash2, Info, Settings, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { type FlowNodeData, getNodeCategory, getNodeDefinition } from "./nodes";

interface NodePropertiesPanelProps {
  node: Node<FlowNodeData>;
  onUpdate: (updates: Partial<FlowNodeData>) => void;
  onDelete: () => void;
}

// Configuration field definitions by node type
const nodeConfigFields: Record<string, ConfigField[]> = {
  // RAG Nodes
  retrieverNode: [
    { key: "vectorStoreId", label: "Vector Store ID", type: "text" },
    { key: "topK", label: "Top K Results", type: "number", defaultValue: 5 },
    { key: "minScore", label: "Min Score", type: "number", defaultValue: 0.7 },
    { key: "filters", label: "Filters (JSON)", type: "json" },
  ],
  rerankerNode: [
    { key: "model", label: "Model", type: "select", options: ["cross-encoder", "cohere-rerank", "bge-reranker"] },
    { key: "topN", label: "Top N", type: "number", defaultValue: 3 },
  ],
  embeddingNode: [
    { key: "model", label: "Model", type: "select", options: ["nomic-embed-text", "mxbai-embed-large", "all-minilm"] },
    { key: "dimensions", label: "Dimensions", type: "number" },
  ],
  vectorStoreNode: [
    { key: "collection", label: "Collection Name", type: "text", defaultValue: "default" },
    { key: "indexType", label: "Index Type", type: "select", options: ["hnsw", "flat", "ivf"] },
  ],

  // LLM Nodes
  llmNode: [
    { key: "model", label: "Model", type: "select", options: ["llama3.2", "llama3.1", "mistral", "mixtral", "phi3", "qwen2.5"] },
    { key: "temperature", label: "Temperature", type: "number", defaultValue: 0.7 },
    { key: "maxTokens", label: "Max Tokens", type: "number" },
    { key: "topP", label: "Top P", type: "number", defaultValue: 0.9 },
    { key: "systemPrompt", label: "System Prompt", type: "textarea" },
  ],
  promptTemplateNode: [
    { key: "template", label: "Prompt Template", type: "textarea" },
    { key: "variables", label: "Variables (comma-separated)", type: "text" },
  ],
  chatModelNode: [
    { key: "model", label: "Model", type: "select", options: ["llama3.2", "llama3.1", "mistral", "mixtral"] },
    { key: "systemPrompt", label: "System Prompt", type: "textarea" },
    { key: "memoryEnabled", label: "Enable Memory", type: "boolean" },
    { key: "maxHistory", label: "Max History Messages", type: "number", defaultValue: 10 },
  ],

  // Eval Nodes
  llmJudgeNode: [
    { key: "model", label: "Judge Model", type: "select", options: ["llama3.2", "gpt-4", "claude-3"] },
    { key: "criteria", label: "Criteria (comma-separated)", type: "text" },
    { key: "scoreRange", label: "Score Range (min,max)", type: "text", defaultValue: "1,5" },
    { key: "promptTemplate", label: "Evaluation Prompt", type: "textarea" },
    { key: "emitRLMetric", label: "Emit RL Metric", type: "boolean" },
    { key: "metricName", label: "RL Metric Name", type: "text" },
  ],
  faithfulnessNode: [
    { key: "threshold", label: "Threshold", type: "number", defaultValue: 0.8 },
    { key: "model", label: "Evaluation Model", type: "select", options: ["llama3.2", "gpt-4"] },
  ],
  relevanceNode: [
    { key: "threshold", label: "Threshold", type: "number", defaultValue: 0.7 },
    { key: "model", label: "Evaluation Model", type: "select", options: ["llama3.2", "gpt-4"] },
  ],

  // HITL Nodes
  humanReviewNode: [
    { key: "assignee", label: "Assignee", type: "text" },
    { key: "timeout", label: "Timeout (seconds)", type: "number", defaultValue: 3600 },
    { key: "instructions", label: "Instructions", type: "textarea" },
    { key: "webhookUrl", label: "Webhook URL", type: "text" },
  ],
  approvalGateNode: [
    { key: "approvers", label: "Approvers (comma-separated)", type: "text" },
    { key: "minApprovals", label: "Min Approvals", type: "number", defaultValue: 1 },
    { key: "timeout", label: "Timeout (seconds)", type: "number", defaultValue: 86400 },
  ],
  feedbackNode: [
    { key: "feedbackType", label: "Feedback Type", type: "select", options: ["rating", "binary", "text", "ranking"] },
    { key: "emitRLMetric", label: "Emit RL Metric", type: "boolean" },
    { key: "metricName", label: "RL Metric Name", type: "text" },
  ],

  // Tool Nodes
  toolNode: [
    { key: "toolName", label: "Tool Name", type: "text" },
    { key: "toolArgs", label: "Tool Arguments (JSON)", type: "json" },
  ],
  apiCallNode: [
    { key: "url", label: "URL", type: "text" },
    { key: "method", label: "Method", type: "select", options: ["GET", "POST", "PUT", "DELETE", "PATCH"] },
    { key: "headers", label: "Headers (JSON)", type: "json" },
    { key: "body", label: "Body", type: "textarea" },
    { key: "timeout", label: "Timeout (ms)", type: "number", defaultValue: 30000 },
  ],
  codeExecutorNode: [
    { key: "language", label: "Language", type: "select", options: ["python", "javascript", "typescript", "shell"] },
    { key: "code", label: "Code", type: "code" },
    { key: "sandbox", label: "Sandboxed Execution", type: "boolean", defaultValue: true },
  ],

  // Data Nodes
  dataSourceNode: [
    { key: "sourceId", label: "Data Source ID", type: "text" },
    { key: "sourceType", label: "Source Type", type: "select", options: ["database", "file", "api", "s3", "gcs"] },
    { key: "query", label: "Query / Path", type: "textarea" },
  ],
  dataSinkNode: [
    { key: "sinkId", label: "Data Sink ID", type: "text" },
    { key: "format", label: "Format", type: "select", options: ["json", "csv", "parquet", "yaml"] },
    { key: "mode", label: "Write Mode", type: "select", options: ["overwrite", "append", "merge"] },
  ],
  transformNode: [
    { key: "transformType", label: "Transform Type", type: "select", options: ["map", "filter", "reduce", "flatMap", "aggregate", "join"] },
    { key: "expression", label: "Expression", type: "textarea" },
  ],

  // Control Nodes
  conditionalNode: [
    { key: "condition", label: "Condition", type: "text" },
  ],
  loopNode: [
    { key: "maxIterations", label: "Max Iterations", type: "number", defaultValue: 10 },
    { key: "breakCondition", label: "Break Condition", type: "text" },
  ],

  // Orchestration Nodes
  prefectTaskNode: [
    { key: "taskName", label: "Task Name", type: "text" },
    { key: "retries", label: "Retries", type: "number", defaultValue: 3 },
    { key: "retryDelay", label: "Retry Delay (seconds)", type: "number", defaultValue: 30 },
    { key: "cacheKey", label: "Cache Key Function", type: "text" },
    { key: "tags", label: "Tags (comma-separated)", type: "text" },
    { key: "timeout", label: "Timeout (seconds)", type: "number" },
  ],
};

interface ConfigField {
  key: string;
  label: string;
  type: "text" | "number" | "boolean" | "select" | "textarea" | "json" | "code";
  options?: string[];
  defaultValue?: unknown;
}

export function NodePropertiesPanel({ node, onUpdate, onDelete }: NodePropertiesPanelProps) {
  const category = getNodeCategory(node.type || "");
  const definition = getNodeDefinition(node.type || "");
  const configFields = nodeConfigFields[node.type || ""] || [];

  const updateConfig = (key: string, value: unknown) => {
    onUpdate({
      config: {
        ...node.data.config,
        [key]: value,
      },
    });
  };

  const parseValue = (value: string, type: string) => {
    if (type === "number") {
      const num = parseFloat(value);
      return isNaN(num) ? undefined : num;
    }
    if (type === "boolean") {
      return value === "true";
    }
    if (type === "json") {
      try {
        return JSON.parse(value);
      } catch {
        return value;
      }
    }
    return value;
  };

  const renderField = (field: ConfigField) => {
    const currentValue = node.data.config?.[field.key];
    const displayValue = currentValue ?? field.defaultValue ?? "";

    switch (field.type) {
      case "text":
        return (
          <Input
            value={String(displayValue)}
            onChange={(e) => updateConfig(field.key, e.target.value)}
            placeholder={`Enter ${field.label.toLowerCase()}`}
          />
        );

      case "number":
        return (
          <Input
            type="number"
            value={displayValue === "" ? "" : Number(displayValue)}
            onChange={(e) => updateConfig(field.key, parseValue(e.target.value, "number"))}
            placeholder={`Enter ${field.label.toLowerCase()}`}
          />
        );

      case "boolean":
        return (
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">{displayValue ? "Enabled" : "Disabled"}</span>
            <Switch
              checked={Boolean(displayValue)}
              onCheckedChange={(checked) => updateConfig(field.key, checked)}
            />
          </div>
        );

      case "select":
        return (
          <Select
            value={String(displayValue)}
            onValueChange={(value) => updateConfig(field.key, value)}
          >
            <SelectTrigger>
              <SelectValue placeholder={`Select ${field.label.toLowerCase()}`} />
            </SelectTrigger>
            <SelectContent>
              {field.options?.map((option) => (
                <SelectItem key={option} value={option}>
                  {option}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        );

      case "textarea":
      case "code":
        return (
          <Textarea
            value={String(displayValue)}
            onChange={(e) => updateConfig(field.key, e.target.value)}
            placeholder={`Enter ${field.label.toLowerCase()}`}
            rows={field.type === "code" ? 8 : 4}
            className={field.type === "code" ? "font-mono text-xs" : ""}
          />
        );

      case "json":
        return (
          <Textarea
            value={typeof displayValue === "object" ? JSON.stringify(displayValue, null, 2) : String(displayValue)}
            onChange={(e) => updateConfig(field.key, parseValue(e.target.value, "json"))}
            placeholder="Enter JSON..."
            rows={4}
            className="font-mono text-xs"
          />
        );

      default:
        return null;
    }
  };

  return (
    <ScrollArea className="h-[calc(100vh-180px)]">
      <div className="space-y-6 py-4 pr-4">
        {/* Node Info */}
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            {category && (
              <div className={`w-3 h-3 rounded-full bg-gradient-to-br ${category.color}`} />
            )}
            <Badge variant="secondary">{definition?.label || node.type}</Badge>
          </div>
          <p className="text-sm text-muted-foreground">
            {definition?.description || "Configure this node's properties"}
          </p>
        </div>

        <Separator />

        {/* Basic Properties */}
        <Accordion type="single" collapsible defaultValue="basic">
          <AccordionItem value="basic">
            <AccordionTrigger className="text-sm">
              <div className="flex items-center gap-2">
                <Info className="size-4" />
                Basic Properties
              </div>
            </AccordionTrigger>
            <AccordionContent className="space-y-4 pt-2">
              <div className="space-y-2">
                <Label htmlFor="node-label">Label</Label>
                <Input
                  id="node-label"
                  value={node.data.label}
                  onChange={(e) => onUpdate({ label: e.target.value })}
                  placeholder="Node label"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="node-description">Description</Label>
                <Textarea
                  id="node-description"
                  value={node.data.description || ""}
                  onChange={(e) => onUpdate({ description: e.target.value })}
                  placeholder="Optional description"
                  rows={2}
                />
              </div>
            </AccordionContent>
          </AccordionItem>

          {/* Configuration */}
          {configFields.length > 0 && (
            <AccordionItem value="config">
              <AccordionTrigger className="text-sm">
                <div className="flex items-center gap-2">
                  <Settings className="size-4" />
                  Configuration
                </div>
              </AccordionTrigger>
              <AccordionContent className="space-y-4 pt-2">
                {configFields.map((field) => (
                  <div key={field.key} className="space-y-2">
                    <Label htmlFor={field.key}>{field.label}</Label>
                    {renderField(field)}
                  </div>
                ))}
              </AccordionContent>
            </AccordionItem>
          )}

          {/* RL Metrics (for eval nodes) */}
          {(node.type?.includes("Judge") || node.type?.includes("feedback") || node.type?.includes("faithfulness") || node.type?.includes("relevance")) && (
            <AccordionItem value="rl">
              <AccordionTrigger className="text-sm">
                <div className="flex items-center gap-2">
                  <Zap className="size-4" />
                  RL Optimization
                </div>
              </AccordionTrigger>
              <AccordionContent className="space-y-4 pt-2">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="emit-rl">Emit RL Metric</Label>
                    <Switch
                      id="emit-rl"
                      checked={Boolean(node.data.config?.emitRLMetric)}
                      onCheckedChange={(checked) => updateConfig("emitRLMetric", checked)}
                    />
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Enable to send evaluation scores to the RL training pipeline
                  </p>
                </div>

                {node.data.config?.emitRLMetric && (
                  <div className="space-y-2">
                    <Label htmlFor="metric-name">Metric Name</Label>
                    <Input
                      id="metric-name"
                      value={String(node.data.config?.metricName || "")}
                      onChange={(e) => updateConfig("metricName", e.target.value)}
                      placeholder="e.g., response_quality"
                    />
                  </div>
                )}
              </AccordionContent>
            </AccordionItem>
          )}
        </Accordion>

        <Separator />

        {/* Delete Button */}
        <Button variant="destructive" className="w-full" onClick={onDelete}>
          <Trash2 className="size-4 mr-2" />
          Delete Node
        </Button>
      </div>
    </ScrollArea>
  );
}

export default NodePropertiesPanel;
