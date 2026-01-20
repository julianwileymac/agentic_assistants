"use client";

import * as React from "react";
import { NodeProps } from "@xyflow/react";
import { Wrench, Globe, Code } from "lucide-react";
import type { FlowNodeData } from "./index";
import { BaseNode } from "./BaseNode";

export function ToolNode(props: NodeProps<FlowNodeData>) {
  const { data } = props;
  
  return (
    <BaseNode {...props} icon={<Wrench className="size-4" />} color="from-rose-500 to-pink-500">
      <div className="space-y-1">
        {data.config?.toolName ? (
          <div className="flex justify-between">
            <span className="text-muted-foreground">Tool:</span>
            <span className="font-mono text-[10px]">{String(data.config.toolName)}</span>
          </div>
        ) : (
          <span className="text-muted-foreground italic">No tool selected</span>
        )}
        {data.config?.toolArgs && Object.keys(data.config.toolArgs).length > 0 && (
          <div className="bg-muted/50 p-1.5 rounded text-[10px] font-mono">
            {Object.entries(data.config.toolArgs as Record<string, unknown>)
              .slice(0, 3)
              .map(([k, v]) => (
                <div key={k}>{k}: {String(v)}</div>
              ))}
          </div>
        )}
      </div>
    </BaseNode>
  );
}

export function APICallNode(props: NodeProps<FlowNodeData>) {
  const { data } = props;
  
  const methodColors: Record<string, string> = {
    GET: "text-green-500",
    POST: "text-blue-500",
    PUT: "text-yellow-500",
    DELETE: "text-red-500",
    PATCH: "text-purple-500",
  };
  
  return (
    <BaseNode {...props} icon={<Globe className="size-4" />} color="from-rose-500 to-pink-500">
      <div className="space-y-1">
        <div className="flex items-center gap-2">
          <span className={`font-mono text-[10px] font-bold ${methodColors[String(data.config?.method) || "GET"]}`}>
            {String(data.config?.method) || "GET"}
          </span>
          {data.config?.url && (
            <span className="font-mono text-[10px] truncate flex-1">
              {String(data.config.url).slice(0, 30)}...
            </span>
          )}
        </div>
        {data.config?.headers && Object.keys(data.config.headers).length > 0 && (
          <div className="text-muted-foreground text-[10px]">
            {Object.keys(data.config.headers as Record<string, unknown>).length} headers
          </div>
        )}
        {data.config?.timeout && (
          <div className="flex justify-between">
            <span className="text-muted-foreground">Timeout:</span>
            <span className="font-mono">{String(data.config.timeout)}ms</span>
          </div>
        )}
      </div>
    </BaseNode>
  );
}

export function CodeExecutorNode(props: NodeProps<FlowNodeData>) {
  const { data } = props;
  
  const languageIcons: Record<string, string> = {
    python: "Python",
    javascript: "JS",
    typescript: "TS",
    shell: "Shell",
  };
  
  return (
    <BaseNode {...props} icon={<Code className="size-4" />} color="from-rose-500 to-pink-500">
      <div className="space-y-1">
        <div className="flex justify-between">
          <span className="text-muted-foreground">Language:</span>
          <span className="font-mono text-[10px] bg-muted px-1 rounded">
            {languageIcons[String(data.config?.language)] || String(data.config?.language) || "python"}
          </span>
        </div>
        {data.config?.code && (
          <div className="bg-muted/50 p-1.5 rounded text-[10px] font-mono line-clamp-3 whitespace-pre">
            {String(data.config.code).slice(0, 100)}...
          </div>
        )}
        {data.config?.sandbox && (
          <div className="text-amber-500 text-[10px]">Sandboxed execution</div>
        )}
      </div>
    </BaseNode>
  );
}
