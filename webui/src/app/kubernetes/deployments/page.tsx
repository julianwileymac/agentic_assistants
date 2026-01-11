"use client";

import * as React from "react";
import {
  Layers,
  Plus,
  RefreshCw,
  MoreHorizontal,
  Play,
  Pause,
  Trash2,
  Scale,
  RotateCcw,
  FileText,
  CheckCircle,
  XCircle,
  Clock,
  Loader2,
} from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";
import {
  useKubernetesDeployments,
  useScaleDeployment,
  useDeleteDeployment,
  useRestartDeployment,
  useDeploymentLogs,
} from "@/lib/api";

function StatusBadge({ status }: { status: string }) {
  const variants: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
    Running: "default",
    Pending: "secondary",
    Scaling: "secondary",
    Updating: "secondary",
    Failed: "destructive",
    Unknown: "outline",
  };

  const icons: Record<string, React.ReactNode> = {
    Running: <CheckCircle className="size-3" />,
    Pending: <Clock className="size-3" />,
    Scaling: <Loader2 className="size-3 animate-spin" />,
    Updating: <Loader2 className="size-3 animate-spin" />,
    Failed: <XCircle className="size-3" />,
  };

  return (
    <Badge variant={variants[status] || "outline"} className="gap-1">
      {icons[status]}
      {status}
    </Badge>
  );
}

function TypeBadge({ type }: { type: string | null }) {
  if (!type) return null;

  const colors: Record<string, string> = {
    agent: "bg-blue-500/10 text-blue-500",
    flow: "bg-purple-500/10 text-purple-500",
    model: "bg-orange-500/10 text-orange-500",
    custom: "bg-gray-500/10 text-gray-500",
  };

  return (
    <span className={`px-2 py-0.5 rounded text-xs font-medium ${colors[type] || colors.custom}`}>
      {type}
    </span>
  );
}

export default function DeploymentsPage() {
  const [namespace, setNamespace] = React.useState<string | undefined>(undefined);
  const [deploymentType, setDeploymentType] = React.useState<string | undefined>(undefined);
  const { data: deployments, isLoading, mutate } = useKubernetesDeployments({
    namespace,
    deployment_type: deploymentType,
  });

  const [scaleDialog, setScaleDialog] = React.useState<{
    open: boolean;
    name: string;
    namespace: string;
    current: number;
  }>({ open: false, name: "", namespace: "", current: 1 });
  const [scaleValue, setScaleValue] = React.useState(1);

  const [logsDialog, setLogsDialog] = React.useState<{
    open: boolean;
    name: string;
    namespace: string;
  }>({ open: false, name: "", namespace: "" });
  const [logs, setLogs] = React.useState<string>("");

  const { trigger: scaleDeployment, isMutating: isScaling } = useScaleDeployment();
  const { trigger: deleteDeployment, isMutating: isDeleting } = useDeleteDeployment();
  const { trigger: restartDeployment, isMutating: isRestarting } = useRestartDeployment();
  const { trigger: fetchLogs } = useDeploymentLogs();

  const handleScale = async () => {
    try {
      await scaleDeployment({
        namespace: scaleDialog.namespace,
        name: scaleDialog.name,
        replicas: scaleValue,
      });
      toast.success(`Scaled ${scaleDialog.name} to ${scaleValue} replicas`);
      setScaleDialog({ ...scaleDialog, open: false });
      mutate();
    } catch (error) {
      toast.error("Failed to scale deployment");
    }
  };

  const handleDelete = async (name: string, namespace: string) => {
    if (!confirm(`Are you sure you want to delete ${name}?`)) return;

    try {
      await deleteDeployment({ namespace, name });
      toast.success(`Deleted ${name}`);
      mutate();
    } catch (error) {
      toast.error("Failed to delete deployment");
    }
  };

  const handleRestart = async (name: string, namespace: string) => {
    try {
      await restartDeployment({ namespace, name });
      toast.success(`Restarted ${name}`);
      mutate();
    } catch (error) {
      toast.error("Failed to restart deployment");
    }
  };

  const handleViewLogs = async (name: string, namespace: string) => {
    setLogsDialog({ open: true, name, namespace });
    try {
      const result = await fetchLogs({ namespace, name, tail_lines: 200 });
      setLogs(result.logs || "No logs available");
    } catch (error) {
      setLogs("Failed to fetch logs");
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Deployments</h1>
          <p className="text-muted-foreground">
            Manage Kubernetes deployments for agents, flows, and models
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={() => mutate()}>
            <RefreshCw className="size-4 mr-2" />
            Refresh
          </Button>
          <Button>
            <Plus className="size-4 mr-2" />
            New Deployment
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center gap-4">
            <div className="w-48">
              <Label className="text-xs text-muted-foreground">Namespace</Label>
              <Select value={namespace || "all"} onValueChange={(v) => setNamespace(v === "all" ? undefined : v)}>
                <SelectTrigger>
                  <SelectValue placeholder="All namespaces" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All namespaces</SelectItem>
                  <SelectItem value="agentic-workloads">agentic-workloads</SelectItem>
                  <SelectItem value="model-serving">model-serving</SelectItem>
                  <SelectItem value="default">default</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="w-48">
              <Label className="text-xs text-muted-foreground">Type</Label>
              <Select value={deploymentType || "all"} onValueChange={(v) => setDeploymentType(v === "all" ? undefined : v)}>
                <SelectTrigger>
                  <SelectValue placeholder="All types" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All types</SelectItem>
                  <SelectItem value="agent">Agents</SelectItem>
                  <SelectItem value="flow">Flows</SelectItem>
                  <SelectItem value="model">Models</SelectItem>
                  <SelectItem value="custom">Custom</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Deployments Table */}
      <Card>
        <CardHeader>
          <CardTitle>Active Deployments</CardTitle>
          <CardDescription>
            {deployments?.length || 0} deployment(s) managed by Agentic
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-16 w-full" />
              ))}
            </div>
          ) : deployments && deployments.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Namespace</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Replicas</TableHead>
                  <TableHead>Image</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {deployments.map((deployment) => (
                  <TableRow key={`${deployment.namespace}-${deployment.name}`}>
                    <TableCell className="font-medium">{deployment.name}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{deployment.namespace}</Badge>
                    </TableCell>
                    <TableCell>
                      <TypeBadge type={deployment.deployment_type} />
                    </TableCell>
                    <TableCell>
                      <StatusBadge status={deployment.status} />
                    </TableCell>
                    <TableCell>
                      {deployment.ready_replicas}/{deployment.replicas}
                    </TableCell>
                    <TableCell className="max-w-[200px] truncate text-xs text-muted-foreground">
                      {deployment.image}
                    </TableCell>
                    <TableCell className="text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon">
                            <MoreHorizontal className="size-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem
                            onClick={() => {
                              setScaleValue(deployment.replicas);
                              setScaleDialog({
                                open: true,
                                name: deployment.name,
                                namespace: deployment.namespace,
                                current: deployment.replicas,
                              });
                            }}
                          >
                            <Scale className="size-4 mr-2" />
                            Scale
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            onClick={() => handleRestart(deployment.name, deployment.namespace)}
                          >
                            <RotateCcw className="size-4 mr-2" />
                            Restart
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            onClick={() => handleViewLogs(deployment.name, deployment.namespace)}
                          >
                            <FileText className="size-4 mr-2" />
                            View Logs
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem
                            className="text-destructive"
                            onClick={() => handleDelete(deployment.name, deployment.namespace)}
                          >
                            <Trash2 className="size-4 mr-2" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="text-center py-12 text-muted-foreground">
              <Layers className="size-12 mx-auto mb-4 opacity-50" />
              <p>No deployments found</p>
              <p className="text-sm">Deploy an agent or flow to get started</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Scale Dialog */}
      <Dialog open={scaleDialog.open} onOpenChange={(open) => setScaleDialog({ ...scaleDialog, open })}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Scale Deployment</DialogTitle>
            <DialogDescription>
              Adjust the number of replicas for {scaleDialog.name}
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Label htmlFor="replicas">Replicas</Label>
            <Input
              id="replicas"
              type="number"
              min={0}
              max={10}
              value={scaleValue}
              onChange={(e) => setScaleValue(parseInt(e.target.value) || 0)}
              className="mt-2"
            />
            <p className="text-xs text-muted-foreground mt-2">
              Current: {scaleDialog.current} replica(s)
            </p>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setScaleDialog({ ...scaleDialog, open: false })}>
              Cancel
            </Button>
            <Button onClick={handleScale} disabled={isScaling}>
              {isScaling ? <Loader2 className="size-4 mr-2 animate-spin" /> : null}
              Scale
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Logs Dialog */}
      <Dialog open={logsDialog.open} onOpenChange={(open) => setLogsDialog({ ...logsDialog, open })}>
        <DialogContent className="max-w-4xl max-h-[80vh]">
          <DialogHeader>
            <DialogTitle>Logs: {logsDialog.name}</DialogTitle>
            <DialogDescription>
              Recent logs from {logsDialog.namespace}/{logsDialog.name}
            </DialogDescription>
          </DialogHeader>
          <div className="bg-black rounded-lg p-4 overflow-auto max-h-[50vh]">
            <pre className="text-xs text-green-400 font-mono whitespace-pre-wrap">
              {logs || "Loading..."}
            </pre>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setLogsDialog({ ...logsDialog, open: false })}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
