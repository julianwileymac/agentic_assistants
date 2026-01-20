"use client";

import * as React from "react";
import { Handle, Position, NodeProps } from "@xyflow/react";
import { User, ShieldCheck, ThumbsUp } from "lucide-react";
import { cn } from "@/lib/utils";
import type { FlowNodeData } from "./index";
import { BaseNode } from "./BaseNode";

export function HumanReviewNode(props: NodeProps<FlowNodeData>) {
  const { data, selected } = props;
  
  return (
    <div
      className={cn(
        "min-w-[180px] rounded-lg border-2 bg-background shadow-md transition-all border-dashed border-green-500/50",
        selected ? "ring-2 ring-green-500 ring-offset-2" : ""
      )}
    >
      <div className="flex items-center gap-2 px-3 py-2 rounded-t-md bg-gradient-to-r from-green-500 to-emerald-500 text-white">
        <User className="size-4" />
        <span className="font-medium text-sm">{data.label || "Human Review"}</span>
      </div>
      
      <div className="px-3 py-2 text-xs space-y-1">
        {data.config?.assignee && (
          <div className="flex justify-between">
            <span className="text-muted-foreground">Assignee:</span>
            <span className="font-mono text-[10px]">{String(data.config.assignee)}</span>
          </div>
        )}
        <div className="flex justify-between">
          <span className="text-muted-foreground">Timeout:</span>
          <span className="font-mono">{data.config?.timeout || 3600}s</span>
        </div>
        {data.config?.instructions && (
          <div className="bg-green-50 dark:bg-green-950/30 p-1.5 rounded text-[10px] mt-1">
            {String(data.config.instructions).slice(0, 80)}...
          </div>
        )}
        <div className="flex items-center gap-1 text-green-600 text-[10px] mt-1">
          <User className="size-3" />
          Pauses for human input
        </div>
      </div>

      <Handle
        type="target"
        position={Position.Top}
        className="!w-3 !h-3 !bg-green-500 !border-2 !border-background"
      />
      <Handle
        type="source"
        position={Position.Bottom}
        className="!w-3 !h-3 !bg-green-500 !border-2 !border-background"
      />
    </div>
  );
}

export function ApprovalGateNode(props: NodeProps<FlowNodeData>) {
  const { data, selected } = props;
  
  return (
    <div
      className={cn(
        "min-w-[180px] rounded-lg border-2 bg-background shadow-md transition-all border-dashed border-green-500/50",
        selected ? "ring-2 ring-green-500 ring-offset-2" : ""
      )}
    >
      <div className="flex items-center gap-2 px-3 py-2 rounded-t-md bg-gradient-to-r from-green-500 to-emerald-500 text-white">
        <ShieldCheck className="size-4" />
        <span className="font-medium text-sm">{data.label || "Approval Gate"}</span>
      </div>
      
      <div className="px-3 py-2 text-xs space-y-1">
        {data.config?.approvers && Array.isArray(data.config.approvers) && (
          <div>
            <span className="text-muted-foreground text-[10px]">Approvers:</span>
            <div className="flex flex-wrap gap-1 mt-0.5">
              {(data.config.approvers as string[]).map((a) => (
                <span key={a} className="bg-green-500/10 text-green-600 px-1 rounded text-[10px]">
                  {a}
                </span>
              ))}
            </div>
          </div>
        )}
        <div className="flex justify-between">
          <span className="text-muted-foreground">Min Approvals:</span>
          <span className="font-mono">{data.config?.minApprovals || 1}</span>
        </div>
      </div>

      <Handle
        type="target"
        position={Position.Top}
        className="!w-3 !h-3 !bg-green-500 !border-2 !border-background"
      />
      {/* Approved output */}
      <Handle
        type="source"
        position={Position.Right}
        id="approved"
        className="!w-3 !h-3 !bg-green-600 !border-2 !border-background"
        style={{ top: "50%" }}
      />
      {/* Rejected output */}
      <Handle
        type="source"
        position={Position.Bottom}
        id="rejected"
        className="!w-3 !h-3 !bg-red-500 !border-2 !border-background"
      />
    </div>
  );
}

export function FeedbackNode(props: NodeProps<FlowNodeData>) {
  const { data } = props;
  
  return (
    <BaseNode {...props} icon={<ThumbsUp className="size-4" />} color="from-green-500 to-emerald-500">
      <div className="space-y-1">
        <div className="flex justify-between">
          <span className="text-muted-foreground">Type:</span>
          <span className="font-mono text-[10px]">{data.config?.feedbackType || "rating"}</span>
        </div>
        {data.config?.feedbackType === "rating" && (
          <div className="flex justify-between">
            <span className="text-muted-foreground">Scale:</span>
            <span className="font-mono">1-5</span>
          </div>
        )}
        {data.config?.emitRLMetric && (
          <div className="text-blue-500 text-[10px]">Feeds into RL training</div>
        )}
      </div>
    </BaseNode>
  );
}
