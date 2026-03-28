'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { 
  Play, 
  RefreshCw, 
  GitBranch,
  Clock,
  CheckCircle2,
  XCircle,
  Loader2,
  Search,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { TestingSection } from '@/components/testing/testing-section';
import { getBackendUrl } from "@/lib/api-client";
import { ReactFlow, Background, Controls, MiniMap } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

function ReactFlowInner({ nodes, edges }: { nodes: any[]; edges: any[] }) {
  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      fitView
      proOptions={{ hideAttribution: true }}
      style={{ background: 'transparent' }}
    >
      <Background color="#1e293b" gap={16} />
      <Controls showInteractive={false} />
      <MiniMap style={{ background: '#0f172a' }} />
    </ReactFlow>
  );
}

// Types
interface PipelineNode {
  name: string;
  inputs: string[];
  outputs: string[];
  tags: string[];
}

interface PipelineInfo {
  name: string;
  node_count: number;
  inputs: string[];
  outputs: string[];
  nodes: PipelineNode[];
}

interface PipelineRunStatus {
  run_id: string;
  pipeline_name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  nodes_completed: number;
  nodes_total: number;
  errors: string[];
  started_at: string | null;
  completed_at: string | null;
}

const API_BASE = getBackendUrl();

// API functions
async function fetchPipelines(): Promise<string[]> {
  const res = await fetch(`${API_BASE}/api/v1/pipelines`);
  const data = await res.json();
  return data.pipelines || [];
}

async function fetchPipelineInfo(name: string): Promise<PipelineInfo> {
  const res = await fetch(`${API_BASE}/api/v1/pipelines/${name}`);
  return res.json();
}

async function runPipeline(
  name: string, 
  options: { runner?: string; tags?: string[]; async_run?: boolean }
): Promise<{ run_id: string; success: boolean }> {
  const res = await fetch(`${API_BASE}/api/v1/pipelines/${name}/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(options),
  });
  return res.json();
}

async function fetchRunStatus(name: string, runId: string): Promise<PipelineRunStatus> {
  const res = await fetch(`${API_BASE}/api/v1/pipelines/${name}/status/${runId}`);
  return res.json();
}

// Pipeline DAG Visualization Component
function PipelineDAG({ pipeline }: { pipeline: PipelineInfo }) {
  const rfNodes = React.useMemo(() => {
    const nodes: Array<{ id: string; data: { label: string }; position: { x: number; y: number }; style?: React.CSSProperties }> = [];
    const ySpacing = 80;

    pipeline.inputs.forEach((input, i) => {
      nodes.push({
        id: `input-${input}`,
        data: { label: `[Input] ${input}` },
        position: { x: 0, y: i * ySpacing },
        style: { background: 'rgba(14,165,233,0.15)', border: '1px solid rgba(14,165,233,0.4)', color: '#38bdf8', fontSize: 12, borderRadius: 8 },
      });
    });

    pipeline.nodes.forEach((node, i) => {
      nodes.push({
        id: `node-${node.name}`,
        data: { label: node.name },
        position: { x: 300, y: i * ySpacing },
        style: { background: 'rgba(16,185,129,0.15)', border: '1px solid rgba(16,185,129,0.4)', color: '#34d399', fontSize: 12, borderRadius: 8 },
      });
    });

    pipeline.outputs.forEach((output, i) => {
      nodes.push({
        id: `output-${output}`,
        data: { label: `[Output] ${output}` },
        position: { x: 600, y: i * ySpacing },
        style: { background: 'rgba(245,158,11,0.15)', border: '1px solid rgba(245,158,11,0.4)', color: '#fbbf24', fontSize: 12, borderRadius: 8 },
      });
    });

    return nodes;
  }, [pipeline]);

  const rfEdges = React.useMemo(() => {
    const edges: Array<{ id: string; source: string; target: string; animated?: boolean; style?: React.CSSProperties }> = [];
    const edgeStyle = { stroke: '#475569' };

    pipeline.nodes.forEach((node) => {
      node.inputs.forEach((inp) => {
        const sourceId = pipeline.inputs.includes(inp) ? `input-${inp}` : `node-${inp}`;
        edges.push({ id: `e-${sourceId}-${node.name}`, source: sourceId, target: `node-${node.name}`, animated: true, style: edgeStyle });
      });
      node.outputs.forEach((out) => {
        const targetId = pipeline.outputs.includes(out) ? `output-${out}` : `node-${out}`;
        edges.push({ id: `e-${node.name}-${targetId}`, source: `node-${node.name}`, target: targetId, style: edgeStyle });
      });
    });

    return edges;
  }, [pipeline]);

  return (
    <div className="relative bg-slate-950 rounded-xl overflow-hidden border border-slate-800" style={{ height: 350 }}>
      <ReactFlowInner nodes={rfNodes} edges={rfEdges} />
      </div>
    </div>
  );
}

// Pipeline Card Component
function PipelineCard({ 
  name, 
  isSelected, 
  onClick,
  onRun,
}: { 
  name: string;
  isSelected: boolean;
  onClick: () => void;
  onRun: () => void;
}) {
  const [info, setInfo] = useState<PipelineInfo | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPipelineInfo(name)
      .then(setInfo)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [name]);

  return (
    <div
      className={cn(
        "p-4 rounded-xl border cursor-pointer transition-all",
        isSelected
          ? "bg-slate-800/50 border-emerald-500/50"
          : "bg-slate-900/50 border-slate-800 hover:border-slate-700"
      )}
      onClick={onClick}
    >
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2">
            <GitBranch className="w-4 h-4 text-emerald-400" />
            <h3 className="font-semibold text-white">{name}</h3>
          </div>
          {loading ? (
            <div className="mt-2 text-sm text-slate-500">Loading...</div>
          ) : info ? (
            <div className="mt-2 space-y-1 text-sm text-slate-400">
              <div>{info.node_count} nodes</div>
              <div className="text-xs text-slate-500">
                {info.inputs.length} inputs → {info.outputs.length} outputs
              </div>
            </div>
          ) : null}
        </div>
        <button
          className="p-2 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 transition-colors"
          onClick={(e) => {
            e.stopPropagation();
            onRun();
          }}
        >
          <Play className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}

// Run Status Component
function RunStatusBadge({ status }: { status: PipelineRunStatus['status'] }) {
  const statusConfig = {
    pending: { icon: Clock, color: 'text-slate-400', bg: 'bg-slate-500/10' },
    running: { icon: Loader2, color: 'text-blue-400', bg: 'bg-blue-500/10', spin: true },
    completed: { icon: CheckCircle2, color: 'text-emerald-400', bg: 'bg-emerald-500/10' },
    failed: { icon: XCircle, color: 'text-red-400', bg: 'bg-red-500/10' },
  };

  const config = statusConfig[status];
  const Icon = config.icon;

  return (
    <span className={cn('inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-sm', config.bg, config.color)}>
      <Icon className={cn('w-4 h-4', config.spin && 'animate-spin')} />
      {status}
    </span>
  );
}

// Main Pipelines Page
export default function PipelinesPage() {
  const [pipelines, setPipelines] = useState<string[]>([]);
  const [selectedPipeline, setSelectedPipeline] = useState<string | null>(null);
  const [pipelineInfo, setPipelineInfo] = useState<PipelineInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [currentRun, setCurrentRun] = useState<PipelineRunStatus | null>(null);
  const [runHistory, setRunHistory] = useState<PipelineRunStatus[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [runnerType, setRunnerType] = useState<'sequential' | 'parallel' | 'thread'>('sequential');

  // Fetch pipelines on mount
  useEffect(() => {
    fetchPipelines()
      .then(setPipelines)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  // Fetch pipeline info when selection changes
  useEffect(() => {
    if (selectedPipeline) {
      fetchPipelineInfo(selectedPipeline)
        .then(setPipelineInfo)
        .catch(console.error);
    }
  }, [selectedPipeline]);

  // Poll for run status
  useEffect(() => {
    if (!currentRun || !selectedPipeline) return;
    if (currentRun.status === 'completed' || currentRun.status === 'failed') return;

    const interval = setInterval(() => {
      fetchRunStatus(selectedPipeline, currentRun.run_id)
        .then(setCurrentRun)
        .catch(console.error);
    }, 1000);

    return () => clearInterval(interval);
  }, [currentRun, selectedPipeline]);

  // Handle run pipeline
  const handleRun = async (name: string) => {
    setRunning(true);
    setCurrentRun(null);

    try {
      const result = await runPipeline(name, { 
        runner: runnerType, 
        async_run: true 
      });
      
      setCurrentRun({
        run_id: result.run_id,
        pipeline_name: name,
        status: 'pending',
        progress: 0,
        nodes_completed: 0,
        nodes_total: pipelineInfo?.node_count || 0,
        errors: [],
        started_at: new Date().toISOString(),
        completed_at: null,
      });
    } catch (error) {
      console.error('Failed to run pipeline:', error);
    } finally {
      setRunning(false);
    }
  };

  // Filter pipelines by search
  const filteredPipelines = pipelines.filter((name) =>
    name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white flex items-center gap-3">
                <GitBranch className="w-7 h-7 text-emerald-400" />
                Pipelines
              </h1>
              <p className="text-slate-400 text-sm mt-1">
                Kedro-inspired data pipelines and DAG execution
              </p>
            </div>

            <div className="flex items-center gap-4">
              {/* Runner Type Selector */}
              <select
                value={runnerType}
                onChange={(e) => setRunnerType(e.target.value as typeof runnerType)}
                className="px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-white focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
              >
                <option value="sequential">Sequential Runner</option>
                <option value="parallel">Parallel Runner</option>
                <option value="thread">Thread Runner</option>
              </select>

              <button
                onClick={() => {
                  setLoading(true);
                  fetchPipelines()
                    .then(setPipelines)
                    .catch(console.error)
                    .finally(() => setLoading(false));
                }}
                className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 transition-colors"
              >
                <RefreshCw className={cn("w-5 h-5", loading && "animate-spin")} />
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-12 gap-6">
          {/* Sidebar - Pipeline List */}
          <div className="col-span-4">
            <div className="bg-slate-900/50 rounded-xl border border-slate-800 overflow-hidden">
              {/* Search */}
              <div className="p-4 border-b border-slate-800">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                  <input
                    type="text"
                    placeholder="Search pipelines..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
                  />
                </div>
              </div>

              {/* Pipeline List */}
              <div className="p-4 space-y-3 max-h-[600px] overflow-y-auto">
                {loading ? (
                  <div className="text-center py-8 text-slate-500">
                    <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" />
                    Loading pipelines...
                  </div>
                ) : filteredPipelines.length === 0 ? (
                  <div className="text-center py-8 text-slate-500">
                    No pipelines registered.
                    <br />
                    <span className="text-xs">
                      Use pipeline_registry.register() to add pipelines.
                    </span>
                  </div>
                ) : (
                  filteredPipelines.map((name) => (
                    <PipelineCard
                      key={name}
                      name={name}
                      isSelected={selectedPipeline === name}
                      onClick={() => setSelectedPipeline(name)}
                      onRun={() => handleRun(name)}
                    />
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="col-span-8 space-y-6">
            {selectedPipeline && pipelineInfo ? (
              <>
                {/* Pipeline Header */}
                <div className="bg-slate-900/50 rounded-xl border border-slate-800 p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-xl font-bold text-white">{selectedPipeline}</h2>
                      <p className="text-slate-400 mt-1">
                        {pipelineInfo.node_count} nodes • {pipelineInfo.inputs.length} inputs • {pipelineInfo.outputs.length} outputs
                      </p>
                    </div>
                    <button
                      onClick={() => handleRun(selectedPipeline)}
                      disabled={running}
                      className={cn(
                        "px-4 py-2 rounded-lg font-medium flex items-center gap-2 transition-colors",
                        running
                          ? "bg-slate-700 text-slate-400 cursor-not-allowed"
                          : "bg-emerald-500 hover:bg-emerald-600 text-white"
                      )}
                    >
                      {running ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <Play className="w-4 h-4" />
                      )}
                      Run Pipeline
                    </button>
                  </div>

                  {/* Current Run Status */}
                  {currentRun && (
                    <div className="mt-4 p-4 bg-slate-800/50 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <RunStatusBadge status={currentRun.status} />
                          <span className="text-sm text-slate-400">
                            {currentRun.nodes_completed} / {currentRun.nodes_total} nodes
                          </span>
                        </div>
                        <span className="text-xs text-slate-500 font-mono">
                          {currentRun.run_id.slice(0, 8)}...
                        </span>
                      </div>

                      {/* Progress Bar */}
                      <div className="mt-3 h-2 bg-slate-700 rounded-full overflow-hidden">
                        <div
                          className={cn(
                            "h-full transition-all duration-500",
                            currentRun.status === 'completed' && "bg-emerald-500",
                            currentRun.status === 'failed' && "bg-red-500",
                            currentRun.status === 'running' && "bg-blue-500",
                            currentRun.status === 'pending' && "bg-slate-500"
                          )}
                          style={{ width: `${(currentRun.progress || 0) * 100}%` }}
                        />
                      </div>

                      {/* Errors */}
                      {currentRun.errors.length > 0 && (
                        <div className="mt-3 p-3 bg-red-500/10 border border-red-500/30 rounded text-sm text-red-400">
                          {currentRun.errors.map((err, i) => (
                            <div key={i}>{err}</div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* DAG Visualization */}
                <div className="bg-slate-900/50 rounded-xl border border-slate-800 p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">Pipeline DAG</h3>
                  <PipelineDAG pipeline={pipelineInfo} />
                </div>

                {/* Node List */}
                <div className="bg-slate-900/50 rounded-xl border border-slate-800 p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">Nodes</h3>
                  <div className="space-y-2">
                    {pipelineInfo.nodes.map((node, idx) => (
                      <div
                        key={node.name}
                        className="p-4 bg-slate-800/50 rounded-lg flex items-center justify-between"
                      >
                        <div>
                          <div className="font-medium text-white">{node.name}</div>
                          <div className="text-sm text-slate-400 mt-1">
                            <span className="text-sky-400">{node.inputs.join(', ')}</span>
                            {' → '}
                            <span className="text-amber-400">{node.outputs.join(', ')}</span>
                          </div>
                        </div>
                        <div className="flex gap-1">
                          {node.tags.map((tag) => (
                            <span
                              key={tag}
                              className="px-2 py-0.5 bg-slate-700 rounded text-xs text-slate-300"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            ) : (
              <div className="bg-slate-900/50 rounded-xl border border-slate-800 p-12 text-center">
                <GitBranch className="w-16 h-16 text-slate-700 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-slate-400">Select a Pipeline</h3>
                <p className="text-slate-500 mt-2 max-w-md mx-auto">
                  Choose a pipeline from the list to view its DAG structure,
                  nodes, and run execution.
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
      <div className="max-w-7xl mx-auto px-6 pb-10">
        <TestingSection
          resourceType="pipeline"
          resourceName="Pipeline"
          defaultCode={`# Pipeline test\nresult = {\n    "status": "ok",\n    "notes": "Validate pipeline execution",\n}\n`}
        />
      </div>
    </div>
  );
}
