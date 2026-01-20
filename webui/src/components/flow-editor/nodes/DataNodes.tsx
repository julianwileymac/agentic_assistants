"use client";

import * as React from "react";
import { NodeProps } from "@xyflow/react";
import { Download, Upload, Shuffle } from "lucide-react";
import type { FlowNodeData } from "./index";
import { BaseNode } from "./BaseNode";

export function DataSourceNode(props: NodeProps<FlowNodeData>) {
  const { data } = props;
  
  return (
    <BaseNode 
      {...props} 
      icon={<Download className="size-4" />} 
      color="from-teal-500 to-cyan-600"
      handles={{ top: false, bottom: true }}
    >
      <div className="space-y-1">
        {data.config?.sourceId ? (
          <div className="flex justify-between">
            <span className="text-muted-foreground">Source:</span>
            <span className="font-mono text-[10px]">{String(data.config.sourceId)}</span>
          </div>
        ) : (
          <span className="text-muted-foreground italic">No source configured</span>
        )}
        {data.config?.sourceType && (
          <div className="flex justify-between">
            <span className="text-muted-foreground">Type:</span>
            <span className="font-mono text-[10px]">{String(data.config.sourceType)}</span>
          </div>
        )}
        {data.config?.query && (
          <div className="bg-muted/50 p-1.5 rounded text-[10px] font-mono line-clamp-2">
            {String(data.config.query)}
          </div>
        )}
      </div>
    </BaseNode>
  );
}

export function DataSinkNode(props: NodeProps<FlowNodeData>) {
  const { data } = props;
  
  return (
    <BaseNode 
      {...props} 
      icon={<Upload className="size-4" />} 
      color="from-teal-500 to-cyan-600"
      handles={{ top: true, bottom: false }}
    >
      <div className="space-y-1">
        {data.config?.sinkId ? (
          <div className="flex justify-between">
            <span className="text-muted-foreground">Sink:</span>
            <span className="font-mono text-[10px]">{String(data.config.sinkId)}</span>
          </div>
        ) : (
          <span className="text-muted-foreground italic">No sink configured</span>
        )}
        <div className="flex justify-between">
          <span className="text-muted-foreground">Format:</span>
          <span className="font-mono text-[10px]">{data.config?.format || "json"}</span>
        </div>
        {data.config?.mode && (
          <div className="flex justify-between">
            <span className="text-muted-foreground">Mode:</span>
            <span className="font-mono text-[10px]">{String(data.config.mode)}</span>
          </div>
        )}
      </div>
    </BaseNode>
  );
}

export function TransformNode(props: NodeProps<FlowNodeData>) {
  const { data } = props;
  
  const transformTypes: Record<string, string> = {
    map: "Map",
    filter: "Filter",
    reduce: "Reduce",
    flatMap: "FlatMap",
    aggregate: "Aggregate",
    join: "Join",
  };
  
  return (
    <BaseNode {...props} icon={<Shuffle className="size-4" />} color="from-teal-500 to-cyan-600">
      <div className="space-y-1">
        <div className="flex justify-between">
          <span className="text-muted-foreground">Type:</span>
          <span className="font-mono text-[10px]">
            {transformTypes[String(data.config?.transformType)] || String(data.config?.transformType) || "map"}
          </span>
        </div>
        {data.config?.expression && (
          <div className="bg-muted/50 p-1.5 rounded text-[10px] font-mono line-clamp-2">
            {String(data.config.expression)}
          </div>
        )}
        {data.config?.outputSchema && (
          <div className="text-blue-500 text-[10px]">Schema defined</div>
        )}
      </div>
    </BaseNode>
  );
}
