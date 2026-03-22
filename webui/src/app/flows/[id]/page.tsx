"use client";

import * as React from "react";
import { useCallback, useState, useRef, useMemo } from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
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
  NodeTypes,
  ReactFlowProvider,
  useReactFlow,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import {
  ArrowLeft,
  Save,
  Loader2,
  Trash2,
  Play,
  Pause,
  RotateCcw,
  Check,
  AlertCircle,
  Settings,
  Code,
  Eye,
  ChevronRight,
  ChevronLeft,
  Maximize2,
  Download,
  Upload,
} from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { CodeEditor } from "@/components/code-editor";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { useFlow, useUpdateFlow, useValidateFlow, useRunFlow } from "@/lib/api";
import { toast } from "sonner";
import { TestingSection } from "@/components/testing/testing-section";

// Import flow editor components
import { FlowCanvas } from "@/components/flow-editor/FlowCanvas";
import { NodePalette } from "@/components/flow-editor/NodePalette";
import { NodePropertiesPanel } from "@/components/flow-editor/NodePropertiesPanel";
import { flowNodeTypes, type FlowNodeData } from "@/components/flow-editor/nodes";

const statusColors: Record<string, string> = {
  active: "bg-green-500/10 text-green-500 border-green-500/20",
  paused: "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
  draft: "bg-gray-500/10 text-gray-500 border-gray-500/20",
  archived: "bg-red-500/10 text-red-500 border-red-500/20",
};

// Parse flow YAML to extract nodes and edges
function parseFlowYaml(yaml: string): { nodes: Node<FlowNodeData>[]; edges: Edge[] } {
  // Default nodes if parsing fails or empty
  const defaultNodes: Node<FlowNodeData>[] = [
    {
      id: "start-1",
      type: "startNode",
      position: { x: 250, y: 50 },
      data: { label: "Start", nodeType: "start", config: {} },
    },
    {
      id: "end-1",
      type: "endNode",
      position: { x: 250, y: 400 },
      data: { label: "End", nodeType: "end", config: {} },
    },
  ];

  const defaultEdges: Edge[] = [];

  if (!yaml || yaml.trim() === "") {
    return { nodes: defaultNodes, edges: defaultEdges };
  }

  try {
    // Try to parse YAML-like structure for nodes
    // This is a simplified parser - in production, use js-yaml
    const lines = yaml.split("\n");
    const nodes: Node<FlowNodeData>[] = [...defaultNodes];
    const edges: Edge[] = [];

    let currentSection = "";
    let yOffset = 150;

    for (const line of lines) {
      const trimmed = line.trim();
      
      if (trimmed.startsWith("agents:")) {
        currentSection = "agents";
      } else if (trimmed.startsWith("tasks:")) {
        currentSection = "tasks";
      } else if (trimmed.startsWith("- name:") && currentSection === "agents") {
        const name = trimmed.replace("- name:", "").trim();
        nodes.push({
          id: `agent-${nodes.length}`,
          type: "llmNode",
          position: { x: 100, y: yOffset },
          data: { 
            label: name, 
            nodeType: "llm",
            config: { model: "llama3.2" }
          },
        });
        yOffset += 100;
      } else if (trimmed.startsWith("- name:") && currentSection === "tasks") {
        const name = trimmed.replace("- name:", "").trim();
        nodes.push({
          id: `task-${nodes.length}`,
          type: "toolNode",
          position: { x: 400, y: yOffset - 100 },
          data: { 
            label: name, 
            nodeType: "tool",
            config: {}
          },
        });
      }
    }

    // Connect nodes sequentially
    for (let i = 0; i < nodes.length - 1; i++) {
      if (nodes[i].type !== "endNode" && nodes[i + 1].type !== "startNode") {
        edges.push({
          id: `edge-${i}`,
          source: nodes[i].id,
          target: nodes[i + 1].id,
          animated: true,
        });
      }
    }

    return { nodes, edges };
  } catch (e) {
    return { nodes: defaultNodes, edges: defaultEdges };
  }
}

// Flow Editor Inner Component (needs ReactFlowProvider context)
function FlowEditorInner() {
  const router = useRouter();
  const params = useParams();
  const flowId = params.id as string;

  const { data: flow, isLoading, mutate } = useFlow(flowId);
  const { trigger: updateFlow, isMutating: isUpdating } = useUpdateFlow(flowId);
  const { trigger: validateFlow, isMutating: isValidating } = useValidateFlow(flowId);
  const { trigger: runFlow, isMutating: isRunning } = useRunFlow(flowId);

  const [activeTab, setActiveTab] = useState<"visual" | "yaml">("visual");
  const [selectedNode, setSelectedNode] = useState<Node<FlowNodeData> | null>(null);
  const [isPaletteOpen, setIsPaletteOpen] = useState(true);
  const [isPropertiesOpen, setIsPropertiesOpen] = useState(false);
  const [validationResult, setValidationResult] = useState<{
    valid: boolean;
    errors: string[];
    warnings: string[];
  } | null>(null);

  // Form state for flow details
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    flow_type: "crew",
    status: "draft",
    flow_yaml: "",
    tags: "",
  });

  // Flow nodes and edges state
  const [nodes, setNodes, onNodesChange] = useNodesState<Node<FlowNodeData>>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  const reactFlowInstance = useReactFlow();

  // Initialize form data and nodes when flow loads
  React.useEffect(() => {
    if (flow) {
      setFormData({
        name: flow.name,
        description: flow.description,
        flow_type: flow.flow_type,
        status: flow.status,
        flow_yaml: flow.flow_yaml,
        tags: flow.tags.join(", "),
      });

      // Parse YAML to nodes/edges
      const { nodes: parsedNodes, edges: parsedEdges } = parseFlowYaml(flow.flow_yaml);
      setNodes(parsedNodes);
      setEdges(parsedEdges);
    }
  }, [flow, setNodes, setEdges]);

  // Handle edge connections
  const onConnect = useCallback(
    (params: Connection) => {
      setEdges((eds) => addEdge({ ...params, animated: true }, eds));
    },
    [setEdges]
  );

  // Handle node selection
  const onNodeClick = useCallback((_: React.MouseEvent, node: Node<FlowNodeData>) => {
    setSelectedNode(node);
    setIsPropertiesOpen(true);
  }, []);

  // Handle node drag from palette
  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();

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
          config: {}
        },
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [reactFlowInstance, setNodes]
  );

  // Handle node property updates
  const onNodeUpdate = useCallback(
    (nodeId: string, updates: Partial<FlowNodeData>) => {
      setNodes((nds) =>
        nds.map((node) => {
          if (node.id === nodeId) {
            return {
              ...node,
              data: { ...node.data, ...updates },
            };
          }
          return node;
        })
      );
    },
    [setNodes]
  );

  // Delete selected node
  const onDeleteNode = useCallback(() => {
    if (selectedNode) {
      setNodes((nds) => nds.filter((n) => n.id !== selectedNode.id));
      setEdges((eds) =>
        eds.filter((e) => e.source !== selectedNode.id && e.target !== selectedNode.id)
      );
      setSelectedNode(null);
      setIsPropertiesOpen(false);
    }
  }, [selectedNode, setNodes, setEdges]);

  // Save flow
  const handleSave = async () => {
    if (!formData.name.trim()) {
      toast.error("Flow name is required");
      return;
    }

    try {
      await updateFlow({
        name: formData.name.trim(),
        description: formData.description.trim(),
        flow_type: formData.flow_type,
        status: formData.status,
        flow_yaml: formData.flow_yaml,
        tags: formData.tags
          .split(",")
          .map((t) => t.trim())
          .filter(Boolean),
        metadata: {
          nodes: nodes.map((n) => ({ id: n.id, type: n.type, position: n.position, data: n.data })),
          edges: edges.map((e) => ({ id: e.id, source: e.source, target: e.target })),
        },
      });
      toast.success("Flow saved successfully");
      mutate();
    } catch (error) {
      toast.error("Failed to save flow");
    }
  };

  // Validate flow
  const handleValidate = async () => {
    try {
      const result = await validateFlow();
      setValidationResult(result);
      if (result.valid) {
        toast.success("Flow is valid");
      } else {
        toast.error(`Validation failed: ${result.errors.join(", ")}`);
      }
    } catch (error) {
      toast.error("Failed to validate flow");
    }
  };

  // Run flow
  const handleRun = async () => {
    try {
      const result = await runFlow({});
      toast.success(`Flow started: ${result.status}`);
    } catch (error) {
      toast.error("Failed to run flow");
    }
  };

  // Delete flow
  const handleDelete = async () => {
    try {
      const response = await fetch(`http://localhost:8080/api/v1/flows/${flowId}`, {
        method: "DELETE",
      });

      if (response.ok) {
        toast.success("Flow deleted");
        router.push("/flows");
      } else {
        toast.error("Failed to delete flow");
      }
    } catch (error) {
      toast.error("Failed to delete flow");
    }
  };

  // Export flow as JSON
  const handleExport = () => {
    const flowData = {
      ...formData,
      nodes: nodes.map((n) => ({ id: n.id, type: n.type, position: n.position, data: n.data })),
      edges: edges.map((e) => ({ id: e.id, source: e.source, target: e.target })),
    };
    const blob = new Blob([JSON.stringify(flowData, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${formData.name || "flow"}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (isLoading) {
    return (
      <div className="h-screen flex flex-col">
        <div className="border-b p-4">
          <div className="flex items-center gap-4">
            <Skeleton className="h-10 w-10" />
            <div>
              <Skeleton className="h-8 w-64" />
              <Skeleton className="h-4 w-48 mt-2" />
            </div>
          </div>
        </div>
        <div className="flex-1">
          <Skeleton className="h-full w-full" />
        </div>
      </div>
    );
  }

  if (!flow) {
    return (
      <div className="h-screen flex items-center justify-center">
        <Card className="max-w-md">
          <CardContent className="pt-6 text-center">
            <AlertCircle className="size-12 mx-auto mb-4 text-muted-foreground" />
            <h3 className="text-lg font-semibold mb-2">Flow not found</h3>
            <p className="text-muted-foreground mb-4">
              The flow you&apos;re looking for doesn&apos;t exist or has been deleted.
            </p>
            <Button asChild>
              <Link href="/flows">Back to Flows</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="h-screen flex flex-col overflow-hidden">
      {/* Header */}
      <div className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 z-10">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" asChild>
              <Link href="/flows">
                <ArrowLeft className="size-4" />
              </Link>
            </Button>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-semibold">{flow.name}</h1>
                <Badge variant="outline" className={statusColors[flow.status]}>
                  {flow.status}
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground">
                {flow.flow_type} flow &bull; Updated{" "}
                {new Date(flow.updated_at).toLocaleDateString()}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Tab Switcher */}
            <div className="flex items-center border rounded-lg p-1 mr-2">
              <Button
                variant={activeTab === "visual" ? "secondary" : "ghost"}
                size="sm"
                onClick={() => setActiveTab("visual")}
              >
                <Eye className="size-4 mr-1" />
                Visual
              </Button>
              <Button
                variant={activeTab === "yaml" ? "secondary" : "ghost"}
                size="sm"
                onClick={() => setActiveTab("yaml")}
              >
                <Code className="size-4 mr-1" />
                YAML
              </Button>
            </div>

            <Button variant="outline" size="sm" onClick={handleValidate} disabled={isValidating}>
              {isValidating ? (
                <Loader2 className="size-4 mr-1 animate-spin" />
              ) : (
                <Check className="size-4 mr-1" />
              )}
              Validate
            </Button>

            <Button variant="outline" size="sm" onClick={handleRun} disabled={isRunning}>
              {isRunning ? (
                <Loader2 className="size-4 mr-1 animate-spin" />
              ) : (
                <Play className="size-4 mr-1" />
              )}
              Run
            </Button>

            <Button variant="outline" size="sm" onClick={handleExport}>
              <Download className="size-4 mr-1" />
              Export
            </Button>

            <Button onClick={handleSave} disabled={isUpdating}>
              {isUpdating ? (
                <Loader2 className="size-4 mr-1 animate-spin" />
              ) : (
                <Save className="size-4 mr-1" />
              )}
              Save
            </Button>

            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button variant="destructive" size="icon">
                  <Trash2 className="size-4" />
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Delete Flow?</AlertDialogTitle>
                  <AlertDialogDescription>
                    This will permanently delete &quot;{flow.name}&quot;. This action cannot be
                    undone.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <AlertDialogAction onClick={handleDelete}>Delete</AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </div>
        </div>

        {/* Validation Results */}
        {validationResult && !validationResult.valid && (
          <div className="px-4 pb-3">
            <div className="bg-destructive/10 text-destructive rounded-lg p-3 text-sm">
              <div className="flex items-center gap-2 font-medium">
                <AlertCircle className="size-4" />
                Validation Errors
              </div>
              <ul className="mt-2 ml-6 list-disc">
                {validationResult.errors.map((error, i) => (
                  <li key={i}>{error}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {activeTab === "visual" ? (
          <>
            {/* Node Palette Sidebar */}
            <div
              className={`border-r bg-background transition-all duration-300 ${
                isPaletteOpen ? "w-64" : "w-0"
              } overflow-hidden`}
            >
              <NodePalette />
            </div>

            {/* Toggle Palette Button */}
            <Button
              variant="ghost"
              size="icon"
              className="absolute left-0 top-1/2 -translate-y-1/2 z-10 rounded-l-none border border-l-0"
              onClick={() => setIsPaletteOpen(!isPaletteOpen)}
              style={{ left: isPaletteOpen ? "256px" : "0px" }}
            >
              {isPaletteOpen ? (
                <ChevronLeft className="size-4" />
              ) : (
                <ChevronRight className="size-4" />
              )}
            </Button>

            {/* Flow Canvas */}
            <div className="flex-1 relative">
              <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onConnect={onConnect}
                onNodeClick={onNodeClick}
                onDragOver={onDragOver}
                onDrop={onDrop}
                nodeTypes={flowNodeTypes}
                fitView
                snapToGrid
                snapGrid={[15, 15]}
                defaultEdgeOptions={{
                  animated: true,
                  style: { stroke: "hsl(var(--primary))", strokeWidth: 2 },
                }}
              >
                <Controls />
                <MiniMap
                  nodeStrokeWidth={3}
                  zoomable
                  pannable
                  className="!bg-muted/50"
                />
                <Background gap={15} size={1} />

                <Panel position="bottom-center" className="mb-4">
                  <div className="bg-background/95 backdrop-blur border rounded-lg px-3 py-2 text-sm text-muted-foreground">
                    {nodes.length} nodes &bull; {edges.length} connections
                  </div>
                </Panel>
              </ReactFlow>
            </div>

            {/* Properties Panel */}
            <Sheet open={isPropertiesOpen} onOpenChange={setIsPropertiesOpen}>
              <SheetContent className="w-[400px] sm:w-[540px]">
                <SheetHeader>
                  <SheetTitle>Node Properties</SheetTitle>
                  <SheetDescription>
                    Configure the selected node&apos;s settings
                  </SheetDescription>
                </SheetHeader>
                {selectedNode && (
                  <NodePropertiesPanel
                    node={selectedNode}
                    onUpdate={(updates) => onNodeUpdate(selectedNode.id, updates)}
                    onDelete={onDeleteNode}
                  />
                )}
              </SheetContent>
            </Sheet>
          </>
        ) : (
          /* YAML Editor Tab */
          <div className="flex-1 flex">
            {/* Flow Details Form */}
            <div className="w-80 border-r p-4 overflow-auto">
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Flow Name</Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    rows={3}
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="flow_type">Flow Type</Label>
                  <Select
                    value={formData.flow_type}
                    onValueChange={(value) => setFormData({ ...formData, flow_type: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="crew">CrewAI Crew</SelectItem>
                      <SelectItem value="pipeline">Pipeline</SelectItem>
                      <SelectItem value="workflow">Workflow</SelectItem>
                      <SelectItem value="rag">RAG Pipeline</SelectItem>
                      <SelectItem value="prefect">Prefect Flow</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="status">Status</Label>
                  <Select
                    value={formData.status}
                    onValueChange={(value) => setFormData({ ...formData, status: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="draft">Draft</SelectItem>
                      <SelectItem value="active">Active</SelectItem>
                      <SelectItem value="paused">Paused</SelectItem>
                      <SelectItem value="archived">Archived</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="tags">Tags</Label>
                  <Input
                    id="tags"
                    placeholder="tag1, tag2, tag3"
                    value={formData.tags}
                    onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                  />
                </div>
              </div>
            </div>

            {/* YAML Editor */}
            <div className="flex-1 p-4">
              <Label htmlFor="yaml" className="mb-2 block">
                Flow Definition (YAML)
              </Label>
              <CodeEditor
                value={formData.flow_yaml}
                onChange={(value) => setFormData({ ...formData, flow_yaml: value })}
                language="yaml"
                height="calc(100vh - 200px)"
              />
            </div>
          </div>
        )}
      </div>
      <div className="px-4 pb-6">
        <TestingSection
          resourceType="flow"
          resourceId={flow.id}
          resourceName={flow.name}
          defaultCode={`# Validate flow outputs\nresult = {\n    \"flow_id\": \"${flow.id}\",\n    \"status\": \"ok\",\n}\n`}
        />
      </div>
    </div>
  );
}

// Main page component with ReactFlowProvider
export default function FlowEditorPage() {
  return (
    <ReactFlowProvider>
      <FlowEditorInner />
    </ReactFlowProvider>
  );
}
