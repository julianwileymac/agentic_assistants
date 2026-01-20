"use client";

import * as React from "react";
import { Handle, Position, NodeProps } from "@xyflow/react";
import { Play, Square } from "lucide-react";
import { cn } from "@/lib/utils";
import type { FlowNodeData } from "./index";

export function StartNode({ data, selected }: NodeProps<FlowNodeData>) {
  return (
    <div
      className={cn(
        "w-20 h-20 rounded-full border-2 bg-gradient-to-br from-green-500 to-emerald-600 text-white flex flex-col items-center justify-center shadow-lg transition-all",
        selected ? "ring-4 ring-green-300 ring-offset-2" : ""
      )}
    >
      <Play className="size-6 fill-current" />
      <span className="text-xs font-medium mt-1">{data.label || "Start"}</span>
      <Handle
        type="source"
        position={Position.Bottom}
        className="!w-3 !h-3 !bg-white !border-2 !border-green-600"
      />
    </div>
  );
}

export function EndNode({ data, selected }: NodeProps<FlowNodeData>) {
  return (
    <div
      className={cn(
        "w-20 h-20 rounded-full border-2 bg-gradient-to-br from-red-500 to-rose-600 text-white flex flex-col items-center justify-center shadow-lg transition-all",
        selected ? "ring-4 ring-red-300 ring-offset-2" : ""
      )}
    >
      <Square className="size-6 fill-current" />
      <span className="text-xs font-medium mt-1">{data.label || "End"}</span>
      <Handle
        type="target"
        position={Position.Top}
        className="!w-3 !h-3 !bg-white !border-2 !border-red-600"
      />
    </div>
  );
}
