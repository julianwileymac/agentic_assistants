"use client";

import * as React from "react";
import { useCallback } from "react";
import {
  ReactFlow,
  Controls,
  Background,
  MiniMap,
  addEdge,
  useNodesState,
  useEdgesState,
  Panel,
  Connection,
  Edge,
  Node,
  useReactFlow,
  BackgroundVariant,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import { flowNodeTypes, type FlowNodeData } from "./nodes";

interface FlowCanvasProps {
  initialNodes?: Node<FlowNodeData>[];
  initialEdges?: Edge[];
  onNodesChange?: (nodes: Node<FlowNodeData>[]) => void;
  onEdgesChange?: (edges: Edge[]) => void;
  onNodeSelect?: (node: Node<FlowNodeData> | null) => void;
  readOnly?: boolean;
}

export function FlowCanvas({
  initialNodes = [],
  initialEdges = [],
  onNodesChange: onNodesChangeCallback,
  onEdgesChange: onEdgesChangeCallback,
  onNodeSelect,
  readOnly = false,
}: FlowCanvasProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState<Node<FlowNodeData>>(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const reactFlowInstance = useReactFlow();

  // Sync nodes/edges with parent
  React.useEffect(() => {
    onNodesChangeCallback?.(nodes);
  }, [nodes, onNodesChangeCallback]);

  React.useEffect(() => {
    onEdgesChangeCallback?.(edges);
  }, [edges, onEdgesChangeCallback]);

  // Handle edge connections
  const onConnect = useCallback(
    (params: Connection) => {
      if (readOnly) return;
      setEdges((eds) =>
        addEdge(
          {
            ...params,
            animated: true,
            style: { stroke: "hsl(var(--primary))", strokeWidth: 2 },
          },
          eds
        )
      );
    },
    [setEdges, readOnly]
  );

  // Handle node selection
  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: Node<FlowNodeData>) => {
      onNodeSelect?.(node);
    },
    [onNodeSelect]
  );

  // Handle pane click (deselect)
  const onPaneClick = useCallback(() => {
    onNodeSelect?.(null);
  }, [onNodeSelect]);

  // Handle node drag from palette
  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();
      if (readOnly) return;

      const type = event.dataTransfer.getData("application/reactflow/type");
      const label = event.dataTransfer.getData("application/reactflow/label");
      const nodeType = event.dataTransfer.getData("application/reactflow/nodeType");

      if (!type) return;

      const position = reactFlowInstance.screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      const newNode: Node<FlowNodeData> = {
        id: `${type}-${Date.now()}`,
        type,
        position,
        data: {
          label: label || type,
          nodeType: nodeType || "custom",
          config: {},
        },
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [reactFlowInstance, setNodes, readOnly]
  );

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={readOnly ? undefined : onNodesChange}
      onEdgesChange={readOnly ? undefined : onEdgesChange}
      onConnect={onConnect}
      onNodeClick={onNodeClick}
      onPaneClick={onPaneClick}
      onDragOver={onDragOver}
      onDrop={onDrop}
      nodeTypes={flowNodeTypes}
      fitView
      snapToGrid
      snapGrid={[15, 15]}
      nodesDraggable={!readOnly}
      nodesConnectable={!readOnly}
      elementsSelectable={!readOnly}
      defaultEdgeOptions={{
        animated: true,
        style: { stroke: "hsl(var(--primary))", strokeWidth: 2 },
      }}
      proOptions={{ hideAttribution: true }}
    >
      <Controls showInteractive={!readOnly} />
      <MiniMap
        nodeStrokeWidth={3}
        zoomable
        pannable
        className="!bg-muted/50 !border-border"
        maskColor="rgba(0, 0, 0, 0.1)"
      />
      <Background
        variant={BackgroundVariant.Dots}
        gap={15}
        size={1}
        color="hsl(var(--muted-foreground) / 0.2)"
      />

      <Panel position="bottom-center" className="mb-4">
        <div className="bg-background/95 backdrop-blur border rounded-lg px-3 py-2 text-sm text-muted-foreground shadow-sm">
          {nodes.length} nodes &bull; {edges.length} connections
          {readOnly && <span className="ml-2 text-yellow-500">(Read Only)</span>}
        </div>
      </Panel>
    </ReactFlow>
  );
}

export default FlowCanvas;
