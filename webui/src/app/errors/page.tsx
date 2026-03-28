"use client";

import React, { useState, useEffect, useCallback, useRef } from "react";
import {
  AlertTriangle,
  RefreshCw,
  Trash2,
  Loader2,
  Search,
  Clock,
  ChevronDown,
  ChevronRight,
  X,
  Filter,
  ToggleLeft,
  ToggleRight,
  AlertCircle,
  Info,
  Bug,
  ShieldAlert,
} from "lucide-react";
import { toast } from "sonner";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
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
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
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
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { apiFetch } from "@/lib/api";

interface ErrorEntry {
  id: string;
  timestamp: string;
  status_code: number;
  method?: string;
  path: string;
  error_message: string;
  detail?: string;
  traceback?: string;
  request_info?: {
    headers?: Record<string, string>;
    query_params?: Record<string, string>;
    body?: string;
    client_ip?: string;
  };
  severity?: "critical" | "error" | "warning" | "info";
}

interface ErrorDetail extends ErrorEntry {
  traceback?: string;
  request_info?: {
    headers?: Record<string, string>;
    query_params?: Record<string, string>;
    body?: string;
    client_ip?: string;
  };
}

interface ErrorSummary {
  total: number;
  by_severity: Record<string, number>;
  by_status_code: Record<string, number>;
}

const severityConfig: Record<string, { color: string; icon: React.ReactNode; label: string }> = {
  critical: { color: "bg-red-600/10 text-red-500 border-red-500/20", icon: <ShieldAlert className="h-3 w-3" />, label: "Critical" },
  error: { color: "bg-red-500/10 text-red-400 border-red-400/20", icon: <AlertCircle className="h-3 w-3" />, label: "Error" },
  warning: { color: "bg-yellow-500/10 text-yellow-500 border-yellow-500/20", icon: <AlertTriangle className="h-3 w-3" />, label: "Warning" },
  info: { color: "bg-blue-500/10 text-blue-500 border-blue-500/20", icon: <Info className="h-3 w-3" />, label: "Info" },
};

function SeverityBadge({ severity }: { severity: string }) {
  const config = severityConfig[severity] || severityConfig.error;
  return (
    <Badge variant="outline" className={config.color}>
      {config.icon}
      {config.label}
    </Badge>
  );
}

function StatusCodeBadge({ code }: { code: number }) {
  let color = "bg-gray-500/10 text-gray-400 border-gray-500/20";
  if (code >= 500) color = "bg-red-500/10 text-red-500 border-red-500/20";
  else if (code >= 400) color = "bg-yellow-500/10 text-yellow-500 border-yellow-500/20";
  else if (code >= 300) color = "bg-blue-500/10 text-blue-400 border-blue-400/20";
  return (
    <Badge variant="outline" className={`font-mono ${color}`}>
      {code}
    </Badge>
  );
}

export default function ErrorBrowserPage() {
  const [errors, setErrors] = useState<ErrorEntry[]>([]);
  const [summary, setSummary] = useState<ErrorSummary>({ total: 0, by_severity: {}, by_status_code: {} });
  const [loading, setLoading] = useState(true);
  const [clearing, setClearing] = useState(false);
  const [selectedError, setSelectedError] = useState<ErrorDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());

  const [filterStatus, setFilterStatus] = useState<string>("");
  const [filterPath, setFilterPath] = useState("");
  const [filterTimeRange, setFilterTimeRange] = useState<string>("");
  const [autoRefresh, setAutoRefresh] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const fetchErrors = useCallback(async () => {
    try {
      const params: Record<string, string | number | boolean | undefined> = {};
      if (filterStatus) params.status_code = filterStatus;
      if (filterPath) params.path_pattern = filterPath;
      if (filterTimeRange) params.time_range = filterTimeRange;

      const data = await apiFetch<{ errors: ErrorEntry[]; total: number; summary?: ErrorSummary }>(
        "/api/v1/errors",
        { params }
      );
      setErrors(data.errors || []);
      if (data.summary) {
        setSummary(data.summary);
      } else {
        const byStatus: Record<string, number> = {};
        const bySeverity: Record<string, number> = {};
        (data.errors || []).forEach((e) => {
          const sc = String(e.status_code);
          byStatus[sc] = (byStatus[sc] || 0) + 1;
          const sev = e.severity || "error";
          bySeverity[sev] = (bySeverity[sev] || 0) + 1;
        });
        setSummary({ total: data.total || (data.errors || []).length, by_severity: bySeverity, by_status_code: byStatus });
      }
    } catch (err) {
      toast.error("Failed to load errors", { description: String(err) });
    }
  }, [filterStatus, filterPath, filterTimeRange]);

  const loadAll = useCallback(async () => {
    setLoading(true);
    await fetchErrors();
    setLoading(false);
  }, [fetchErrors]);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  useEffect(() => {
    if (autoRefresh) {
      intervalRef.current = setInterval(fetchErrors, 5000);
    } else if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [autoRefresh, fetchErrors]);

  async function handleViewDetail(errorId: string) {
    setDetailLoading(true);
    try {
      const detail = await apiFetch<ErrorDetail>(`/api/v1/errors/${errorId}`);
      setSelectedError(detail);
    } catch (err) {
      toast.error("Failed to load error detail", { description: String(err) });
    } finally {
      setDetailLoading(false);
    }
  }

  async function handleClearAll() {
    setClearing(true);
    try {
      await apiFetch("/api/v1/errors", { method: "DELETE" });
      toast.success("All errors cleared");
      setErrors([]);
      setSummary({ total: 0, by_severity: {}, by_status_code: {} });
    } catch (err) {
      toast.error("Failed to clear errors", { description: String(err) });
    } finally {
      setClearing(false);
    }
  }

  function toggleRow(id: string) {
    setExpandedRows((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  function clearFilters() {
    setFilterStatus("");
    setFilterPath("");
    setFilterTimeRange("");
  }

  const hasFilters = !!(filterStatus || filterPath || filterTimeRange);

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <Skeleton className="h-8 w-48 mb-2" />
          <Skeleton className="h-4 w-80" />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-24" />
          ))}
        </div>
        <Skeleton className="h-96" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Error Browser</h1>
          <p className="text-muted-foreground">
            Inspect, filter, and manage API errors and exceptions.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={autoRefresh ? "text-green-500" : "text-muted-foreground"}
          >
            {autoRefresh ? <ToggleRight className="h-4 w-4 mr-1.5" /> : <ToggleLeft className="h-4 w-4 mr-1.5" />}
            Auto-refresh
          </Button>
          <Button variant="outline" size="sm" onClick={loadAll}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button variant="destructive" size="sm" disabled={errors.length === 0}>
                <Trash2 className="h-4 w-4 mr-2" />
                Clear All
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Clear all errors?</AlertDialogTitle>
                <AlertDialogDescription>
                  This will permanently delete {summary.total} error records. This action cannot be undone.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction onClick={handleClearAll} disabled={clearing}>
                  {clearing ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : null}
                  Delete All
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-red-500/10"><Bug className="h-5 w-5 text-red-500" /></div>
              <div>
                <p className="text-2xl font-bold">{summary.total}</p>
                <p className="text-xs text-muted-foreground">Total Errors</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-red-600/10"><ShieldAlert className="h-5 w-5 text-red-600" /></div>
              <div>
                <p className="text-2xl font-bold">{summary.by_severity?.critical || 0}</p>
                <p className="text-xs text-muted-foreground">Critical</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-yellow-500/10"><AlertTriangle className="h-5 w-5 text-yellow-500" /></div>
              <div>
                <p className="text-2xl font-bold">{summary.by_severity?.warning || 0}</p>
                <p className="text-xs text-muted-foreground">Warnings</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-orange-500/10"><AlertCircle className="h-5 w-5 text-orange-500" /></div>
              <div>
                <p className="text-2xl font-bold">{(summary.by_status_code?.["500"] || 0) + (summary.by_status_code?.["502"] || 0) + (summary.by_status_code?.["503"] || 0)}</p>
                <p className="text-xs text-muted-foreground">5xx Errors</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-wrap items-end gap-3">
            <div className="space-y-1.5 min-w-[150px]">
              <Label className="text-xs">Status Code</Label>
              <Select value={filterStatus} onValueChange={setFilterStatus}>
                <SelectTrigger className="h-9">
                  <SelectValue placeholder="All" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All</SelectItem>
                  <SelectItem value="400">400</SelectItem>
                  <SelectItem value="401">401</SelectItem>
                  <SelectItem value="403">403</SelectItem>
                  <SelectItem value="404">404</SelectItem>
                  <SelectItem value="422">422</SelectItem>
                  <SelectItem value="500">500</SelectItem>
                  <SelectItem value="502">502</SelectItem>
                  <SelectItem value="503">503</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5 min-w-[150px]">
              <Label className="text-xs">Time Range</Label>
              <Select value={filterTimeRange} onValueChange={setFilterTimeRange}>
                <SelectTrigger className="h-9">
                  <SelectValue placeholder="All time" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All time</SelectItem>
                  <SelectItem value="1h">Last hour</SelectItem>
                  <SelectItem value="6h">Last 6 hours</SelectItem>
                  <SelectItem value="24h">Last 24 hours</SelectItem>
                  <SelectItem value="7d">Last 7 days</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5 flex-1 min-w-[200px]">
              <Label className="text-xs">Path Pattern</Label>
              <div className="relative">
                <Search className="h-4 w-4 absolute left-2.5 top-2.5 text-muted-foreground" />
                <Input
                  className="h-9 pl-8"
                  placeholder="/api/v1/..."
                  value={filterPath}
                  onChange={(e) => setFilterPath(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && fetchErrors()}
                />
              </div>
            </div>
            <Button variant="outline" size="sm" className="h-9" onClick={fetchErrors}>
              <Filter className="h-3.5 w-3.5 mr-1.5" />
              Apply
            </Button>
            {hasFilters && (
              <Button variant="ghost" size="sm" className="h-9" onClick={clearFilters}>
                <X className="h-3.5 w-3.5 mr-1.5" />
                Clear
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Error Table */}
      <Card>
        <CardContent className="p-0">
          {errors.length === 0 ? (
            <div className="text-center py-16 text-muted-foreground">
              <AlertTriangle className="h-12 w-12 mx-auto mb-3 opacity-40" />
              <p className="font-medium">No errors found</p>
              <p className="text-sm">{hasFilters ? "Try adjusting your filters." : "No errors have been recorded."}</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-8" />
                  <TableHead>Timestamp</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Path</TableHead>
                  <TableHead>Severity</TableHead>
                  <TableHead className="max-w-xs">Message</TableHead>
                  <TableHead className="w-20">Detail</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {errors.map((error) => (
                  <React.Fragment key={error.id}>
                    <TableRow
                      className="cursor-pointer hover:bg-muted/50"
                      onClick={() => toggleRow(error.id)}
                    >
                      <TableCell className="px-2">
                        {expandedRows.has(error.id) ? (
                          <ChevronDown className="h-4 w-4 text-muted-foreground" />
                        ) : (
                          <ChevronRight className="h-4 w-4 text-muted-foreground" />
                        )}
                      </TableCell>
                      <TableCell className="text-xs text-muted-foreground whitespace-nowrap">
                        <Clock className="h-3 w-3 inline mr-1" />
                        {new Date(error.timestamp).toLocaleString()}
                      </TableCell>
                      <TableCell><StatusCodeBadge code={error.status_code} /></TableCell>
                      <TableCell>
                        <span className="font-mono text-xs">
                          {error.method && <span className="text-muted-foreground mr-1">{error.method}</span>}
                          {error.path}
                        </span>
                      </TableCell>
                      <TableCell><SeverityBadge severity={error.severity || "error"} /></TableCell>
                      <TableCell className="max-w-xs truncate text-sm">{error.error_message}</TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleViewDetail(error.id);
                          }}
                        >
                          View
                        </Button>
                      </TableCell>
                    </TableRow>
                    {expandedRows.has(error.id) && (
                      <TableRow>
                        <TableCell colSpan={7} className="bg-muted/30 p-4">
                          <div className="space-y-2">
                            <p className="text-sm font-medium">Error Message</p>
                            <p className="text-sm text-muted-foreground">{error.error_message}</p>
                            {error.detail && (
                              <>
                                <p className="text-sm font-medium mt-3">Detail</p>
                                <pre className="text-xs bg-muted p-3 rounded-md overflow-x-auto whitespace-pre-wrap font-mono">
                                  {error.detail}
                                </pre>
                              </>
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

      {/* Detail Dialog */}
      <Dialog open={!!selectedError} onOpenChange={(open) => !open && setSelectedError(null)}>
        <DialogContent className="max-w-2xl max-h-[80vh]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              Error Detail
              {selectedError && <StatusCodeBadge code={selectedError.status_code} />}
            </DialogTitle>
            <DialogDescription>
              {selectedError?.path}
            </DialogDescription>
          </DialogHeader>
          {detailLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
          ) : selectedError ? (
            <ScrollArea className="max-h-[60vh] pr-4">
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-xs text-muted-foreground">Timestamp</Label>
                    <p className="text-sm">{new Date(selectedError.timestamp).toLocaleString()}</p>
                  </div>
                  <div>
                    <Label className="text-xs text-muted-foreground">Severity</Label>
                    <div className="mt-0.5"><SeverityBadge severity={selectedError.severity || "error"} /></div>
                  </div>
                  <div>
                    <Label className="text-xs text-muted-foreground">Method</Label>
                    <p className="text-sm font-mono">{selectedError.method || "—"}</p>
                  </div>
                  <div>
                    <Label className="text-xs text-muted-foreground">Path</Label>
                    <p className="text-sm font-mono">{selectedError.path}</p>
                  </div>
                </div>

                <Separator />

                <div>
                  <Label className="text-xs text-muted-foreground">Error Message</Label>
                  <p className="text-sm mt-1">{selectedError.error_message}</p>
                </div>

                {selectedError.detail && (
                  <div>
                    <Label className="text-xs text-muted-foreground">Detail</Label>
                    <pre className="text-xs bg-muted p-3 rounded-md mt-1 overflow-x-auto whitespace-pre-wrap font-mono">
                      {selectedError.detail}
                    </pre>
                  </div>
                )}

                {selectedError.traceback && (
                  <div>
                    <Label className="text-xs text-muted-foreground">Traceback</Label>
                    <pre className="text-xs bg-muted p-3 rounded-md mt-1 overflow-x-auto whitespace-pre-wrap font-mono text-red-400">
                      {selectedError.traceback}
                    </pre>
                  </div>
                )}

                {selectedError.request_info && (
                  <>
                    <Separator />
                    <div>
                      <Label className="text-xs text-muted-foreground">Request Info</Label>
                      <div className="mt-2 space-y-2">
                        {selectedError.request_info.client_ip && (
                          <p className="text-xs">
                            <span className="text-muted-foreground">Client IP:</span>{" "}
                            <span className="font-mono">{selectedError.request_info.client_ip}</span>
                          </p>
                        )}
                        {selectedError.request_info.headers && Object.keys(selectedError.request_info.headers).length > 0 && (
                          <div>
                            <p className="text-xs text-muted-foreground mb-1">Headers</p>
                            <pre className="text-xs bg-muted p-2 rounded-md overflow-x-auto font-mono">
                              {JSON.stringify(selectedError.request_info.headers, null, 2)}
                            </pre>
                          </div>
                        )}
                        {selectedError.request_info.query_params && Object.keys(selectedError.request_info.query_params).length > 0 && (
                          <div>
                            <p className="text-xs text-muted-foreground mb-1">Query Params</p>
                            <pre className="text-xs bg-muted p-2 rounded-md overflow-x-auto font-mono">
                              {JSON.stringify(selectedError.request_info.query_params, null, 2)}
                            </pre>
                          </div>
                        )}
                        {selectedError.request_info.body && (
                          <div>
                            <p className="text-xs text-muted-foreground mb-1">Request Body</p>
                            <pre className="text-xs bg-muted p-2 rounded-md overflow-x-auto font-mono">
                              {selectedError.request_info.body}
                            </pre>
                          </div>
                        )}
                      </div>
                    </div>
                  </>
                )}
              </div>
            </ScrollArea>
          ) : null}
        </DialogContent>
      </Dialog>
    </div>
  );
}
