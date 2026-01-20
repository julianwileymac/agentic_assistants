"use client";

import * as React from "react";
import { NodeProps } from "@xyflow/react";
import { Workflow } from "lucide-react";
import type { FlowNodeData } from "./index";
import { BaseNode } from "./BaseNode";

export function PrefectTaskNode(props: NodeProps<FlowNodeData>) {
  const { data } = props;
  
  return (
    <BaseNode {...props} icon={<Workflow className="size-4" />} color="from-indigo-500 to-blue-600">
      <div className="space-y-1">
        {data.config?.taskName ? (
          <div className="flex justify-between">
            <span className="text-muted-foreground">Task:</span>
            <span className="font-mono text-[10px]">{String(data.config.taskName)}</span>
          </div>
        ) : (
          <span className="text-muted-foreground italic">No task configured</span>
        )}
        <div className="flex justify-between">
          <span className="text-muted-foreground">Retries:</span>
          <span className="font-mono">{data.config?.retries || 3}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">Retry Delay:</span>
          <span className="font-mono">{data.config?.retryDelay || 30}s</span>
        </div>
        {data.config?.cacheKey && (
          <div className="text-green-500 text-[10px]">Caching enabled</div>
        )}
        {data.config?.tags && Array.isArray(data.config.tags) && (
          <div className="flex flex-wrap gap-1 mt-1">
            {(data.config.tags as string[]).slice(0, 3).map((tag) => (
              <span key={tag} className="bg-indigo-500/10 text-indigo-600 px-1 rounded text-[10px]">
                {tag}
              </span>
            ))}
          </div>
        )}
        {data.status === "running" && (
          <div className="flex items-center gap-1 text-blue-500 text-[10px] mt-1">
            <span className="animate-pulse">Running in Prefect...</span>
          </div>
        )}
      </div>
    </BaseNode>
  );
}
