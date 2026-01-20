"use client";

import * as React from "react";
import { NodeProps } from "@xyflow/react";
import { Search, ArrowUpDown, Binary, Database } from "lucide-react";
import type { FlowNodeData } from "./index";
import { BaseNode } from "./BaseNode";

export function RetrieverNode(props: NodeProps<FlowNodeData>) {
  const { data } = props;
  
  return (
    <BaseNode {...props} icon={<Search className="size-4" />} color="from-blue-500 to-cyan-500">
      <div className="space-y-1">
        <div className="flex justify-between">
          <span className="text-muted-foreground">Top K:</span>
          <span className="font-mono">{data.config?.topK || 5}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">Min Score:</span>
          <span className="font-mono">{data.config?.minScore || 0.7}</span>
        </div>
        {data.config?.vectorStoreId && (
          <div className="text-muted-foreground text-[10px] truncate">
            Store: {String(data.config.vectorStoreId)}
          </div>
        )}
      </div>
    </BaseNode>
  );
}

export function RerankerNode(props: NodeProps<FlowNodeData>) {
  const { data } = props;
  
  return (
    <BaseNode {...props} icon={<ArrowUpDown className="size-4" />} color="from-blue-500 to-cyan-500">
      <div className="space-y-1">
        <div className="flex justify-between">
          <span className="text-muted-foreground">Model:</span>
          <span className="font-mono text-[10px]">{data.config?.model || "cross-encoder"}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">Top N:</span>
          <span className="font-mono">{data.config?.topN || 3}</span>
        </div>
      </div>
    </BaseNode>
  );
}

export function EmbeddingNode(props: NodeProps<FlowNodeData>) {
  const { data } = props;
  
  return (
    <BaseNode {...props} icon={<Binary className="size-4" />} color="from-blue-500 to-cyan-500">
      <div className="space-y-1">
        <div className="flex justify-between">
          <span className="text-muted-foreground">Model:</span>
          <span className="font-mono text-[10px]">{data.config?.model || "nomic-embed-text"}</span>
        </div>
        {data.config?.dimensions && (
          <div className="flex justify-between">
            <span className="text-muted-foreground">Dims:</span>
            <span className="font-mono">{String(data.config.dimensions)}</span>
          </div>
        )}
      </div>
    </BaseNode>
  );
}

export function VectorStoreNode(props: NodeProps<FlowNodeData>) {
  const { data } = props;
  
  return (
    <BaseNode {...props} icon={<Database className="size-4" />} color="from-blue-500 to-cyan-500">
      <div className="space-y-1">
        <div className="flex justify-between">
          <span className="text-muted-foreground">Collection:</span>
          <span className="font-mono text-[10px]">{data.config?.collection || "default"}</span>
        </div>
        {data.config?.indexType && (
          <div className="flex justify-between">
            <span className="text-muted-foreground">Index:</span>
            <span className="font-mono text-[10px]">{String(data.config.indexType)}</span>
          </div>
        )}
      </div>
    </BaseNode>
  );
}
