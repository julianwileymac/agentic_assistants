'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Play,
  RefreshCw,
  CheckCircle2,
  XCircle,
  Loader2,
  Clock,
  ChevronRight,
  Calendar,
  Search,
  Filter,
  ToggleLeft,
  ToggleRight,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { getBackendUrl } from "@/lib/api-client";

const API_BASE = getBackendUrl();

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

// Types
interface JobInfo {
  name: string;
  description: string | null;
  tags: Record<string, string>;
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

// Status badge
function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    SUCCESS: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
    FAILURE: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
    RUNNING: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
    STARTING: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
    CANCELED: 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400',
    STOPPED: 'bg-gray-100 text-gray-600 dark:bg-gray-900/30 dark:text-gray-400',
    RUNNING_SCHED: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
  };

  const icons: Record<string, React.ReactNode> = {
    SUCCESS: <CheckCircle2 className="w-3 h-3" />,
    FAILURE: <XCircle className="w-3 h-3" />,
    RUNNING: <Loader2 className="w-3 h-3 animate-spin" />,
    STARTING: <Loader2 className="w-3 h-3 animate-spin" />,
  };

  return (
    <span className={cn('inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium', colors[status] || 'bg-gray-100 text-gray-800')}>
      {icons[status]}
      {status}
    </span>
  );
}

export default function DagsterJobsPage() {
  const [jobs, setJobs] = useState<JobInfo[]>([]);
  const [schedules, setSchedules] = useState<ScheduleInfo[]>([]);
  const [runs, setRuns] = useState<RunInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedJob, setSelectedJob] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [launching, setLaunching] = useState<string | null>(null);
  const [togglingSchedule, setTogglingSchedule] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    const [j, s, r] = await Promise.all([
      safeFetch(`${API_BASE}/api/v1/dagster/jobs`, []),
      safeFetch(`${API_BASE}/api/v1/dagster/schedules`, []),
      safeFetch(`${API_BASE}/api/v1/dagster/runs?limit=50`, []),
    ]);
    setJobs(j);
    setSchedules(s);
    setRuns(r);
    setLoading(false);
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  const handleLaunchJob = async (name: string) => {
    setLaunching(name);
    await safeFetch(`${API_BASE}/api/v1/dagster/jobs/${name}/run`, null, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ run_config: {} }),
    });
    setTimeout(loadData, 1500);
    setLaunching(null);
  };

  const handleToggleSchedule = async (name: string) => {
    setTogglingSchedule(name);
    await safeFetch(`${API_BASE}/api/v1/dagster/schedules/${name}/toggle`, null, {
      method: 'POST',
    });
    setTimeout(loadData, 500);
    setTogglingSchedule(null);
  };

  const filteredJobs = jobs.filter(j =>
    j.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (j.description || '').toLowerCase().includes(searchQuery.toLowerCase())
  );

  const jobRuns = selectedJob
    ? runs.filter(r => r.job_name === selectedJob)
    : runs;

  const getScheduleForJob = (jobName: string) =>
    schedules.find(s => s.job_name === jobName || s.name.includes(jobName));

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Dagster Jobs</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Browse, run, and manage jobs and schedules
          </p>
        </div>
        <button
          onClick={loadData}
          disabled={loading}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm border rounded-md hover:bg-accent transition-colors"
        >
          <RefreshCw className={cn('w-4 h-4', loading && 'animate-spin')} />
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Job List */}
        <div className="space-y-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input
              type="text"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              placeholder="Search jobs..."
              className="w-full pl-9 pr-4 py-2 text-sm border rounded-md bg-background"
            />
          </div>

          {/* Job cards */}
          <div className="border rounded-lg divide-y">
            {filteredJobs.length === 0 && (
              <div className="p-4 text-sm text-muted-foreground text-center">
                {loading ? 'Loading...' : 'No jobs found'}
              </div>
            )}
            {filteredJobs.map(job => {
              const schedule = getScheduleForJob(job.name);
              const lastRun = runs.find(r => r.job_name === job.name);
              const isSelected = selectedJob === job.name;

              return (
                <div
                  key={job.name}
                  onClick={() => setSelectedJob(isSelected ? null : job.name)}
                  className={cn(
                    'p-3 cursor-pointer transition-colors',
                    isSelected ? 'bg-accent' : 'hover:bg-accent/50'
                  )}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <ChevronRight className={cn(
                        'w-4 h-4 text-muted-foreground transition-transform',
                        isSelected && 'rotate-90'
                      )} />
                      <span className="text-sm font-medium">{job.name}</span>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleLaunchJob(job.name);
                      }}
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
                  {job.description && (
                    <p className="text-xs text-muted-foreground mt-1 ml-6 line-clamp-1">
                      {job.description}
                    </p>
                  )}
                  <div className="flex items-center gap-3 mt-1.5 ml-6 text-xs text-muted-foreground">
                    {schedule && (
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        <code>{schedule.cron_schedule}</code>
                      </span>
                    )}
                    {lastRun && (
                      <StatusBadge status={lastRun.status} />
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Schedules */}
          <div className="border rounded-lg">
            <div className="p-3 border-b">
              <h3 className="text-sm font-semibold flex items-center gap-2">
                <Calendar className="w-4 h-4" />
                Schedules
              </h3>
            </div>
            <div className="divide-y">
              {schedules.length === 0 && (
                <div className="p-3 text-sm text-muted-foreground text-center">No schedules</div>
              )}
              {schedules.map(sched => (
                <div key={sched.name} className="p-3 flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium">{sched.name}</p>
                    <p className="text-xs text-muted-foreground">
                      <code>{sched.cron_schedule}</code>
                    </p>
                  </div>
                  <button
                    onClick={() => handleToggleSchedule(sched.name)}
                    disabled={togglingSchedule === sched.name}
                    className="text-muted-foreground hover:text-foreground transition-colors"
                  >
                    {togglingSchedule === sched.name ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : sched.status === 'RUNNING' ? (
                      <ToggleRight className="w-5 h-5 text-green-600" />
                    ) : (
                      <ToggleLeft className="w-5 h-5" />
                    )}
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right: Run History */}
        <div className="lg:col-span-2">
          <div className="border rounded-lg">
            <div className="p-4 border-b flex items-center justify-between">
              <h2 className="text-sm font-semibold">
                {selectedJob ? `Runs: ${selectedJob}` : 'All Runs'}
              </h2>
              {selectedJob && (
                <button
                  onClick={() => setSelectedJob(null)}
                  className="text-xs text-muted-foreground hover:text-foreground"
                >
                  Show all
                </button>
              )}
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
                  {jobRuns.length === 0 && (
                    <tr>
                      <td colSpan={5} className="p-8 text-center text-muted-foreground">
                        {loading ? (
                          <Loader2 className="w-5 h-5 animate-spin mx-auto" />
                        ) : (
                          'No runs found'
                        )}
                      </td>
                    </tr>
                  )}
                  {jobRuns.map(run => (
                    <tr key={run.run_id} className="hover:bg-accent/50 transition-colors">
                      <td className="p-3">
                        <code className="text-xs bg-muted px-1.5 py-0.5 rounded">
                          {run.run_id.substring(0, 8)}
                        </code>
                      </td>
                      <td className="p-3 font-medium">{run.job_name}</td>
                      <td className="p-3"><StatusBadge status={run.status} /></td>
                      <td className="p-3 text-muted-foreground text-xs">
                        {run.start_time
                          ? new Date(run.start_time).toLocaleString()
                          : '-'}
                      </td>
                      <td className="p-3 text-muted-foreground">
                        {run.duration_seconds != null
                          ? `${run.duration_seconds}s`
                          : run.status === 'RUNNING' || run.status === 'STARTING'
                            ? <Loader2 className="w-3 h-3 animate-spin" />
                            : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
