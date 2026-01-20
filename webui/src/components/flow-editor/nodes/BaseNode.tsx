"use client";

import * as React from "react";
import { Handle, Position, NodeProps } from "@xyflow/react";
import { cn } from "@/lib/utils";
import type { FlowNodeData } from "./index";

interface BaseNodeProps extends NodeProps<FlowNodeData> {
  icon: React.ReactNode;
  color: string;
  handles?: {
    top?: boolean;
    bottom?: boolean;
    left?: boolean;
    right?: boolean;
  };
  children?: React.ReactNode;
}

export function BaseNode({
  data,
  selected,
  icon,
  color,
  handles = { top: true, bottom: true },
  children,
}: BaseNodeProps) {
  const statusColors: Record<string, string> = {
    idle: "border-border",
    running: "border-blue-500 animate-pulse",
    success: "border-green-500",
    error: "border-red-500",
  };

  return (
    <div
      className={cn(
        "min-w-[180px] rounded-lg border-2 bg-background shadow-md transition-all",
        selected ? "ring-2 ring-primary ring-offset-2" : "",
        statusColors[data.status || "idle"]
      )}
    >
      {/* Header */}
      <div
        className={cn(
          "flex items-center gap-2 px-3 py-2 rounded-t-md bg-gradient-to-r text-white",
          color
        )}
      >
        {icon}
        <span className="font-medium text-sm truncate">{data.label}</span>
      </div>

      {/* Content */}
      <div className="px-3 py-2 text-xs">
        {data.description && (
          <p className="text-muted-foreground mb-2">{data.description}</p>
        )}
        {children}
        {data.metrics && Object.keys(data.metrics).length > 0 && (
          <div className="mt-2 pt-2 border-t border-dashed">
            {Object.entries(data.metrics).map(([key, value]) => (
              <div key={key} className="flex justify-between">
                <span className="text-muted-foreground">{key}:</span>
                <span className="font-mono">{value}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Handles */}
      {handles.top && (
        <Handle
          type="target"
          position={Position.Top}
          className="!w-3 !h-3 !bg-primary !border-2 !border-background"
        />
      )}
      {handles.bottom && (
        <Handle
          type="source"
          position={Position.Bottom}
          className="!w-3 !h-3 !bg-primary !border-2 !border-background"
        />
      )}
      {handles.left && (
        <Handle
          type="target"
          position={Position.Left}
          className="!w-3 !h-3 !bg-primary !border-2 !border-background"
        />
      )}
      {handles.right && (
        <Handle
          type="source"
          position={Position.Right}
          className="!w-3 !h-3 !bg-primary !border-2 !border-background"
        />
      )}
    </div>
  );
}

export default BaseNode;
