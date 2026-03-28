"use client";

import * as React from "react";
import { useCallback, useEffect, useRef, useState } from "react";
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
  EdgeLabelRenderer,
  BaseEdge,
  getBezierPath,
  type EdgeProps,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import ELK from "elkjs/lib/elk.bundled.js";

import { flowNodeTypes, type FlowNodeData } from "./nodes";
import { apiFetch } from "@/lib/api";
import { getWsUrl } from "@/lib/api-client";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import {
  LayoutGrid,
  Save,
  Download,
  ShieldCheck,
  Maximize,
  Plus,
  Loader2,
} from "lucide-react";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface FlowCanvasProps {
  flowId?: string;
  readOnly?: boolean;
  className?: string;
  initialNodes?: Node<FlowNodeData>[];
  initialEdges?: Edge[];
  onNodesChange?: (nodes: Node[]) => void;
  onEdgesChange?: (edges: Edge[]) => void;
  onNodeSelect?: (node: Node<FlowNodeData> | null) => void;
}

type ExecutionStatus = "pending" | "running" | "success" | "failed";

interface NodeExecState {
  [nodeId: string]: ExecutionStatus;
}

// ---------------------------------------------------------------------------
// ELK auto-layout hook
// ---------------------------------------------------------------------------

const elk = new ELK();

const ELK_OPTIONS = {
  "elk.algorithm": "layered",
  "elk.direction": "DOWN",
  "elk.spacing.nodeNode": "80",
  "elk.layered.spacing.nodeNodeBetweenLayers": "100",
  "elk.layered.crossingMinimization.strategy": "LAYER_SWEEP",
};

function useAutoLayout() {
  const [layouting, setLayouting] = useState(false);

  const computeLayout = useCallback(
    async (nodes: Node[], edges: Edge[]): Promise<{ nodes: Node[]; edges: Edge[] }> => {
      if (nodes.length === 0) return { nodes, edges };

      setLayouting(true);
      try {
        const graph = {
          id: "root",
          layoutOptions: ELK_OPTIONS,
          children: nodes.map((n) => ({
            id: n.id,
            width: n.measured?.width ?? 200,
            height: n.measured?.height ?? 80,
          })),
          edges: edges.map((e) => ({
            id: e.id,
            sources: [e.source],
            targets: [e.target],
          })),
        };

        const laid = await elk.layout(graph);

        const positioned = nodes.map((node) => {
          const found = laid.children?.find((c) => c.id === node.id);
          return {
            ...node,
            position: {
              x: found?.x ?? node.position.x,
              y: found?.y ?? node.position.y,
            },
          };
        });

        return { nodes: positioned, edges };
      } finally {
        setLayouting(false);
      }
    },
    [],
  );

  return { computeLayout, layouting };
}

// ---------------------------------------------------------------------------
// WebSocket execution-tracking hook
// ---------------------------------------------------------------------------

function useExecutionTracking(flowId: string | undefined) {
  const [execState, setExecState] = useState<NodeExecState>({});
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!flowId) return;

    const url = getWsUrl("/ws");
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      ws.send(JSON.stringify({ action: "subscribe", topic: `flow.${flowId}.execution` }));
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.topic === `flow.${flowId}.execution` && msg.node_id && msg.status) {
          setExecState((prev) => ({ ...prev, [msg.node_id]: msg.status as ExecutionStatus }));
        }
      } catch {
        /* ignore non-json frames */
      }
    };

    ws.onerror = () => {
      /* silent – avoids crashing when backend isn't running */
    };

    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, [flowId]);

  return execState;
}

// ---------------------------------------------------------------------------
// Execution-status ring styles
// ---------------------------------------------------------------------------

function execRingClass(status: ExecutionStatus | undefined): string {
  switch (status) {
    case "running":
      return "ring-2 ring-blue-500 ring-offset-2 ring-offset-background animate-pulse";
    case "success":
      return "ring-2 ring-green-500 ring-offset-2 ring-offset-background";
    case "failed":
      return "ring-2 ring-red-500 ring-offset-2 ring-offset-background";
    case "pending":
      return "ring-2 ring-muted-foreground/40 ring-offset-2 ring-offset-background";
    default:
      return "";
  }
}

// ---------------------------------------------------------------------------
// Labeled edge component
// ---------------------------------------------------------------------------

function LabeledEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data,
  style,
  markerEnd,
}: EdgeProps) {
  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    targetX,
    targetY,
    sourcePosition,
    targetPosition,
  });

  const label = (data?.label as string) ?? "data";

  return (
    <>
      <BaseEdge id={id} path={edgePath} style={style} markerEnd={markerEnd} />
      <EdgeLabelRenderer>
        <div
          style={{
            position: "absolute",
            transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
            pointerEvents: "all",
          }}
          className="rounded bg-muted/90 px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground border border-border shadow-sm"
        >
          {label}
        </div>
      </EdgeLabelRenderer>
    </>
  );
}

const edgeTypes = { labeled: LabeledEdge };

// ---------------------------------------------------------------------------
// FlowCanvas component
// ---------------------------------------------------------------------------

export function FlowCanvas({
  flowId,
  readOnly = false,
  className,
  initialNodes = [],
  initialEdges = [],
  onNodesChange: onNodesChangeCallback,
  onEdgesChange: onEdgesChangeCallback,
  onNodeSelect,
}: FlowCanvasProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState<Node<FlowNodeData>>(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const reactFlowInstance = useReactFlow();
  const { computeLayout, layouting } = useAutoLayout();
  const execState = useExecutionTracking(flowId);

  const [saving, setSaving] = useState(false);
  const [validating, setValidating] = useState(false);

  // ------ sync nodes/edges to parent ------ //
  useEffect(() => {
    onNodesChangeCallback?.(nodes);
  }, [nodes, onNodesChangeCallback]);

  useEffect(() => {
    onEdgesChangeCallback?.(edges);
  }, [edges, onEdgesChangeCallback]);

  // ------ apply execution ring classes to nodes ------ //
  useEffect(() => {
    if (Object.keys(execState).length === 0) return;

    setNodes((nds) =>
      nds.map((n) => {
        const status = execState[n.id];
        if (!status) return n;
        return {
          ...n,
          className: cn(n.className, execRingClass(status)),
          data: { ...n.data, status: status === "failed" ? "error" : status },
        };
      }),
    );
  }, [execState, setNodes]);

  // ------ load flow on mount ------ //
  useEffect(() => {
    if (!flowId) return;

    apiFetch<{ flow_yaml?: string }>(`/api/v1/flows/${flowId}`)
      .then((res) => {
        if (!res.flow_yaml) return;
        try {
          const { nodes: n, edges: e } = JSON.parse(res.flow_yaml);
          if (Array.isArray(n)) setNodes(n);
          if (Array.isArray(e)) setEdges(e);
        } catch {
          /* flow_yaml was not json-serialized nodes/edges */
        }
      })
      .catch(() => {
        /* flow not found – keep current state */
      });
    // only on mount / flowId change
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [flowId]);

  // ------ handlers ------ //

  const onConnect = useCallback(
    (params: Connection) => {
      if (readOnly) return;
      setEdges((eds) =>
        addEdge(
          {
            ...params,
            type: "labeled",
            data: { label: "data" },
            animated: true,
            style: { stroke: "hsl(var(--primary))", strokeWidth: 2 },
          },
          eds,
        ),
      );
    },
    [setEdges, readOnly],
  );

  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: Node<FlowNodeData>) => {
      onNodeSelect?.(node);
    },
    [onNodeSelect],
  );

  const onPaneClick = useCallback(() => {
    onNodeSelect?.(null);
  }, [onNodeSelect]);

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
    [reactFlowInstance, setNodes, readOnly],
  );

  // ------ toolbar actions ------ //

  const handleAutoLayout = useCallback(async () => {
    const result = await computeLayout(nodes, edges);
    setNodes(result.nodes);
  }, [nodes, edges, computeLayout, setNodes]);

  const handleSave = useCallback(async () => {
    if (!flowId) {
      toast.error("No flow ID – cannot save");
      return;
    }
    setSaving(true);
    try {
      await apiFetch(`/api/v1/flows/${flowId}`, {
        method: "POST",
        body: JSON.stringify({ flow_yaml: JSON.stringify({ nodes, edges }) }),
      });
      toast.success("Flow saved");
    } catch (err) {
      toast.error(`Save failed: ${err instanceof Error ? err.message : "unknown error"}`);
    } finally {
      setSaving(false);
    }
  }, [flowId, nodes, edges]);

  const handleValidate = useCallback(async () => {
    if (!flowId) {
      toast.error("No flow ID – cannot validate");
      return;
    }
    setValidating(true);
    try {
      const res = await apiFetch<{ valid: boolean; errors: string[] }>(
        `/api/v1/flows/${flowId}/validate`,
      );
      if (res.valid) {
        toast.success("Flow is valid");
      } else {
        res.errors.forEach((e) => toast.error(e));
      }
    } catch (err) {
      toast.error(`Validation failed: ${err instanceof Error ? err.message : "unknown error"}`);
    } finally {
      setValidating(false);
    }
  }, [flowId]);

  const handleZoomToFit = useCallback(() => {
    reactFlowInstance.fitView({ padding: 0.2, duration: 300 });
  }, [reactFlowInstance]);

  const handleAddNode = useCallback(() => {
    if (readOnly) return;
    const center = reactFlowInstance.screenToFlowPosition({
      x: window.innerWidth / 2,
      y: window.innerHeight / 2,
    });
    const newNode: Node<FlowNodeData> = {
      id: `custom-${Date.now()}`,
      type: "llmNode",
      position: center,
      data: { label: "New Node", nodeType: "llm", config: {} },
    };
    setNodes((nds) => nds.concat(newNode));
  }, [reactFlowInstance, setNodes, readOnly]);

  // ------ render ------ //

  return (
    <div className={cn("relative h-full w-full", className)}>
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
        edgeTypes={edgeTypes}
        fitView
        snapToGrid
        snapGrid={[15, 15]}
        nodesDraggable={!readOnly}
        nodesConnectable={!readOnly}
        elementsSelectable={!readOnly}
        defaultEdgeOptions={{
          type: "labeled",
          animated: true,
          data: { label: "data" },
          style: { stroke: "hsl(var(--primary))", strokeWidth: 2 },
        }}
        proOptions={{ hideAttribution: true }}
      >
        {/* Built-in controls */}
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

        {/* ---- Floating toolbar ---- */}
        <Panel position="top-center" className="mt-2">
          <div className="flex items-center gap-1 rounded-lg border bg-background/95 px-2 py-1.5 shadow-lg backdrop-blur">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleAutoLayout}
              disabled={layouting || readOnly}
              className="h-8 gap-1.5 text-xs"
            >
              {layouting ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <LayoutGrid className="h-3.5 w-3.5" />
              )}
              Auto Layout
            </Button>

            <div className="mx-0.5 h-5 w-px bg-border" />

            <Button
              variant="ghost"
              size="sm"
              onClick={handleSave}
              disabled={saving || !flowId}
              className="h-8 gap-1.5 text-xs"
            >
              {saving ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <Save className="h-3.5 w-3.5" />
              )}
              Save
            </Button>

            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                if (!flowId) return;
                apiFetch<{ flow_yaml?: string }>(`/api/v1/flows/${flowId}`)
                  .then((res) => {
                    if (!res.flow_yaml) {
                      toast.info("No saved flow data");
                      return;
                    }
                    const { nodes: n, edges: e } = JSON.parse(res.flow_yaml);
                    if (Array.isArray(n)) setNodes(n);
                    if (Array.isArray(e)) setEdges(e);
                    toast.success("Flow loaded");
                  })
                  .catch(() => toast.error("Failed to load flow"));
              }}
              disabled={!flowId}
              className="h-8 gap-1.5 text-xs"
            >
              <Download className="h-3.5 w-3.5" />
              Load
            </Button>

            <div className="mx-0.5 h-5 w-px bg-border" />

            <Button
              variant="ghost"
              size="sm"
              onClick={handleValidate}
              disabled={validating || !flowId}
              className="h-8 gap-1.5 text-xs"
            >
              {validating ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <ShieldCheck className="h-3.5 w-3.5" />
              )}
              Validate
            </Button>

            <div className="mx-0.5 h-5 w-px bg-border" />

            <Button
              variant="ghost"
              size="sm"
              onClick={handleZoomToFit}
              className="h-8 gap-1.5 text-xs"
            >
              <Maximize className="h-3.5 w-3.5" />
              Fit
            </Button>

            <Button
              variant="ghost"
              size="sm"
              onClick={handleAddNode}
              disabled={readOnly}
              className="h-8 gap-1.5 text-xs"
            >
              <Plus className="h-3.5 w-3.5" />
              Add Node
            </Button>
          </div>
        </Panel>

        {/* ---- Status bar ---- */}
        <Panel position="bottom-center" className="mb-4">
          <div className="flex items-center gap-2 rounded-lg border bg-background/95 px-3 py-2 text-sm text-muted-foreground shadow-sm backdrop-blur">
            <span>
              {nodes.length} nodes &bull; {edges.length} connections
            </span>
            {readOnly && (
              <Badge variant="outline" className="text-yellow-500 border-yellow-500/40">
                Read Only
              </Badge>
            )}
            {flowId && (
              <Badge variant="secondary" className="font-mono text-[10px]">
                {flowId}
              </Badge>
            )}
          </div>
        </Panel>
      </ReactFlow>
    </div>
  );
}

export default FlowCanvas;
