"use client";

import * as React from "react";
import {
  Shield,
  ShieldCheck,
  ShieldAlert,
  Download,
  Play,
  RefreshCw,
  Search,
  Wifi,
  WifiOff,
  FileText,
  Loader2,
  Plus,
  Wrench,
  Scan,
  Globe,
  Activity,
  CheckCircle2,
  XCircle,
  Clock,
  AlertTriangle,
} from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
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
import { apiFetch } from "@/lib/api";
import { toast } from "sonner";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface SecurityTool {
  id: string;
  name: string;
  description?: string;
  category: string;
  installed: boolean;
  version?: string;
}

interface ScanOperation {
  id: string;
  target: string;
  scan_type: string;
  status: "pending" | "running" | "completed" | "failed";
  started_at: string;
  completed_at?: string;
  findings_count?: number;
}

interface VpnProfile {
  id: string;
  name: string;
  server: string;
  protocol: string;
}

interface VpnStatus {
  connected: boolean;
  profile?: string;
  ip?: string;
  uptime_seconds?: number;
}

interface SecurityReport {
  id: string;
  title: string;
  type: string;
  created_at: string;
  download_url?: string;
}

interface HealthStatus {
  status: "healthy" | "degraded" | "unhealthy";
  services?: Record<string, string>;
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function HealthIndicator({ health }: { health: HealthStatus | null }) {
  if (!health) return <Skeleton className="h-6 w-20" />;
  const cfg = {
    healthy: { icon: ShieldCheck, color: "text-green-500", bg: "bg-green-500/10" },
    degraded: { icon: AlertTriangle, color: "text-amber-500", bg: "bg-amber-500/10" },
    unhealthy: { icon: ShieldAlert, color: "text-red-500", bg: "bg-red-500/10" },
  }[health.status];
  const Icon = cfg.icon;
  return (
    <Badge variant="outline" className={`gap-1.5 ${cfg.color}`}>
      <Icon className="size-3.5" />
      {health.status}
    </Badge>
  );
}

function ScanStatusBadge({ status }: { status: ScanOperation["status"] }) {
  const map: Record<
    ScanOperation["status"],
    { icon: React.ElementType; variant: "default" | "secondary" | "destructive" | "outline"; spin?: boolean }
  > = {
    pending: { icon: Clock, variant: "outline" },
    running: { icon: Loader2, variant: "default", spin: true },
    completed: { icon: CheckCircle2, variant: "secondary" },
    failed: { icon: XCircle, variant: "destructive" },
  };
  const cfg = map[status];
  const Icon = cfg.icon;
  return (
    <Badge variant={cfg.variant} className="gap-1">
      <Icon className={`size-3 ${cfg.spin ? "animate-spin" : ""}`} />
      {status}
    </Badge>
  );
}

// ---------------------------------------------------------------------------
// Main Page
// ---------------------------------------------------------------------------

export default function CybersecPage() {
  // Health
  const [health, setHealth] = React.useState<HealthStatus | null>(null);

  // Tools
  const [tools, setTools] = React.useState<SecurityTool[]>([]);
  const [toolsLoading, setToolsLoading] = React.useState(true);
  const [categoryFilter, setCategoryFilter] = React.useState("all");
  const [toolSearch, setToolSearch] = React.useState("");
  const [installingTool, setInstallingTool] = React.useState<string | null>(null);
  const [executingTool, setExecutingTool] = React.useState<string | null>(null);

  // Scans
  const [scans, setScans] = React.useState<ScanOperation[]>([]);
  const [scansLoading, setScansLoading] = React.useState(true);
  const [scanTarget, setScanTarget] = React.useState("");
  const [scanType, setScanType] = React.useState("port_scan");
  const [launchingScan, setLaunchingScan] = React.useState(false);

  // VPN
  const [vpnStatus, setVpnStatus] = React.useState<VpnStatus | null>(null);
  const [vpnProfiles, setVpnProfiles] = React.useState<VpnProfile[]>([]);
  const [vpnLoading, setVpnLoading] = React.useState(true);
  const [vpnToggling, setVpnToggling] = React.useState(false);

  // Reports
  const [reports, setReports] = React.useState<SecurityReport[]>([]);
  const [reportsLoading, setReportsLoading] = React.useState(true);
  const [reportType, setReportType] = React.useState("vulnerability");
  const [generatingReport, setGeneratingReport] = React.useState(false);

  // -------------------------------------------------------------------------
  // Data fetching
  // -------------------------------------------------------------------------

  const loadHealth = React.useCallback(async () => {
    try {
      const data = await apiFetch<HealthStatus>("/api/v1/cybersec/health");
      setHealth(data);
    } catch {
      setHealth({ status: "unhealthy" });
    }
  }, []);

  const loadTools = React.useCallback(async () => {
    setToolsLoading(true);
    try {
      const data = await apiFetch<{ tools: SecurityTool[] }>("/api/v1/cybersec/tools");
      setTools(data.tools ?? []);
    } catch {
      toast.error("Failed to load security tools");
    } finally {
      setToolsLoading(false);
    }
  }, []);

  const loadScans = React.useCallback(async () => {
    try {
      const data = await apiFetch<{ operations: ScanOperation[] }>("/api/v1/cybersec/operations/scan", {
        method: "GET",
      });
      setScans(data.operations ?? []);
    } catch {
      /* silently fail - scans list endpoint may use different path */
    } finally {
      setScansLoading(false);
    }
  }, []);

  const loadVpn = React.useCallback(async () => {
    try {
      const [status, profiles] = await Promise.all([
        apiFetch<VpnStatus>("/api/v1/cybersec/network/vpn/status"),
        apiFetch<{ profiles: VpnProfile[] }>("/api/v1/cybersec/network/vpn/profiles"),
      ]);
      setVpnStatus(status);
      setVpnProfiles(profiles.profiles ?? []);
    } catch {
      setVpnStatus({ connected: false });
    } finally {
      setVpnLoading(false);
    }
  }, []);

  const loadReports = React.useCallback(async () => {
    try {
      const data = await apiFetch<{ reports: SecurityReport[] }>("/api/v1/cybersec/reports");
      setReports(data.reports ?? []);
    } catch {
      toast.error("Failed to load reports");
    } finally {
      setReportsLoading(false);
    }
  }, []);

  React.useEffect(() => {
    loadHealth();
    loadTools();
    loadScans();
    loadVpn();
    loadReports();
  }, [loadHealth, loadTools, loadScans, loadVpn, loadReports]);

  // -------------------------------------------------------------------------
  // Derived state
  // -------------------------------------------------------------------------

  const categories = React.useMemo(() => {
    const set = new Set(tools.map((t) => t.category));
    return ["all", ...Array.from(set).sort()];
  }, [tools]);

  const filteredTools = React.useMemo(() => {
    let list = tools;
    if (categoryFilter !== "all") list = list.filter((t) => t.category === categoryFilter);
    if (toolSearch) {
      const q = toolSearch.toLowerCase();
      list = list.filter(
        (t) => t.name.toLowerCase().includes(q) || t.description?.toLowerCase().includes(q),
      );
    }
    return list;
  }, [tools, categoryFilter, toolSearch]);

  // -------------------------------------------------------------------------
  // Actions
  // -------------------------------------------------------------------------

  const handleInstallTool = async (toolId: string) => {
    setInstallingTool(toolId);
    try {
      await apiFetch("/api/v1/cybersec/tools/install", {
        method: "POST",
        body: JSON.stringify({ tool_id: toolId }),
      });
      toast.success("Tool installed");
      loadTools();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Install failed");
    } finally {
      setInstallingTool(null);
    }
  };

  const handleExecuteTool = async (toolId: string) => {
    setExecutingTool(toolId);
    try {
      await apiFetch(`/api/v1/cybersec/tools/${toolId}/execute`, { method: "POST" });
      toast.success("Tool executed");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Execution failed");
    } finally {
      setExecutingTool(null);
    }
  };

  const handleLaunchScan = async () => {
    if (!scanTarget.trim()) return;
    setLaunchingScan(true);
    try {
      await apiFetch("/api/v1/cybersec/operations/scan", {
        method: "POST",
        body: JSON.stringify({ target: scanTarget, scan_type: scanType }),
      });
      toast.success("Scan launched");
      setScanTarget("");
      loadScans();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to launch scan");
    } finally {
      setLaunchingScan(false);
    }
  };

  const handleVpnToggle = async () => {
    setVpnToggling(true);
    try {
      const action = vpnStatus?.connected ? "disconnect" : "connect";
      await apiFetch(`/api/v1/cybersec/network/vpn/${action}`, { method: "POST" });
      toast.success(vpnStatus?.connected ? "Disconnected" : "Connected");
      loadVpn();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "VPN action failed");
    } finally {
      setVpnToggling(false);
    }
  };

  const handleGenerateReport = async () => {
    setGeneratingReport(true);
    try {
      await apiFetch("/api/v1/cybersec/reports/generate", {
        method: "POST",
        body: JSON.stringify({ type: reportType }),
      });
      toast.success("Report generation started");
      loadReports();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to generate report");
    } finally {
      setGeneratingReport(false);
    }
  };

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Cybersecurity</h1>
          <p className="text-muted-foreground">
            Security tools, scanning, VPN management, and reporting
          </p>
        </div>
        <div className="flex items-center gap-3">
          <HealthIndicator health={health} />
          <Button variant="outline" onClick={() => { loadHealth(); loadTools(); loadScans(); loadVpn(); loadReports(); }}>
            <RefreshCw className="size-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      <Tabs defaultValue="tools" className="space-y-4">
        <TabsList>
          <TabsTrigger value="tools">
            <Wrench className="size-3.5 mr-1.5" />
            Tools
          </TabsTrigger>
          <TabsTrigger value="scans">
            <Scan className="size-3.5 mr-1.5" />
            Scans
          </TabsTrigger>
          <TabsTrigger value="vpn">
            <Globe className="size-3.5 mr-1.5" />
            VPN
          </TabsTrigger>
          <TabsTrigger value="reports">
            <FileText className="size-3.5 mr-1.5" />
            Reports
          </TabsTrigger>
        </TabsList>

        {/* ================================================================ */}
        {/* Tools Tab */}
        {/* ================================================================ */}
        <TabsContent value="tools" className="space-y-4">
          <div className="flex items-center gap-3">
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
              <Input
                placeholder="Search tools…"
                className="pl-9"
                value={toolSearch}
                onChange={(e) => setToolSearch(e.target.value)}
              />
            </div>
            <Select value={categoryFilter} onValueChange={setCategoryFilter}>
              <SelectTrigger className="w-44">
                <SelectValue placeholder="Category" />
              </SelectTrigger>
              <SelectContent>
                {categories.map((cat) => (
                  <SelectItem key={cat} value={cat}>
                    {cat === "all" ? "All Categories" : cat}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {toolsLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <Skeleton key={i} className="h-36 w-full rounded-lg" />
              ))}
            </div>
          ) : filteredTools.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <Shield className="size-12 mx-auto mb-4 opacity-50" />
                <h3 className="text-lg font-semibold mb-2">No tools found</h3>
                <p className="text-muted-foreground">
                  {toolSearch || categoryFilter !== "all"
                    ? "Try adjusting your filters"
                    : "No security tools available"}
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredTools.map((tool) => (
                <Card key={tool.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-4 space-y-3">
                    <div className="flex items-start justify-between">
                      <div className="min-w-0">
                        <h4 className="font-semibold truncate">{tool.name}</h4>
                        {tool.description && (
                          <p className="text-xs text-muted-foreground line-clamp-2 mt-1">
                            {tool.description}
                          </p>
                        )}
                      </div>
                      <Badge variant={tool.installed ? "secondary" : "outline"} className="shrink-0 ml-2">
                        {tool.installed ? "Installed" : "Available"}
                      </Badge>
                    </div>

                    <div className="flex items-center gap-2 flex-wrap">
                      <Badge variant="outline" className="text-[10px]">{tool.category}</Badge>
                      {tool.version && (
                        <Badge variant="outline" className="text-[10px]">v{tool.version}</Badge>
                      )}
                    </div>

                    <div className="flex items-center gap-2">
                      {!tool.installed ? (
                        <Button
                          variant="outline"
                          size="sm"
                          className="h-7 text-xs gap-1"
                          onClick={() => handleInstallTool(tool.id)}
                          disabled={installingTool === tool.id}
                        >
                          {installingTool === tool.id ? (
                            <Loader2 className="size-3 animate-spin" />
                          ) : (
                            <Download className="size-3" />
                          )}
                          Install
                        </Button>
                      ) : (
                        <Button
                          variant="outline"
                          size="sm"
                          className="h-7 text-xs gap-1"
                          onClick={() => handleExecuteTool(tool.id)}
                          disabled={executingTool === tool.id}
                        >
                          {executingTool === tool.id ? (
                            <Loader2 className="size-3 animate-spin" />
                          ) : (
                            <Play className="size-3" />
                          )}
                          Execute
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        {/* ================================================================ */}
        {/* Scans Tab */}
        {/* ================================================================ */}
        <TabsContent value="scans" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Plus className="size-4" />
                Launch New Scan
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-end gap-3">
                <div className="flex-1 space-y-1.5">
                  <label className="text-xs font-medium">Target</label>
                  <Input
                    placeholder="192.168.1.0/24 or example.com"
                    value={scanTarget}
                    onChange={(e) => setScanTarget(e.target.value)}
                  />
                </div>
                <div className="w-48 space-y-1.5">
                  <label className="text-xs font-medium">Scan Type</label>
                  <Select value={scanType} onValueChange={setScanType}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="port_scan">Port Scan</SelectItem>
                      <SelectItem value="vulnerability">Vulnerability</SelectItem>
                      <SelectItem value="network_map">Network Map</SelectItem>
                      <SelectItem value="web_app">Web App</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Button onClick={handleLaunchScan} disabled={launchingScan || !scanTarget.trim()}>
                  {launchingScan ? (
                    <Loader2 className="size-4 mr-2 animate-spin" />
                  ) : (
                    <Scan className="size-4 mr-2" />
                  )}
                  Scan
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Scan History</CardTitle>
            </CardHeader>
            <CardContent>
              {scansLoading ? (
                <div className="space-y-3">
                  {[1, 2, 3].map((i) => <Skeleton key={i} className="h-12 w-full rounded-lg" />)}
                </div>
              ) : scans.length === 0 ? (
                <div className="py-12 text-center">
                  <Scan className="size-12 mx-auto mb-4 opacity-50" />
                  <h3 className="text-lg font-semibold mb-2">No scans yet</h3>
                  <p className="text-muted-foreground">Launch a scan above to get started</p>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>ID</TableHead>
                      <TableHead>Target</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Findings</TableHead>
                      <TableHead>Started</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {scans.map((scan) => (
                      <TableRow key={scan.id}>
                        <TableCell className="font-mono text-xs">{scan.id.slice(0, 10)}…</TableCell>
                        <TableCell className="font-mono text-sm">{scan.target}</TableCell>
                        <TableCell>
                          <Badge variant="outline">{scan.scan_type}</Badge>
                        </TableCell>
                        <TableCell>
                          <ScanStatusBadge status={scan.status} />
                        </TableCell>
                        <TableCell>{scan.findings_count ?? "—"}</TableCell>
                        <TableCell className="text-muted-foreground text-sm">
                          {new Date(scan.started_at).toLocaleString()}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* ================================================================ */}
        {/* VPN Tab */}
        {/* ================================================================ */}
        <TabsContent value="vpn" className="space-y-4">
          {vpnLoading ? (
            <div className="space-y-4">
              <Skeleton className="h-32 w-full rounded-lg" />
              <Skeleton className="h-48 w-full rounded-lg" />
            </div>
          ) : (
            <>
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-base">
                    <Activity className="size-4" />
                    Connection Status
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                        vpnStatus?.connected ? "bg-green-500/10" : "bg-muted"
                      }`}>
                        {vpnStatus?.connected ? (
                          <Wifi className="size-6 text-green-500" />
                        ) : (
                          <WifiOff className="size-6 text-muted-foreground" />
                        )}
                      </div>
                      <div>
                        <p className="font-semibold">
                          {vpnStatus?.connected ? "Connected" : "Disconnected"}
                        </p>
                        {vpnStatus?.connected && (
                          <div className="text-sm text-muted-foreground space-y-0.5">
                            {vpnStatus.profile && <p>Profile: {vpnStatus.profile}</p>}
                            {vpnStatus.ip && <p>IP: {vpnStatus.ip}</p>}
                            {vpnStatus.uptime_seconds != null && (
                              <p>Uptime: {Math.floor(vpnStatus.uptime_seconds / 60)}m</p>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                    <Button
                      variant={vpnStatus?.connected ? "destructive" : "default"}
                      onClick={handleVpnToggle}
                      disabled={vpnToggling}
                    >
                      {vpnToggling ? (
                        <Loader2 className="size-4 mr-2 animate-spin" />
                      ) : vpnStatus?.connected ? (
                        <WifiOff className="size-4 mr-2" />
                      ) : (
                        <Wifi className="size-4 mr-2" />
                      )}
                      {vpnStatus?.connected ? "Disconnect" : "Connect"}
                    </Button>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-base">VPN Profiles</CardTitle>
                </CardHeader>
                <CardContent>
                  {vpnProfiles.length === 0 ? (
                    <div className="py-8 text-center">
                      <Globe className="size-10 mx-auto mb-3 opacity-50" />
                      <p className="text-muted-foreground text-sm">No VPN profiles configured</p>
                    </div>
                  ) : (
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Name</TableHead>
                          <TableHead>Server</TableHead>
                          <TableHead>Protocol</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {vpnProfiles.map((profile) => (
                          <TableRow key={profile.id}>
                            <TableCell className="font-medium">{profile.name}</TableCell>
                            <TableCell className="font-mono text-sm">{profile.server}</TableCell>
                            <TableCell>
                              <Badge variant="outline">{profile.protocol}</Badge>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  )}
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>

        {/* ================================================================ */}
        {/* Reports Tab */}
        {/* ================================================================ */}
        <TabsContent value="reports" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Plus className="size-4" />
                Generate Report
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-end gap-3">
                <div className="w-56 space-y-1.5">
                  <label className="text-xs font-medium">Report Type</label>
                  <Select value={reportType} onValueChange={setReportType}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="vulnerability">Vulnerability</SelectItem>
                      <SelectItem value="compliance">Compliance</SelectItem>
                      <SelectItem value="network">Network</SelectItem>
                      <SelectItem value="executive">Executive Summary</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Button onClick={handleGenerateReport} disabled={generatingReport}>
                  {generatingReport ? (
                    <Loader2 className="size-4 mr-2 animate-spin" />
                  ) : (
                    <FileText className="size-4 mr-2" />
                  )}
                  Generate
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Generated Reports</CardTitle>
            </CardHeader>
            <CardContent>
              {reportsLoading ? (
                <div className="space-y-3">
                  {[1, 2, 3].map((i) => <Skeleton key={i} className="h-12 w-full rounded-lg" />)}
                </div>
              ) : reports.length === 0 ? (
                <div className="py-12 text-center">
                  <FileText className="size-12 mx-auto mb-4 opacity-50" />
                  <h3 className="text-lg font-semibold mb-2">No reports yet</h3>
                  <p className="text-muted-foreground">Generate a report above</p>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Title</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead>Created</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {reports.map((report) => (
                      <TableRow key={report.id}>
                        <TableCell className="font-medium">{report.title}</TableCell>
                        <TableCell>
                          <Badge variant="outline">{report.type}</Badge>
                        </TableCell>
                        <TableCell className="text-muted-foreground text-sm">
                          {new Date(report.created_at).toLocaleString()}
                        </TableCell>
                        <TableCell className="text-right">
                          {report.download_url && (
                            <Button variant="ghost" size="sm" className="h-7 text-xs gap-1" asChild>
                              <a href={report.download_url} download>
                                <Download className="size-3" />
                                Download
                              </a>
                            </Button>
                          )}
                        </TableCell>
                      </TableRow>
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
