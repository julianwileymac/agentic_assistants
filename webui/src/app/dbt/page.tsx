'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Play,
  TestTube,
  RefreshCw,
  Loader2,
  CheckCircle2,
  XCircle,
  GitBranch,
  FileCode,
  Box,
  Clock,
  ChevronRight,
  Code2,
} from 'lucide-react';
import { cn } from '@/lib/utils';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

interface DbtModel {
  unique_id: string;
  name: string;
  schema: string;
  database: string;
  materialized: string;
  description: string;
  depends_on: string[];
  tags: string[];
  path: string;
  raw_sql?: string;
  compiled_sql?: string;
}

interface DbtRunResult {
  run_id: string;
  command: string;
  success: boolean;
  stdout: string;
  stderr: string;
  timestamp: string;
  select?: string;
}

interface LineageGraph {
  nodes: { id: string; name: string; type: string; materialized: string }[];
  edges: { source: string; target: string }[];
}

// API helpers
async function fetchModels(): Promise<DbtModel[]> {
  const res = await fetch(`${API_BASE}/api/v1/dbt/models`);
  const data = await res.json();
  return data.models || [];
}

async function fetchModel(name: string): Promise<DbtModel | null> {
  const res = await fetch(`${API_BASE}/api/v1/dbt/models/${name}`);
  if (!res.ok) return null;
  return res.json();
}

async function fetchLineage(): Promise<LineageGraph> {
  const res = await fetch(`${API_BASE}/api/v1/dbt/lineage`);
  return res.json();
}

async function runDbt(select?: string, fullRefresh = false): Promise<DbtRunResult> {
  const res = await fetch(`${API_BASE}/api/v1/dbt/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ select, full_refresh: fullRefresh }),
  });
  return res.json();
}

async function testDbt(select?: string): Promise<DbtRunResult> {
  const res = await fetch(`${API_BASE}/api/v1/dbt/test`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ select }),
  });
  return res.json();
}

function MaterializedBadge({ type }: { type: string }) {
  const colors: Record<string, string> = {
    table: 'bg-emerald-500/10 text-emerald-400',
    view: 'bg-blue-500/10 text-blue-400',
    incremental: 'bg-amber-500/10 text-amber-400',
    ephemeral: 'bg-purple-500/10 text-purple-400',
  };
  return (
    <span className={cn('rounded px-1.5 py-0.5 text-xs font-medium', colors[type] || 'bg-zinc-800 text-zinc-400')}>
      {type}
    </span>
  );
}

function RunResultPanel({ result }: { result: DbtRunResult | null }) {
  if (!result) return null;

  return (
    <div className="rounded-lg border border-zinc-800 bg-zinc-900/50">
      <div className="flex items-center justify-between border-b border-zinc-800 px-4 py-2">
        <div className="flex items-center gap-2">
          {result.success ? (
            <CheckCircle2 className="h-4 w-4 text-emerald-400" />
          ) : (
            <XCircle className="h-4 w-4 text-red-400" />
          )}
          <span className="text-sm font-medium text-zinc-200">
            dbt {result.command} {result.select ? `--select ${result.select}` : ''}
          </span>
        </div>
        <span className="text-xs text-zinc-500">{result.timestamp}</span>
      </div>
      <pre className="max-h-64 overflow-auto p-4 font-mono text-xs text-zinc-400">
        {result.stdout || result.stderr || 'No output'}
      </pre>
    </div>
  );
}

export default function DbtPage() {
  const [models, setModels] = useState<DbtModel[]>([]);
  const [lineage, setLineage] = useState<LineageGraph>({ nodes: [], edges: [] });
  const [selectedModel, setSelectedModel] = useState<DbtModel | null>(null);
  const [lastRun, setLastRun] = useState<DbtRunResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState(false);
  const [activeTab, setActiveTab] = useState<'models' | 'dag' | 'output'>('models');

  const loadModels = useCallback(async () => {
    setLoading(true);
    try {
      const [m, l] = await Promise.all([fetchModels(), fetchLineage()]);
      setModels(m);
      setLineage(l);
    } catch {
      setModels([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const selectModel = useCallback(async (name: string) => {
    const detail = await fetchModel(name);
    setSelectedModel(detail);
  }, []);

  const handleRun = useCallback(async (select?: string) => {
    setRunning(true);
    try {
      const result = await runDbt(select);
      setLastRun(result);
      setActiveTab('output');
    } finally {
      setRunning(false);
    }
  }, []);

  const handleTest = useCallback(async (select?: string) => {
    setRunning(true);
    try {
      const result = await testDbt(select);
      setLastRun(result);
      setActiveTab('output');
    } finally {
      setRunning(false);
    }
  }, []);

  useEffect(() => { loadModels(); }, [loadModels]);

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-zinc-100">dbt Models</h1>
          <p className="mt-1 text-sm text-zinc-500">
            Manage data transformations and models with dbt
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => handleRun()}
            disabled={running}
            className="inline-flex items-center gap-1.5 rounded-md bg-emerald-600 px-3 py-1.5 text-sm text-white hover:bg-emerald-500 disabled:opacity-50"
          >
            {running ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Play className="h-3.5 w-3.5" />}
            Run All
          </button>
          <button
            onClick={() => handleTest()}
            disabled={running}
            className="inline-flex items-center gap-1.5 rounded-md border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-sm text-zinc-300 hover:bg-zinc-700 disabled:opacity-50"
          >
            <TestTube className="h-3.5 w-3.5" />
            Test All
          </button>
          <button
            onClick={loadModels}
            className="rounded-md border border-zinc-700 bg-zinc-800 p-1.5 text-zinc-400 hover:bg-zinc-700"
          >
            <RefreshCw className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-zinc-800">
        {([
          { id: 'models' as const, label: `Models (${models.length})`, icon: Box },
          { id: 'dag' as const, label: 'Dependency Graph', icon: GitBranch },
          { id: 'output' as const, label: 'Run Output', icon: Code2 },
        ]).map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              'flex items-center gap-1.5 border-b-2 px-3 py-2 text-sm font-medium transition-colors',
              activeTab === tab.id
                ? 'border-blue-500 text-blue-400'
                : 'border-transparent text-zinc-500 hover:text-zinc-300'
            )}
          >
            <tab.icon className="h-3.5 w-3.5" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Models tab */}
      {activeTab === 'models' && (
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Model list */}
          <div className="space-y-2 lg:col-span-1">
            {loading ? (
              <div className="flex justify-center py-8">
                <Loader2 className="h-5 w-5 animate-spin text-zinc-600" />
              </div>
            ) : models.length === 0 ? (
              <div className="flex flex-col items-center py-8 text-zinc-600">
                <FileCode className="mb-2 h-8 w-8 text-zinc-700" />
                <p className="text-sm">No dbt models found</p>
                <p className="mt-1 text-xs text-zinc-700">Run &apos;dbt compile&apos; to generate the manifest</p>
              </div>
            ) : (
              models.map((m) => (
                <button
                  key={m.unique_id}
                  onClick={() => selectModel(m.name)}
                  className={cn(
                    'flex w-full items-center gap-3 rounded-md border px-3 py-2.5 text-left transition-colors',
                    selectedModel?.name === m.name
                      ? 'border-blue-500/30 bg-blue-500/5'
                      : 'border-zinc-800 bg-zinc-900/50 hover:border-zinc-700'
                  )}
                >
                  <Box className="h-4 w-4 flex-shrink-0 text-zinc-500" />
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium text-zinc-200">{m.name}</p>
                    <p className="truncate text-xs text-zinc-600">{m.path}</p>
                  </div>
                  <MaterializedBadge type={m.materialized} />
                </button>
              ))
            )}
          </div>

          {/* Model detail */}
          <div className="lg:col-span-2">
            {!selectedModel ? (
              <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-zinc-800 py-16 text-zinc-600">
                <FileCode className="mb-3 h-10 w-10 text-zinc-700" />
                <p className="text-sm">Select a model to view its details</p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-4">
                  <div className="flex items-center justify-between">
                    <h2 className="text-lg font-semibold text-zinc-100">{selectedModel.name}</h2>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleRun(selectedModel.name)}
                        disabled={running}
                        className="inline-flex items-center gap-1 rounded-md bg-emerald-600 px-2 py-1 text-xs text-white hover:bg-emerald-500 disabled:opacity-50"
                      >
                        <Play className="h-3 w-3" /> Run
                      </button>
                      <button
                        onClick={() => handleTest(selectedModel.name)}
                        disabled={running}
                        className="inline-flex items-center gap-1 rounded-md border border-zinc-700 px-2 py-1 text-xs text-zinc-300 hover:bg-zinc-800 disabled:opacity-50"
                      >
                        <TestTube className="h-3 w-3" /> Test
                      </button>
                    </div>
                  </div>
                  <p className="mt-1 text-sm text-zinc-500">
                    {selectedModel.description || 'No description'}
                  </p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    <MaterializedBadge type={selectedModel.materialized} />
                    {selectedModel.tags?.map((t) => (
                      <span key={t} className="rounded bg-zinc-800 px-1.5 py-0.5 text-xs text-zinc-400">
                        {t}
                      </span>
                    ))}
                  </div>
                </div>

                {/* SQL */}
                {(selectedModel.raw_sql || selectedModel.compiled_sql) && (
                  <div className="rounded-lg border border-zinc-800 bg-zinc-900/50">
                    <div className="border-b border-zinc-800 px-4 py-2 text-xs font-medium text-zinc-500">
                      SQL
                    </div>
                    <pre className="max-h-80 overflow-auto p-4 font-mono text-xs text-zinc-400">
                      {selectedModel.compiled_sql || selectedModel.raw_sql}
                    </pre>
                  </div>
                )}

                {/* Dependencies */}
                {selectedModel.depends_on?.length > 0 && (
                  <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-4">
                    <h3 className="mb-2 text-xs font-medium text-zinc-500">Depends On</h3>
                    <div className="flex flex-wrap gap-1.5">
                      {selectedModel.depends_on.map((dep) => (
                        <span key={dep} className="rounded bg-zinc-800 px-2 py-1 text-xs text-zinc-400">
                          {dep.split('.').pop()}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* DAG tab */}
      {activeTab === 'dag' && (
        <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-6">
          {lineage.nodes.length === 0 ? (
            <p className="text-center text-sm text-zinc-600">
              No lineage data available. Run &apos;dbt compile&apos; to generate the model graph.
            </p>
          ) : (
            <div className="space-y-4">
              <p className="text-xs text-zinc-500">
                {lineage.nodes.length} nodes, {lineage.edges.length} edges
              </p>
              <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
                {lineage.nodes.map((node) => (
                  <div
                    key={node.id}
                    className="rounded-md border border-zinc-800 bg-zinc-900 px-3 py-2"
                  >
                    <div className="flex items-center gap-2">
                      <Box className="h-3.5 w-3.5 text-zinc-500" />
                      <span className="truncate text-sm text-zinc-300">{node.name}</span>
                    </div>
                    <div className="mt-1 flex gap-2">
                      <span className="text-xs text-zinc-600">{node.type}</span>
                      {node.materialized && <MaterializedBadge type={node.materialized} />}
                    </div>
                    {/* Show edges */}
                    {lineage.edges
                      .filter((e) => e.target === node.id)
                      .map((e, i) => (
                        <div key={i} className="mt-1 flex items-center gap-1 text-xs text-zinc-600">
                          <ChevronRight className="h-3 w-3" />
                          {e.source.split('.').pop()}
                        </div>
                      ))}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Output tab */}
      {activeTab === 'output' && <RunResultPanel result={lastRun} />}
    </div>
  );
}
