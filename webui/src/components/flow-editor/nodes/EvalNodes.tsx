"use client";

import * as React from "react";
import { NodeProps } from "@xyflow/react";
import { Scale, CheckCircle, Target } from "lucide-react";
import type { FlowNodeData } from "./index";
import { BaseNode } from "./BaseNode";

export function LLMJudgeNode(props: NodeProps<FlowNodeData>) {
  const { data } = props;
  
  return (
    <BaseNode {...props} icon={<Scale className="size-4" />} color="from-amber-500 to-orange-500">
      <div className="space-y-1">
        {data.config?.criteria && Array.isArray(data.config.criteria) && (
          <div>
            <span className="text-muted-foreground text-[10px]">Criteria:</span>
            <div className="flex flex-wrap gap-1 mt-0.5">
              {(data.config.criteria as string[]).slice(0, 3).map((c) => (
                <span key={c} className="bg-amber-500/10 text-amber-600 px-1 rounded text-[10px]">
                  {c}
                </span>
              ))}
              {(data.config.criteria as string[]).length > 3 && (
                <span className="text-muted-foreground text-[10px]">
                  +{(data.config.criteria as string[]).length - 3}
                </span>
              )}
            </div>
          </div>
        )}
        <div className="flex justify-between">
          <span className="text-muted-foreground">Score Range:</span>
          <span className="font-mono text-[10px]">
            {Array.isArray(data.config?.scoreRange) 
              ? `${data.config.scoreRange[0]}-${data.config.scoreRange[1]}`
              : "1-5"}
          </span>
        </div>
        {data.config?.emitRLMetric && (
          <div className="text-green-500 text-[10px]">RL metric enabled</div>
        )}
      </div>
    </BaseNode>
  );
}

export function FaithfulnessNode(props: NodeProps<FlowNodeData>) {
  const { data } = props;
  
  return (
    <BaseNode {...props} icon={<CheckCircle className="size-4" />} color="from-amber-500 to-orange-500">
      <div className="space-y-1">
        <div className="flex justify-between">
          <span className="text-muted-foreground">Threshold:</span>
          <span className="font-mono">{data.config?.threshold || 0.8}</span>
        </div>
        <div className="text-muted-foreground text-[10px]">
          Checks if answer is grounded in context
        </div>
        {data.metrics?.faithfulnessScore !== undefined && (
          <div className="flex justify-between mt-1 pt-1 border-t border-dashed">
            <span className="text-muted-foreground">Score:</span>
            <span className={`font-mono ${
              data.metrics.faithfulnessScore >= (data.config?.threshold || 0.8)
                ? "text-green-500"
                : "text-red-500"
            }`}>
              {data.metrics.faithfulnessScore.toFixed(2)}
            </span>
          </div>
        )}
      </div>
    </BaseNode>
  );
}

export function RelevanceNode(props: NodeProps<FlowNodeData>) {
  const { data } = props;
  
  return (
    <BaseNode {...props} icon={<Target className="size-4" />} color="from-amber-500 to-orange-500">
      <div className="space-y-1">
        <div className="flex justify-between">
          <span className="text-muted-foreground">Threshold:</span>
          <span className="font-mono">{data.config?.threshold || 0.7}</span>
        </div>
        <div className="text-muted-foreground text-[10px]">
          Checks answer relevance to query
        </div>
        {data.metrics?.relevanceScore !== undefined && (
          <div className="flex justify-between mt-1 pt-1 border-t border-dashed">
            <span className="text-muted-foreground">Score:</span>
            <span className={`font-mono ${
              data.metrics.relevanceScore >= (data.config?.threshold || 0.7)
                ? "text-green-500"
                : "text-red-500"
            }`}>
              {data.metrics.relevanceScore.toFixed(2)}
            </span>
          </div>
        )}
      </div>
    </BaseNode>
  );
}
