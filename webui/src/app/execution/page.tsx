"use client";

import * as React from "react";
import {
  Play,
  RefreshCw,
  Clock,
  CheckCircle2,
  XCircle,
  Loader2,
  Terminal,
  ChevronDown,
  ChevronRight,
} from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { CodeEditor } from "@/components/code-editor";
import { apiFetch } from "@/lib/api";
import { toast } from "sonner";

interface ScriptRun {
  id: string;
  status: "running" | "completed" | "failed" | "pending";
  language: string;
  started_at: string;
  duration_ms?: number;
  output?: string;
  error?: string;
}

type SupportedLanguage = "python" | "bash" | "javascript";

const STATUS_CONFIG: Record<
  ScriptRun["status"],
  { icon: React.ElementType; variant: "default" | "secondary" | "destructive" | "outline"; spin?: boolean }
> = {
  running: { icon: Loader2, variant: "default", spin: true },
  completed: { icon: CheckCircle2, variant: "secondary" },
  failed: { icon: XCircle, variant: "destructive" },
  pending: { icon: Clock, variant: "outline" },
};

function StatusBadge({ status }: { status: ScriptRun["status"] }) {
  const cfg = STATUS_CONFIG[status];
  const Icon = cfg.icon;
  return (
    <Badge variant={cfg.variant} className="gap-1">
      <Icon className={`size-3 ${cfg.spin ? "animate-spin" : ""}`} />
      {status}
    </Badge>
  );
}

function formatDuration(ms?: number): string {
  if (ms == null) return "—";
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(1)}s`;
}

function formatTime(iso: string): string {
  try {
    return new Date(iso).toLocaleTimeString();
  } catch {
    return iso;
  }
}

export default function ExecutionPage() {
  const [code, setCode] = React.useState("print('Hello, world!')");
  const [language, setLanguage] = React.useState<SupportedLanguage>("python");
  const [runs, setRuns] = React.useState<ScriptRun[]>([]);
  const [expandedRunId, setExpandedRunId] = React.useState<string | null>(null);
  const [expandedRunDetail, setExpandedRunDetail] = React.useState<ScriptRun | null>(null);
  const [loadingRuns, setLoadingRuns] = React.useState(true);
  const [submitting, setSubmitting] = React.useState(false);

  const hasRunningJob = runs.some((r) => r.status === "running" || r.status === "pending");

  const loadRuns = React.useCallback(async () => {
    try {
      const data = await apiFetch<{ runs: ScriptRun[] }>("/api/v1/execution/runs");
      setRuns(data.runs ?? []);
    } catch {
      toast.error("Failed to load run history");
    } finally {
      setLoadingRuns(false);
    }
  }, []);

  React.useEffect(() => {
    loadRuns();
  }, [loadRuns]);

  React.useEffect(() => {
    if (!hasRunningJob) return;
    const interval = setInterval(loadRuns, 3000);
    return () => clearInterval(interval);
  }, [hasRunningJob, loadRuns]);

  const handleRun = async () => {
    setSubmitting(true);
    try {
      const result = await apiFetch<{ run_id: string }>("/api/v1/execution/scripts/run", {
        method: "POST",
        body: JSON.stringify({ code, language }),
      });
      toast.success(`Script submitted — run ${result.run_id.slice(0, 8)}…`);
      await loadRuns();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to run script");
    } finally {
      setSubmitting(false);
    }
  };

  const handleExpand = async (runId: string) => {
    if (expandedRunId === runId) {
      setExpandedRunId(null);
      setExpandedRunDetail(null);
      return;
    }
    setExpandedRunId(runId);
    setExpandedRunDetail(null);
    try {
      const detail = await apiFetch<ScriptRun>(`/api/v1/execution/runs/${runId}`);
      setExpandedRunDetail(detail);
    } catch {
      toast.error("Failed to load run details");
      setExpandedRunId(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Script Execution</h1>
          <p className="text-muted-foreground">
            Run scripts and review execution history
          </p>
        </div>
        <Button variant="outline" onClick={() => { setLoadingRuns(true); loadRuns(); }}>
          <RefreshCw className="size-4 mr-2" />
          Refresh
        </Button>
      </div>

      <Tabs defaultValue="runner" className="space-y-4">
        <TabsList>
          <TabsTrigger value="runner">
            <Play className="size-3.5 mr-1.5" />
            Runner
          </TabsTrigger>
          <TabsTrigger value="history">
            <Clock className="size-3.5 mr-1.5" />
            History
          </TabsTrigger>
        </TabsList>

        {/* Runner Tab */}
        <TabsContent value="runner" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Terminal className="size-5" />
                  Script Runner
                </CardTitle>
                <div className="flex items-center gap-2">
                  <Select value={language} onValueChange={(v) => setLanguage(v as SupportedLanguage)}>
                    <SelectTrigger className="w-36">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="python">Python</SelectItem>
                      <SelectItem value="bash">Bash</SelectItem>
                      <SelectItem value="javascript">JavaScript</SelectItem>
                    </SelectContent>
                  </Select>
                  <Button onClick={handleRun} disabled={submitting || !code.trim()}>
                    {submitting ? (
                      <Loader2 className="size-4 mr-2 animate-spin" />
                    ) : (
                      <Play className="size-4 mr-2" />
                    )}
                    Run
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <CodeEditor
                value={code}
                onChange={setCode}
                language={language}
                height={320}
              />
            </CardContent>
          </Card>
        </TabsContent>

        {/* History Tab */}
        <TabsContent value="history" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="size-5" />
                Run History
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loadingRuns ? (
                <div className="space-y-3">
                  {[1, 2, 3].map((i) => (
                    <Skeleton key={i} className="h-12 w-full rounded-lg" />
                  ))}
                </div>
              ) : runs.length === 0 ? (
                <div className="py-12 text-center">
                  <Terminal className="size-12 mx-auto mb-4 opacity-50" />
                  <h3 className="text-lg font-semibold mb-2">No executions yet</h3>
                  <p className="text-muted-foreground">
                    Run a script to see its execution history here
                  </p>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-8" />
                      <TableHead>Run ID</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Language</TableHead>
                      <TableHead>Started</TableHead>
                      <TableHead>Duration</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {runs.map((run) => (
                      <React.Fragment key={run.id}>
                        <TableRow
                          className="cursor-pointer"
                          onClick={() => handleExpand(run.id)}
                        >
                          <TableCell>
                            {expandedRunId === run.id ? (
                              <ChevronDown className="size-4 text-muted-foreground" />
                            ) : (
                              <ChevronRight className="size-4 text-muted-foreground" />
                            )}
                          </TableCell>
                          <TableCell className="font-mono text-xs">
                            {run.id.slice(0, 12)}…
                          </TableCell>
                          <TableCell>
                            <StatusBadge status={run.status} />
                          </TableCell>
                          <TableCell>
                            <Badge variant="outline">{run.language}</Badge>
                          </TableCell>
                          <TableCell className="text-muted-foreground text-sm">
                            {formatTime(run.started_at)}
                          </TableCell>
                          <TableCell className="text-muted-foreground text-sm">
                            {formatDuration(run.duration_ms)}
                          </TableCell>
                        </TableRow>

                        {expandedRunId === run.id && (
                          <TableRow>
                            <TableCell colSpan={6} className="bg-muted/30 p-0">
                              <div className="p-4">
                                {!expandedRunDetail ? (
                                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                    <Loader2 className="size-4 animate-spin" />
                                    Loading output…
                                  </div>
                                ) : (
                                  <div className="space-y-2">
                                    {expandedRunDetail.output && (
                                      <div>
                                        <p className="text-xs font-medium mb-1">Output</p>
                                        <pre className="p-3 bg-background rounded-md border text-xs font-mono whitespace-pre-wrap max-h-64 overflow-y-auto">
                                          {expandedRunDetail.output}
                                        </pre>
                                      </div>
                                    )}
                                    {expandedRunDetail.error && (
                                      <div>
                                        <p className="text-xs font-medium text-destructive mb-1">Error</p>
                                        <pre className="p-3 bg-destructive/10 rounded-md border border-destructive/30 text-xs font-mono whitespace-pre-wrap max-h-64 overflow-y-auto text-destructive">
                                          {expandedRunDetail.error}
                                        </pre>
                                      </div>
                                    )}
                                    {!expandedRunDetail.output && !expandedRunDetail.error && (
                                      <p className="text-sm text-muted-foreground italic">
                                        No output available
                                      </p>
                                    )}
                                  </div>
                                )}
                              </div>
                            </TableCell>
                          </TableRow>
                        )}
                      </React.Fragment>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
