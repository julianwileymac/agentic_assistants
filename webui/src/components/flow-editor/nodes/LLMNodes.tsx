"use client";

import * as React from "react";
import { NodeProps } from "@xyflow/react";
import { Brain, FileText, MessageSquare } from "lucide-react";
import type { FlowNodeData } from "./index";
import { BaseNode } from "./BaseNode";

export function LLMNode(props: NodeProps<FlowNodeData>) {
  const { data } = props;
  
  return (
    <BaseNode {...props} icon={<Brain className="size-4" />} color="from-violet-500 to-purple-500">
      <div className="space-y-1">
        <div className="flex justify-between">
          <span className="text-muted-foreground">Model:</span>
          <span className="font-mono text-[10px]">{data.config?.model || "llama3.2"}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">Temp:</span>
          <span className="font-mono">{data.config?.temperature || 0.7}</span>
        </div>
        {data.config?.maxTokens && (
          <div className="flex justify-between">
            <span className="text-muted-foreground">Max Tokens:</span>
            <span className="font-mono">{String(data.config.maxTokens)}</span>
          </div>
        )}
      </div>
    </BaseNode>
  );
}

export function PromptTemplateNode(props: NodeProps<FlowNodeData>) {
  const { data } = props;
  
  return (
    <BaseNode {...props} icon={<FileText className="size-4" />} color="from-violet-500 to-purple-500">
      <div className="space-y-1">
        {data.config?.template ? (
          <div className="bg-muted/50 p-1.5 rounded text-[10px] font-mono line-clamp-3">
            {String(data.config.template).slice(0, 100)}
            {String(data.config.template).length > 100 && "..."}
          </div>
        ) : (
          <span className="text-muted-foreground italic">No template set</span>
        )}
        {data.config?.variables && Array.isArray(data.config.variables) && (
          <div className="flex flex-wrap gap-1 mt-1">
            {(data.config.variables as string[]).map((v) => (
              <span key={v} className="bg-primary/10 text-primary px-1 rounded text-[10px]">
                {"{" + v + "}"}
              </span>
            ))}
          </div>
        )}
      </div>
    </BaseNode>
  );
}

export function ChatModelNode(props: NodeProps<FlowNodeData>) {
  const { data } = props;
  
  return (
    <BaseNode {...props} icon={<MessageSquare className="size-4" />} color="from-violet-500 to-purple-500">
      <div className="space-y-1">
        <div className="flex justify-between">
          <span className="text-muted-foreground">Model:</span>
          <span className="font-mono text-[10px]">{data.config?.model || "llama3.2"}</span>
        </div>
        {data.config?.systemPrompt && (
          <div className="bg-muted/50 p-1.5 rounded text-[10px] line-clamp-2 mt-1">
            System: {String(data.config.systemPrompt).slice(0, 60)}...
          </div>
        )}
        {data.config?.memoryEnabled && (
          <div className="text-green-500 text-[10px]">Memory enabled</div>
        )}
      </div>
    </BaseNode>
  );
}
