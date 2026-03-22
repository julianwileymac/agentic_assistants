'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Play,
  RefreshCw,
  CheckCircle2,
  XCircle,
  Loader2,
  Clock,
  Activity,
  Box,
  Calendar,
  ExternalLink,
  Zap,
  BarChart3,
} from 'lucide-react';
import { cn } from '@/lib/utils';

// Types
interface DagsterHealth {
  status: string;
  dagster_available: boolean;
  webserver_url: string | null;
  version: string | null;
}

interface JobInfo {
  name: string;
  description: string | null;
  tags: Record<string, string>;
}

interface AssetInfo {
  name: string;
  key: string;
  description: string | null;
  group_name: string | null;
}

interface ScheduleInfo {
  name: string;
  cron_schedule: string;
  job_name: string | null;
  status: string;
  description: string | null;
}

interface RunInfo {
  run_id: string;
  job_name: string;
  status: string;
  start_time: string | null;
  end_time: string | null;
  duration_seconds: number | null;
  tags: Record<string, string>;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

async function safeFetch<T>(url: string, fallback: T, options?: RequestInit): Promise<T> {
  try {
    const res = await fetch(url, options);
    if (!res.ok) return fallback;
    const text = await res.text();
    return text ? JSON.parse(text) : fallback;
  } catch {
    return fallback;
  }
}

const HEALTH_FALLBACK: DagsterHealth = { status: 'unavailable', dagster_available: false, webserver_url: null, version: null };

async function fetchHealth(): Promise<DagsterHealth> {
  return safeFetch(`${API_BASE}/api/v1/dagster/health`, HEALTH_FALLBACK);
}

async function fetchJobs(): Promise<JobInfo[]> {
  return safeFetch(`${API_BASE}/api/v1/dagster/jobs`, []);
}

async function fetchAssets(): Promise<AssetInfo[]> {
  return safeFetch(`${API_BASE}/api/v1/dagster/assets`, []);
}

async function fetchSchedules(): Promise<ScheduleInfo[]> {
  return safeFetch(`${API_BASE}/api/v1/dagster/schedules`, []);
}

async function fetchRuns(): Promise<RunInfo[]> {
  return safeFetch(`${API_BASE}/api/v1/dagster/runs?limit=20`, []);
}

async function launchJob(name: string, runConfig: Record<string, unknown> = {}): Promise<RunInfo | null> {
  return safeFetch(`${API_BASE}/api/v1/dagster/jobs/${name}/run`, null, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ run_config: runConfig }),
  });
}

// Status badge component
function StatusBadge({ status }: { status: string }) {
  const config: Record<string, { color: string; icon: React.ReactNode }> = {
    SUCCESS: { color: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400', icon: <CheckCircle2 className="w-3 h-3" /> },
    FAILURE: { color: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400', icon: <XCircle className="w-3 h-3" /> },
    RUNNING: { color: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400', icon: <Loader2 className="w-3 h-3 animate-spin" /> },
    STARTING: { color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400', icon: <Loader2 className="w-3 h-3 animate-spin" /> },
    CANCELED: { color: 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400', icon: <XCircle className="w-3 h-3" /> },
    STOPPED: { color: 'bg-gray-100 text-gray-600 dark:bg-gray-900/30 dark:text-gray-400', icon: <Clock className="w-3 h-3" /> },
    healthy: { color: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400', icon: <CheckCircle2 className="w-3 h-3" /> },
    unavailable: { color: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400', icon: <XCircle className="w-3 h-3" /> },
  };

  const cfg = config[status] || { color: 'bg-gray-100 text-gray-800', icon: null };

  return (
    <span className={cn('inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium', cfg.color)}>
      {cfg.icon}
      {status}
    </span>
  );
}

export default function DagsterDashboard() {
  const [health, setHealth] = useState<DagsterHealth | null>(null);
  const [jobs, setJobs] = useState<JobInfo[]>([]);
  const [assets, setAssets] = useState<AssetInfo[]>([]);
  const [schedules, setSchedules] = useState<ScheduleInfo[]>([]);
  const [runs, setRuns] = useState<RunInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [launching, setLaunching] = useState<string | null>(null);

  const loadAll = useCallback(async () => {
    setLoading(true);
    const [h, j, a, s, r] = await Promise.all([
      fetchHealth(),
      fetchJobs(),
      fetchAssets(),
      fetchSchedules(),
      fetchRuns(),
    ]);
    setHealth(h);
    setJobs(j);
    setAssets(a);
    setSchedules(s);
    setRuns(r);
    setLoading(false);
  }, []);

  useEffect(() => { loadAll(); }, [loadAll]);

  const handleLaunchJob = async (name: string) => {
    setLaunching(name);
    try {
      await launchJob(name);
      // Refresh runs after short delay
      setTimeout(() => {
        fetchRuns().then(setRuns).catch(() => {});
      }, 1000);
    } finally {
      setLaunching(null);
    }
  };

  const successCount = runs.filter(r => r.status === 'SUCCESS').length;
  const failureCount = runs.filter(r => r.status === 'FAILURE').length;
  const runningCount = runs.filter(r => r.status === 'RUNNING' || r.status === 'STARTING').length;

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Dagster Orchestration</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Process scheduling, workflow orchestration, and asset management
          </p>
        </div>
        <div className="flex items-center gap-2">
          {health?.webserver_url && (
            <a
              href={health.webserver_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm border rounded-md hover:bg-accent transition-colors"
            >
              <ExternalLink className="w-4 h-4" />
              Dagster UI
            </a>
          )}
          <button
            onClick={loadAll}
            disabled={loading}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm border rounded-md hover:bg-accent transition-colors"
          >
            <RefreshCw className={cn('w-4 h-4', loading && 'animate-spin')} />
            Refresh
          </button>
        </div>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {/* Health */}
        <div className="border rounded-lg p-4 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-muted-foreground">Status</span>
            <Activity className="w-4 h-4 text-muted-foreground" />
          </div>
          <div className="flex items-center gap-2">
            {health && <StatusBadge status={health.status} />}
            {health?.version && <span className="text-xs text-muted-foreground">v{health.version}</span>}
          </div>
        </div>

        {/* Jobs */}
        <div className="border rounded-lg p-4 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-muted-foreground">Jobs</span>
            <Zap className="w-4 h-4 text-muted-foreground" />
          </div>
          <p className="text-2xl font-bold">{jobs.length}</p>
        </div>

        {/* Assets */}
        <div className="border rounded-lg p-4 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-muted-foreground">Assets</span>
            <Box className="w-4 h-4 text-muted-foreground" />
          </div>
          <p className="text-2xl font-bold">{assets.length}</p>
        </div>

        {/* Schedules */}
        <div className="border rounded-lg p-4 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-muted-foreground">Schedules</span>
            <Calendar className="w-4 h-4 text-muted-foreground" />
          </div>
          <p className="text-2xl font-bold">{schedules.length}</p>
        </div>

        {/* Recent Runs */}
        <div className="border rounded-lg p-4 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-muted-foreground">Runs</span>
            <BarChart3 className="w-4 h-4 text-muted-foreground" />
          </div>
          <div className="flex items-center gap-3 text-sm">
            <span className="text-green-600">{successCount} ok</span>
            <span className="text-red-600">{failureCount} err</span>
            <span className="text-blue-600">{runningCount} run</span>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Jobs Panel */}
        <div className="border rounded-lg">
          <div className="p-4 border-b">
            <h2 className="text-sm font-semibold">Jobs</h2>
          </div>
          <div className="divide-y max-h-80 overflow-y-auto">
            {jobs.length === 0 && (
              <div className="p-4 text-sm text-muted-foreground text-center">No jobs registered</div>
            )}
            {jobs.map(job => (
              <div key={job.name} className="p-3 flex items-center justify-between hover:bg-accent/50 transition-colors">
                <div>
                  <p className="text-sm font-medium">{job.name}</p>
                  {job.description && (
                    <p className="text-xs text-muted-foreground mt-0.5 line-clamp-1">{job.description}</p>
                  )}
                </div>
                <button
                  onClick={() => handleLaunchJob(job.name)}
                  disabled={launching === job.name}
                  className="inline-flex items-center gap-1 px-2 py-1 text-xs border rounded hover:bg-primary hover:text-primary-foreground transition-colors"
                >
                  {launching === job.name ? (
                    <Loader2 className="w-3 h-3 animate-spin" />
                  ) : (
                    <Play className="w-3 h-3" />
                  )}
                  Run
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Assets Panel */}
        <div className="border rounded-lg">
          <div className="p-4 border-b">
            <h2 className="text-sm font-semibold">Assets</h2>
          </div>
          <div className="divide-y max-h-80 overflow-y-auto">
            {assets.length === 0 && (
              <div className="p-4 text-sm text-muted-foreground text-center">No assets registered</div>
            )}
            {assets.map(asset => (
              <div key={asset.key} className="p-3 hover:bg-accent/50 transition-colors">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium">{asset.name}</p>
                  {asset.group_name && (
                    <span className="text-xs bg-secondary text-secondary-foreground px-1.5 py-0.5 rounded">
                      {asset.group_name}
                    </span>
                  )}
                </div>
                {asset.description && (
                  <p className="text-xs text-muted-foreground mt-0.5 line-clamp-1">{asset.description}</p>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Schedules Panel */}
        <div className="border rounded-lg">
          <div className="p-4 border-b">
            <h2 className="text-sm font-semibold">Schedules</h2>
          </div>
          <div className="divide-y max-h-80 overflow-y-auto">
            {schedules.length === 0 && (
              <div className="p-4 text-sm text-muted-foreground text-center">No schedules configured</div>
            )}
            {schedules.map(sched => (
              <div key={sched.name} className="p-3 hover:bg-accent/50 transition-colors">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium">{sched.name}</p>
                  <StatusBadge status={sched.status} />
                </div>
                <p className="text-xs text-muted-foreground mt-0.5">
                  <code className="bg-muted px-1 py-0.5 rounded">{sched.cron_schedule}</code>
                  {sched.job_name && <span className="ml-2">-&gt; {sched.job_name}</span>}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Run History */}
      <div className="border rounded-lg">
        <div className="p-4 border-b">
          <h2 className="text-sm font-semibold">Recent Runs</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/50">
                <th className="text-left p-3 font-medium">Run ID</th>
                <th className="text-left p-3 font-medium">Job</th>
                <th className="text-left p-3 font-medium">Status</th>
                <th className="text-left p-3 font-medium">Started</th>
                <th className="text-left p-3 font-medium">Duration</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {runs.length === 0 && (
                <tr>
                  <td colSpan={5} className="p-4 text-center text-muted-foreground">No runs yet</td>
                </tr>
              )}
              {runs.map(run => (
                <tr key={run.run_id} className="hover:bg-accent/50 transition-colors">
                  <td className="p-3">
                    <code className="text-xs bg-muted px-1.5 py-0.5 rounded">
                      {run.run_id.substring(0, 8)}
                    </code>
                  </td>
                  <td className="p-3 font-medium">{run.job_name}</td>
                  <td className="p-3"><StatusBadge status={run.status} /></td>
                  <td className="p-3 text-muted-foreground">
                    {run.start_time ? new Date(run.start_time).toLocaleString() : '-'}
                  </td>
                  <td className="p-3 text-muted-foreground">
                    {run.duration_seconds != null ? `${run.duration_seconds}s` : '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
