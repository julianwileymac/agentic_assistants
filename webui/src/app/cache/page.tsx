"use client";

import * as React from "react";
import {
  Database,
  Search,
  Trash2,
  RefreshCw,
  Loader2,
  CheckCircle2,
  Clock,
  Workflow,
  Plus,
  BarChart3,
  Tag,
  ThumbsUp,
  Eye,
  AlertTriangle,
  XCircle,
  ArrowRight,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
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
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { toast } from "sonner";
import { apiFetch } from "@/lib/api";
import { getBackendUrl } from "@/lib/api-client";

interface CachedSolution {
  name: string;
  type: string;
  tags: string[];
  success_count: number;
  created_at: string;
  updated_at: string;
  description?: string;
  metadata?: Record<string, unknown>;
}

interface CacheWorkflow {
  id: string;
  name: string;
  status: "pending" | "running" | "completed" | "failed";
  steps: WorkflowStep[];
  created_at: string;
  updated_at: string;
}

interface WorkflowStep {
  name: string;
  status: "pending" | "running" | "completed" | "failed" | "skipped";
  order: number;
}

interface CacheStats {
  total_solutions: number;
  cache_hit_rate: number;
  active_workflows: number;
  total_hits: number;
  total_misses: number;
}

const stepStatusIcon: Record<string, React.ReactNode> = {
  pending: <Clock className="size-3.5 text-muted-foreground" />,
  running: <Loader2 className="size-3.5 text-blue-500 animate-spin" />,
  completed: <CheckCircle2 className="size-3.5 text-green-500" />,
  failed: <XCircle className="size-3.5 text-red-500" />,
  skipped: <ArrowRight className="size-3.5 text-muted-foreground" />,
};

export default function CachePage() {
  const [stats, setStats] = React.useState<CacheStats | null>(null);
  const [solutions, setSolutions] = React.useState<CachedSolution[]>([]);
  const [workflows, setWorkflows] = React.useState<CacheWorkflow[]>([]);
  const [loadingSolutions, setLoadingSolutions] = React.useState(true);
  const [loadingWorkflows, setLoadingWorkflows] = React.useState(true);
  const [loadingStats, setLoadingStats] = React.useState(true);
  const [searchQuery, setSearchQuery] = React.useState("");
  const [tagFilter, setTagFilter] = React.useState("all");
  const [clearing, setClearing] = React.useState(false);
  const [selectedSolution, setSelectedSolution] =
    React.useState<CachedSolution | null>(null);
  const [showNewWorkflow, setShowNewWorkflow] = React.useState(false);
  const [newWorkflowName, setNewWorkflowName] = React.useState("");
  const [newWorkflowSteps, setNewWorkflowSteps] = React.useState("");
  const [creatingWorkflow, setCreatingWorkflow] = React.useState(false);

  const loadStats = React.useCallback(async () => {
    setLoadingStats(true);
    try {
      const data = await apiFetch<CacheStats>("/api/v1/cache/stats");
      setStats(data);
    } catch {
      setStats({
        total_solutions: 0,
        cache_hit_rate: 0,
        active_workflows: 0,
        total_hits: 0,
        total_misses: 0,
      });
    } finally {
      setLoadingStats(false);
    }
  }, []);

  const loadSolutions = React.useCallback(async () => {
    setLoadingSolutions(true);
    try {
      const params: Record<string, string> = {};
      if (searchQuery) params.q = searchQuery;
      if (tagFilter !== "all") params.tag = tagFilter;

      const endpoint = searchQuery
        ? "/api/v1/cache/solutions/search"
        : "/api/v1/cache/solutions";
      const data = await apiFetch<CachedSolution[] | { results: CachedSolution[] }>(
        endpoint,
        { params }
      );
      setSolutions(Array.isArray(data) ? data : data.results ?? []);
    } catch {
      setSolutions([]);
    } finally {
      setLoadingSolutions(false);
    }
  }, [searchQuery, tagFilter]);

  const loadWorkflows = React.useCallback(async () => {
    setLoadingWorkflows(true);
    try {
      const data = await apiFetch<
        CacheWorkflow[] | { workflows: CacheWorkflow[] }
      >("/api/v1/cache/workflows");
      setWorkflows(Array.isArray(data) ? data : data.workflows ?? []);
    } catch {
      setWorkflows([]);
    } finally {
      setLoadingWorkflows(false);
    }
  }, []);

  React.useEffect(() => {
    loadStats();
    loadSolutions();
    loadWorkflows();
  }, [loadStats, loadSolutions, loadWorkflows]);

  const handleDeleteSolution = async (name: string) => {
    try {
      await apiFetch(`/api/v1/cache/solutions`, {
        method: "DELETE",
        body: JSON.stringify({ name }),
      });
      toast.success(`Solution "${name}" deleted`);
      loadSolutions();
      loadStats();
    } catch (err) {
      toast.error(`Failed to delete: ${err}`);
    }
  };

  const handleRecordSuccess = async (name: string) => {
    try {
      await apiFetch(`/api/v1/cache/solutions`, {
        method: "POST",
        body: JSON.stringify({ name, action: "record_success" }),
      });
      toast.success("Success recorded");
      loadSolutions();
      loadStats();
    } catch (err) {
      toast.error(`Failed: ${err}`);
    }
  };

  const handleClearCache = async () => {
    setClearing(true);
    try {
      await apiFetch("/api/v1/cache/clear", { method: "POST" });
      toast.success("Cache cleared");
      loadSolutions();
      loadWorkflows();
      loadStats();
    } catch (err) {
      toast.error(`Failed to clear cache: ${err}`);
    } finally {
      setClearing(false);
    }
  };

  const handleCreateWorkflow = async () => {
    if (!newWorkflowName.trim()) return;
    setCreatingWorkflow(true);
    try {
      const steps = newWorkflowSteps
        .split("\n")
        .map((s) => s.trim())
        .filter(Boolean);
      await apiFetch("/api/v1/cache/workflows", {
        method: "POST",
        body: JSON.stringify({
          name: newWorkflowName,
          steps: steps.map((s, i) => ({ name: s, order: i })),
        }),
      });
      toast.success("Workflow created");
      setShowNewWorkflow(false);
      setNewWorkflowName("");
      setNewWorkflowSteps("");
      loadWorkflows();
      loadStats();
    } catch (err) {
      toast.error(`Failed: ${err}`);
    } finally {
      setCreatingWorkflow(false);
    }
  };

  const allTags = React.useMemo(() => {
    const set = new Set<string>();
    solutions.forEach((s) => s.tags?.forEach((t) => set.add(t)));
    return Array.from(set).sort();
  }, [solutions]);

  const filteredSolutions = React.useMemo(() => {
    return solutions.filter((s) => {
      if (tagFilter !== "all" && !s.tags?.includes(tagFilter)) return false;
      if (!searchQuery) return true;
      const q = searchQuery.toLowerCase();
      return (
        s.name.toLowerCase().includes(q) ||
        s.type?.toLowerCase().includes(q) ||
        s.tags?.some((t) => t.toLowerCase().includes(q))
      );
    });
  }, [solutions, searchQuery, tagFilter]);

  const workflowStatusBadge = (status: CacheWorkflow["status"]) => {
    const map: Record<
      string,
      { variant: "default" | "secondary" | "destructive" | "outline"; label: string }
    > = {
      pending: { variant: "outline", label: "Pending" },
      running: { variant: "default", label: "Running" },
      completed: { variant: "secondary", label: "Completed" },
      failed: { variant: "destructive", label: "Failed" },
    };
    const cfg = map[status] ?? map.pending;
    return <Badge variant={cfg.variant}>{cfg.label}</Badge>;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Solution Cache</h1>
          <p className="text-muted-foreground">
            Manage cached solutions and active cache workflows
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={() => {
              loadStats();
              loadSolutions();
              loadWorkflows();
            }}
          >
            <RefreshCw className="size-4 mr-2" />
            Refresh
          </Button>

          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button variant="destructive" disabled={clearing}>
                {clearing ? (
                  <Loader2 className="size-4 mr-2 animate-spin" />
                ) : (
                  <Trash2 className="size-4 mr-2" />
                )}
                Clear Cache
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Clear entire cache?</AlertDialogTitle>
                <AlertDialogDescription>
                  This will permanently delete all cached solutions and reset
                  statistics. This action cannot be undone.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction onClick={handleClearCache}>
                  Clear Cache
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>
      </div>

      {/* Stats Cards */}
      {loadingStats ? (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-24 rounded-lg" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Card>
            <CardContent className="p-4 flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                <Database className="size-5 text-primary" />
              </div>
              <div>
                <p className="text-2xl font-bold">
                  {stats?.total_solutions ?? 0}
                </p>
                <p className="text-xs text-muted-foreground">
                  Total Solutions
                </p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
                <BarChart3 className="size-5 text-green-500" />
              </div>
              <div>
                <p className="text-2xl font-bold">
                  {stats ? `${(stats.cache_hit_rate * 100).toFixed(1)}%` : "—"}
                </p>
                <p className="text-xs text-muted-foreground">Cache Hit Rate</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                <Workflow className="size-5 text-blue-500" />
              </div>
              <div>
                <p className="text-2xl font-bold">
                  {stats?.active_workflows ?? 0}
                </p>
                <p className="text-xs text-muted-foreground">
                  Active Workflows
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Tabs */}
      <Tabs defaultValue="solutions">
        <TabsList>
          <TabsTrigger value="solutions">Solutions</TabsTrigger>
          <TabsTrigger value="workflows">Workflows</TabsTrigger>
        </TabsList>

        {/* Solutions Tab */}
        <TabsContent value="solutions" className="space-y-4">
          <div className="flex items-center gap-3">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
              <Input
                placeholder="Search solutions..."
                className="pl-9"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <Select value={tagFilter} onValueChange={setTagFilter}>
              <SelectTrigger className="w-[160px]">
                <Tag className="size-3.5 mr-1.5" />
                <SelectValue placeholder="Filter by tag" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Tags</SelectItem>
                {allTags.map((t) => (
                  <SelectItem key={t} value={t}>
                    {t}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {loadingSolutions ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <Skeleton key={i} className="h-40 rounded-lg" />
              ))}
            </div>
          ) : filteredSolutions.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <Database className="size-12 mx-auto mb-4 opacity-40" />
                <h3 className="text-lg font-semibold mb-2">
                  {searchQuery || tagFilter !== "all"
                    ? "No matching solutions"
                    : "No cached solutions"}
                </h3>
                <p className="text-muted-foreground text-sm">
                  {searchQuery || tagFilter !== "all"
                    ? "Try adjusting your search or filter"
                    : "Solutions will appear here once the cache is populated"}
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredSolutions.map((sol) => (
                <Card
                  key={sol.name}
                  className="hover:shadow-md transition-shadow"
                >
                  <CardContent className="p-4 space-y-3">
                    <div className="flex items-start justify-between">
                      <div className="min-w-0">
                        <p className="font-semibold truncate">{sol.name}</p>
                        <Badge variant="outline" className="mt-1 text-xs">
                          {sol.type}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-1 text-xs text-muted-foreground">
                        <ThumbsUp className="size-3" />
                        {sol.success_count}
                      </div>
                    </div>

                    <div className="flex flex-wrap gap-1">
                      {sol.tags?.slice(0, 4).map((t) => (
                        <Badge
                          key={t}
                          variant="secondary"
                          className="text-[10px]"
                        >
                          {t}
                        </Badge>
                      ))}
                      {(sol.tags?.length ?? 0) > 4 && (
                        <Badge variant="secondary" className="text-[10px]">
                          +{sol.tags.length - 4}
                        </Badge>
                      )}
                    </div>

                    <div className="flex items-center gap-1.5">
                      <Button
                        variant="outline"
                        size="sm"
                        className="h-7 text-xs gap-1"
                        onClick={() => setSelectedSolution(sol)}
                      >
                        <Eye className="size-3" />
                        Details
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        className="h-7 text-xs gap-1"
                        onClick={() => handleRecordSuccess(sol.name)}
                      >
                        <ThumbsUp className="size-3" />
                        Success
                      </Button>
                      <div className="flex-1" />
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-7 text-xs gap-1 text-destructive hover:text-destructive"
                        onClick={() => handleDeleteSolution(sol.name)}
                      >
                        <Trash2 className="size-3" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        {/* Workflows Tab */}
        <TabsContent value="workflows" className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              {workflows.length} workflow{workflows.length !== 1 && "s"}
            </p>
            <Button
              size="sm"
              onClick={() => setShowNewWorkflow(true)}
            >
              <Plus className="size-4 mr-1.5" />
              New Workflow
            </Button>
          </div>

          {loadingWorkflows ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-28 rounded-lg" />
              ))}
            </div>
          ) : workflows.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <Workflow className="size-12 mx-auto mb-4 opacity-40" />
                <h3 className="text-lg font-semibold mb-2">
                  No active workflows
                </h3>
                <p className="text-muted-foreground text-sm mb-4">
                  Create a workflow to orchestrate cache operations
                </p>
                <Button onClick={() => setShowNewWorkflow(true)}>
                  <Plus className="size-4 mr-1.5" />
                  Create Workflow
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-3">
              {workflows.map((wf) => (
                <Card key={wf.id}>
                  <CardContent className="p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Workflow className="size-4 text-muted-foreground" />
                        <p className="font-semibold">{wf.name}</p>
                      </div>
                      {workflowStatusBadge(wf.status)}
                    </div>

                    {wf.steps?.length > 0 && (
                      <div className="flex items-center gap-1 overflow-x-auto pb-1">
                        {wf.steps
                          .sort((a, b) => a.order - b.order)
                          .map((step, idx) => (
                            <React.Fragment key={step.name}>
                              {idx > 0 && (
                                <ArrowRight className="size-3 text-muted-foreground shrink-0" />
                              )}
                              <div className="flex items-center gap-1.5 px-2.5 py-1.5 bg-muted rounded-md shrink-0">
                                {stepStatusIcon[step.status] ??
                                  stepStatusIcon.pending}
                                <span className="text-xs font-medium">
                                  {step.name}
                                </span>
                              </div>
                            </React.Fragment>
                          ))}
                      </div>
                    )}

                    <p className="text-xs text-muted-foreground">
                      Created{" "}
                      {new Date(wf.created_at).toLocaleString()}
                    </p>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Solution Detail Dialog */}
      <Dialog
        open={!!selectedSolution}
        onOpenChange={(open) => !open && setSelectedSolution(null)}
      >
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>{selectedSolution?.name}</DialogTitle>
          </DialogHeader>
          {selectedSolution && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground">Type</p>
                  <p className="font-medium">{selectedSolution.type}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Success Count</p>
                  <p className="font-medium">{selectedSolution.success_count}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Created</p>
                  <p className="font-medium">
                    {new Date(selectedSolution.created_at).toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-muted-foreground">Updated</p>
                  <p className="font-medium">
                    {new Date(selectedSolution.updated_at).toLocaleString()}
                  </p>
                </div>
              </div>
              {selectedSolution.description && (
                <div>
                  <p className="text-sm text-muted-foreground mb-1">
                    Description
                  </p>
                  <p className="text-sm">{selectedSolution.description}</p>
                </div>
              )}
              <div>
                <p className="text-sm text-muted-foreground mb-1">Tags</p>
                <div className="flex flex-wrap gap-1">
                  {selectedSolution.tags?.length ? (
                    selectedSolution.tags.map((t) => (
                      <Badge key={t} variant="secondary">
                        {t}
                      </Badge>
                    ))
                  ) : (
                    <span className="text-sm text-muted-foreground">
                      No tags
                    </span>
                  )}
                </div>
              </div>
              {selectedSolution.metadata &&
                Object.keys(selectedSolution.metadata).length > 0 && (
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">
                      Metadata
                    </p>
                    <pre className="text-xs bg-muted p-3 rounded-md overflow-auto max-h-40">
                      {JSON.stringify(selectedSolution.metadata, null, 2)}
                    </pre>
                  </div>
                )}
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* New Workflow Dialog */}
      <Dialog open={showNewWorkflow} onOpenChange={setShowNewWorkflow}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Create Workflow</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="wf-name">Workflow Name</Label>
              <Input
                id="wf-name"
                placeholder="e.g. nightly-cache-refresh"
                value={newWorkflowName}
                onChange={(e) => setNewWorkflowName(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="wf-steps">
                Steps{" "}
                <span className="text-muted-foreground font-normal">
                  (one per line)
                </span>
              </Label>
              <Textarea
                id="wf-steps"
                placeholder={"Fetch data\nProcess results\nUpdate cache"}
                rows={4}
                value={newWorkflowSteps}
                onChange={(e) => setNewWorkflowSteps(e.target.value)}
              />
            </div>
            <div className="flex justify-end gap-2">
              <Button
                variant="outline"
                onClick={() => setShowNewWorkflow(false)}
              >
                Cancel
              </Button>
              <Button
                onClick={handleCreateWorkflow}
                disabled={!newWorkflowName.trim() || creatingWorkflow}
              >
                {creatingWorkflow && (
                  <Loader2 className="size-4 mr-1.5 animate-spin" />
                )}
                Create
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
