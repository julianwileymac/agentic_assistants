"use client";

import * as React from "react";
import { Handle, Position, NodeProps } from "@xyflow/react";
import { GitBranch, Repeat, GitMerge } from "lucide-react";
import { cn } from "@/lib/utils";
import type { FlowNodeData } from "./index";
import { BaseNode } from "./BaseNode";

export function ConditionalNode(props: NodeProps<FlowNodeData>) {
  const { data, selected } = props;
  
  return (
    <div
      className={cn(
        "min-w-[180px] rounded-lg border-2 bg-background shadow-md transition-all",
        selected ? "ring-2 ring-primary ring-offset-2" : ""
      )}
    >
      <div className="flex items-center gap-2 px-3 py-2 rounded-t-md bg-gradient-to-r from-slate-500 to-slate-600 text-white">
        <GitBranch className="size-4" />
        <span className="font-medium text-sm">{data.label || "Conditional"}</span>
      </div>
      
      <div className="px-3 py-2 text-xs">
        {data.config?.condition ? (
          <code className="bg-muted px-1 py-0.5 rounded text-[10px]">
            {String(data.config.condition)}
          </code>
        ) : (
          <span className="text-muted-foreground italic">No condition set</span>
        )}
      </div>

      {/* Input handle (top) */}
      <Handle
        type="target"
        position={Position.Top}
        className="!w-3 !h-3 !bg-primary !border-2 !border-background"
      />
      
      {/* True output (right) */}
      <Handle
        type="source"
        position={Position.Right}
        id="true"
        className="!w-3 !h-3 !bg-green-500 !border-2 !border-background"
        style={{ top: "50%" }}
      />
      
      {/* False output (bottom) */}
      <Handle
        type="source"
        position={Position.Bottom}
        id="false"
        className="!w-3 !h-3 !bg-red-500 !border-2 !border-background"
      />
    </div>
  );
}

export function LoopNode(props: NodeProps<FlowNodeData>) {
  const { data, selected } = props;
  
  return (
    <div
      className={cn(
        "min-w-[180px] rounded-lg border-2 bg-background shadow-md transition-all",
        selected ? "ring-2 ring-primary ring-offset-2" : ""
      )}
    >
      <div className="flex items-center gap-2 px-3 py-2 rounded-t-md bg-gradient-to-r from-slate-500 to-slate-600 text-white">
        <Repeat className="size-4" />
        <span className="font-medium text-sm">{data.label || "Loop"}</span>
      </div>
      
      <div className="px-3 py-2 text-xs">
        <div className="flex justify-between">
          <span className="text-muted-foreground">Max iterations:</span>
          <span className="font-mono">{data.config?.maxIterations || 10}</span>
        </div>
      </div>

      <Handle
        type="target"
        position={Position.Top}
        className="!w-3 !h-3 !bg-primary !border-2 !border-background"
      />
      
      {/* Loop body output */}
      <Handle
        type="source"
        position={Position.Right}
        id="body"
        className="!w-3 !h-3 !bg-blue-500 !border-2 !border-background"
        style={{ top: "50%" }}
      />
      
      {/* Loop complete output */}
      <Handle
        type="source"
        position={Position.Bottom}
        id="complete"
        className="!w-3 !h-3 !bg-primary !border-2 !border-background"
      />
    </div>
  );
}

export function ParallelNode(props: NodeProps<FlowNodeData>) {
  const { data, selected } = props;
  
  return (
    <div
      className={cn(
        "min-w-[180px] rounded-lg border-2 bg-background shadow-md transition-all",
        selected ? "ring-2 ring-primary ring-offset-2" : ""
      )}
    >
      <div className="flex items-center gap-2 px-3 py-2 rounded-t-md bg-gradient-to-r from-slate-500 to-slate-600 text-white">
        <GitMerge className="size-4" />
        <span className="font-medium text-sm">{data.label || "Parallel"}</span>
      </div>
      
      <div className="px-3 py-2 text-xs text-muted-foreground">
        Execute branches in parallel
      </div>

      <Handle
        type="target"
        position={Position.Top}
        className="!w-3 !h-3 !bg-primary !border-2 !border-background"
      />
      
      {/* Multiple output handles for parallel branches */}
      <Handle
        type="source"
        position={Position.Bottom}
        id="branch-1"
        className="!w-3 !h-3 !bg-primary !border-2 !border-background"
        style={{ left: "25%" }}
      />
      <Handle
        type="source"
        position={Position.Bottom}
        id="branch-2"
        className="!w-3 !h-3 !bg-primary !border-2 !border-background"
        style={{ left: "50%" }}
      />
      <Handle
        type="source"
        position={Position.Bottom}
        id="branch-3"
        className="!w-3 !h-3 !bg-primary !border-2 !border-background"
        style={{ left: "75%" }}
      />
    </div>
  );
}
