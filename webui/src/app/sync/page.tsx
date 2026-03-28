"use client";

import * as React from "react";
import {
  RefreshCw,
  Loader2,
  CheckCircle2,
  XCircle,
  Clock,
  Play,
  GitCompare,
  ArrowLeftRight,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  Shield,
  History,
  Merge,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { toast } from "sonner";
import { apiFetch } from "@/lib/api";
import { getBackendUrl } from "@/lib/api-client";

interface SyncSession {
  id: string;
  status: "active" | "completed" | "failed";
  started_at: string;
  completed_at?: string;
  conflicts_found: number;
  conflicts_resolved: number;
  metadata?: Record<string, unknown>;
}

interface ConflictSide {
  source: string;
  value: unknown;
  updated_at?: string;
}

interface SyncConflict {
  conflict_id: string;
  resource_type: string;
  resource_id: string;
  local: ConflictSide;
  remote: ConflictSide;
  status: "pending" | "resolved";
  resolution?: string;
  resolved_at?: string;
  resolved_by?: string;
  created_at: string;
}

type ResolutionStrategy = "keep_local" | "keep_remote" | "merge";

const strategyLabels: Record<ResolutionStrategy, { label: string; icon: React.ElementType }> = {
  keep_local: { label: "Keep Local", icon: Shield },
  keep_remote: { label: "Keep Remote", icon: ArrowLeftRight },
  merge: { label: "Merge", icon: Merge },
};

export default function SyncPage() {
  const [session, setSession] = React.useState<SyncSession | null>(null);
  const [conflicts, setConflicts] = React.useState<SyncConflict[]>([]);
  const [loadingSession, setLoadingSession] = React.useState(false);
  const [loadingConflicts, setLoadingConflicts] = React.useState(true);
  const [starting, setStarting] = React.useState(false);
  const [resolvingId, setResolvingId] = React.useState<string | null>(null);
  const [strategies, setStrategies] = React.useState<
    Record<string, ResolutionStrategy>
  >({});
  const [expandedConflict, setExpandedConflict] = React.useState<
    string | null
  >(null);
  const [sessionName, setSessionName] = React.useState("");

  const loadConflicts = React.useCallback(async () => {
    setLoadingConflicts(true);
    try {
      const data = await apiFetch<
        SyncConflict[] | { conflicts: SyncConflict[] }
      >("/api/v1/sync/conflicts");
      setConflicts(Array.isArray(data) ? data : data.conflicts ?? []);
    } catch {
      setConflicts([]);
    } finally {
      setLoadingConflicts(false);
    }
  }, []);

  React.useEffect(() => {
    loadConflicts();
  }, [loadConflicts]);

  const handleStartSync = async () => {
    setStarting(true);
    setLoadingSession(true);
    try {
      const result = await apiFetch<SyncSession>("/api/v1/sync/sessions", {
        method: "POST",
        body: JSON.stringify({
          name: sessionName || undefined,
        }),
      });
      setSession(result);
      toast.success("Sync session started");
      setSessionName("");
      loadConflicts();
    } catch (err) {
      toast.error(`Failed to start sync: ${err}`);
    } finally {
      setStarting(false);
      setLoadingSession(false);
    }
  };

  const handleResolve = async (conflictId: string) => {
    const strategy = strategies[conflictId];
    if (!strategy) {
      toast.error("Select a resolution strategy first");
      return;
    }

    setResolvingId(conflictId);
    try {
      await apiFetch(`/api/v1/sync/conflicts/${conflictId}/resolve`, {
        method: "POST",
        body: JSON.stringify({ strategy }),
      });
      toast.success("Conflict resolved");
      loadConflicts();
    } catch (err) {
      toast.error(`Failed to resolve: ${err}`);
    } finally {
      setResolvingId(null);
    }
  };

  const pendingConflicts = conflicts.filter((c) => c.status === "pending");
  const resolvedConflicts = conflicts.filter((c) => c.status === "resolved");

  const renderValue = (value: unknown) => {
    if (value === null || value === undefined) return "null";
    if (typeof value === "object") {
      return JSON.stringify(value, null, 2);
    }
    return String(value);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Session Sync</h1>
          <p className="text-muted-foreground">
            Synchronize sessions and resolve data conflicts
          </p>
        </div>
        <Button variant="outline" onClick={loadConflicts}>
          <RefreshCw className="size-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Start Sync Session */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <Play className="size-4" />
            Start Sync Session
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-3">
            <div className="flex-1">
              <Input
                placeholder="Session name (optional)"
                value={sessionName}
                onChange={(e) => setSessionName(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleStartSync()}
              />
            </div>
            <Button onClick={handleStartSync} disabled={starting}>
              {starting ? (
                <Loader2 className="size-4 mr-2 animate-spin" />
              ) : (
                <GitCompare className="size-4 mr-2" />
              )}
              Start Sync
            </Button>
          </div>

          {/* Active session display */}
          {loadingSession ? (
            <Skeleton className="h-20 rounded-md" />
          ) : session ? (
            <div className="p-4 bg-muted rounded-lg space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Badge
                    variant={
                      session.status === "active"
                        ? "default"
                        : session.status === "completed"
                          ? "secondary"
                          : "destructive"
                    }
                  >
                    {session.status === "active" && (
                      <Loader2 className="size-3 mr-1 animate-spin" />
                    )}
                    {session.status}
                  </Badge>
                  <span className="text-sm text-muted-foreground font-mono">
                    {session.id.slice(0, 12)}...
                  </span>
                </div>
                <span className="text-xs text-muted-foreground">
                  Started {new Date(session.started_at).toLocaleString()}
                </span>
              </div>
              <div className="flex gap-4 text-sm">
                <span>
                  <span className="text-muted-foreground">Conflicts found:</span>{" "}
                  <span className="font-medium">{session.conflicts_found}</span>
                </span>
                <span>
                  <span className="text-muted-foreground">Resolved:</span>{" "}
                  <span className="font-medium">
                    {session.conflicts_resolved}
                  </span>
                </span>
              </div>
            </div>
          ) : null}
        </CardContent>
      </Card>

      {/* Pending Conflicts */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base flex items-center gap-2">
              <AlertTriangle className="size-4 text-amber-500" />
              Pending Conflicts
              {pendingConflicts.length > 0 && (
                <Badge variant="secondary">{pendingConflicts.length}</Badge>
              )}
            </CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          {loadingConflicts ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-24 rounded-lg" />
              ))}
            </div>
          ) : pendingConflicts.length === 0 ? (
            <div className="text-center py-10">
              <CheckCircle2 className="size-10 mx-auto mb-3 text-green-500 opacity-60" />
              <p className="font-medium mb-1">No pending conflicts</p>
              <p className="text-sm text-muted-foreground">
                All conflicts have been resolved, or no conflicts exist. Start
                a sync session to check for new ones.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {pendingConflicts.map((conflict) => {
                const isExpanded = expandedConflict === conflict.conflict_id;
                return (
                  <div
                    key={conflict.conflict_id}
                    className="border rounded-lg overflow-hidden"
                  >
                    {/* Conflict header */}
                    <button
                      className="w-full flex items-center justify-between px-4 py-3 hover:bg-muted/50 transition-colors text-left"
                      onClick={() =>
                        setExpandedConflict(
                          isExpanded ? null : conflict.conflict_id
                        )
                      }
                    >
                      <div className="flex items-center gap-3">
                        <ArrowLeftRight className="size-4 text-amber-500 shrink-0" />
                        <div>
                          <p className="text-sm font-medium">
                            {conflict.resource_type} /{" "}
                            <span className="font-mono text-xs">
                              {conflict.resource_id}
                            </span>
                          </p>
                          <p className="text-xs text-muted-foreground">
                            Detected{" "}
                            {new Date(conflict.created_at).toLocaleString()}
                          </p>
                        </div>
                      </div>
                      {isExpanded ? (
                        <ChevronUp className="size-4 text-muted-foreground" />
                      ) : (
                        <ChevronDown className="size-4 text-muted-foreground" />
                      )}
                    </button>

                    {/* Conflict details */}
                    {isExpanded && (
                      <div className="px-4 pb-4 space-y-4">
                        <Separator />
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {/* Local side */}
                          <div className="space-y-2">
                            <div className="flex items-center gap-1.5">
                              <Shield className="size-3.5 text-blue-500" />
                              <span className="text-xs font-medium uppercase tracking-wider text-blue-500">
                                Local
                              </span>
                              <span className="text-[10px] text-muted-foreground">
                                ({conflict.local.source})
                              </span>
                            </div>
                            <pre className="text-xs bg-blue-500/5 border border-blue-500/20 p-3 rounded-md overflow-auto max-h-36">
                              {renderValue(conflict.local.value)}
                            </pre>
                            {conflict.local.updated_at && (
                              <p className="text-[10px] text-muted-foreground">
                                Updated{" "}
                                {new Date(
                                  conflict.local.updated_at
                                ).toLocaleString()}
                              </p>
                            )}
                          </div>

                          {/* Remote side */}
                          <div className="space-y-2">
                            <div className="flex items-center gap-1.5">
                              <ArrowLeftRight className="size-3.5 text-orange-500" />
                              <span className="text-xs font-medium uppercase tracking-wider text-orange-500">
                                Remote
                              </span>
                              <span className="text-[10px] text-muted-foreground">
                                ({conflict.remote.source})
                              </span>
                            </div>
                            <pre className="text-xs bg-orange-500/5 border border-orange-500/20 p-3 rounded-md overflow-auto max-h-36">
                              {renderValue(conflict.remote.value)}
                            </pre>
                            {conflict.remote.updated_at && (
                              <p className="text-[10px] text-muted-foreground">
                                Updated{" "}
                                {new Date(
                                  conflict.remote.updated_at
                                ).toLocaleString()}
                              </p>
                            )}
                          </div>
                        </div>

                        {/* Resolution controls */}
                        <div className="flex items-center gap-3 pt-1">
                          <Select
                            value={strategies[conflict.conflict_id] ?? ""}
                            onValueChange={(v) =>
                              setStrategies((prev) => ({
                                ...prev,
                                [conflict.conflict_id]:
                                  v as ResolutionStrategy,
                              }))
                            }
                          >
                            <SelectTrigger className="w-[180px]">
                              <SelectValue placeholder="Resolution strategy" />
                            </SelectTrigger>
                            <SelectContent>
                              {(
                                Object.entries(strategyLabels) as [
                                  ResolutionStrategy,
                                  (typeof strategyLabels)[ResolutionStrategy],
                                ][]
                              ).map(([key, { label, icon: SIcon }]) => (
                                <SelectItem key={key} value={key}>
                                  <span className="flex items-center gap-1.5">
                                    <SIcon className="size-3.5" />
                                    {label}
                                  </span>
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <Button
                            size="sm"
                            onClick={() =>
                              handleResolve(conflict.conflict_id)
                            }
                            disabled={
                              !strategies[conflict.conflict_id] ||
                              resolvingId === conflict.conflict_id
                            }
                          >
                            {resolvingId === conflict.conflict_id ? (
                              <Loader2 className="size-4 mr-1.5 animate-spin" />
                            ) : (
                              <CheckCircle2 className="size-4 mr-1.5" />
                            )}
                            Resolve
                          </Button>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Resolved Conflicts (History) */}
      <Card className="bg-muted/50">
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <History className="size-4" />
            Resolution History
            {resolvedConflicts.length > 0 && (
              <Badge variant="outline">{resolvedConflicts.length}</Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loadingConflicts ? (
            <Skeleton className="h-20 rounded-lg" />
          ) : resolvedConflicts.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-6">
              No resolved conflicts yet
            </p>
          ) : (
            <div className="space-y-2">
              {resolvedConflicts.map((conflict) => (
                <div
                  key={conflict.conflict_id}
                  className="flex items-center justify-between px-3 py-2.5 bg-background rounded-md"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <CheckCircle2 className="size-4 text-green-500 shrink-0" />
                    <div className="min-w-0">
                      <p className="text-sm font-medium truncate">
                        {conflict.resource_type} / {conflict.resource_id}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Resolved{" "}
                        {conflict.resolved_at
                          ? new Date(conflict.resolved_at).toLocaleString()
                          : "—"}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    {conflict.resolution && (
                      <Badge variant="secondary" className="text-xs">
                        {conflict.resolution}
                      </Badge>
                    )}
                    {conflict.resolved_by && (
                      <span className="text-xs text-muted-foreground">
                        by {conflict.resolved_by}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
