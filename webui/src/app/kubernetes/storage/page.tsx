"use client";

import * as React from "react";
import {
  HardDrive,
  Folder,
  File,
  RefreshCw,
  Plus,
  Trash2,
  Download,
  Upload,
  ChevronRight,
  Home,
  Link as LinkIcon,
  CheckCircle,
  XCircle,
  Settings2,
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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { toast } from "sonner";
import {
  useStorageStatus,
  useStorageBuckets,
  useStorageObjects,
  useCreateBucket,
  useDeleteObject,
  useGetPresignedUrl,
  useTestMinioConnection,
} from "@/lib/api";

function formatBytes(bytes: number): string {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "-";
  return new Date(dateStr).toLocaleString();
}

export default function StoragePage() {
  const { data: status, isLoading: statusLoading, mutate: mutateStatus } = useStorageStatus();
  const { data: bucketsData, isLoading: bucketsLoading, mutate: mutateBuckets } = useStorageBuckets();

  const [selectedBucket, setSelectedBucket] = React.useState<string | null>(null);
  const [currentPrefix, setCurrentPrefix] = React.useState<string>("");
  const { data: objectsData, isLoading: objectsLoading, mutate: mutateObjects } = useStorageObjects(
    selectedBucket || "",
    currentPrefix || undefined
  );

  const [createBucketDialog, setCreateBucketDialog] = React.useState(false);
  const [newBucketName, setNewBucketName] = React.useState("");

  const { trigger: createBucket, isMutating: isCreating } = useCreateBucket();
  const { trigger: deleteObject, isMutating: isDeleting } = useDeleteObject();
  const { trigger: getPresignedUrl } = useGetPresignedUrl();
  const { trigger: testConnection, isMutating: isTesting } = useTestMinioConnection();

  const [cfgEndpoint, setCfgEndpoint] = React.useState("");
  const [cfgAccessKey, setCfgAccessKey] = React.useState("");
  const [cfgSecretKey, setCfgSecretKey] = React.useState("");
  const [cfgSecure, setCfgSecure] = React.useState(false);
  const [showConfig, setShowConfig] = React.useState(false);

  const isConnected = status?.connected ?? false;
  const [testResult, setTestResult] = React.useState<{
    connected: boolean;
    endpoint?: string;
    buckets?: string[];
    error?: string;
  } | null>(null);

  const handleTestConnection = async () => {
    setTestResult(null);
    try {
      const result = await testConnection({
        endpoint: cfgEndpoint || undefined,
        access_key: cfgAccessKey || undefined,
        secret_key: cfgSecretKey || undefined,
        secure: cfgSecure,
      });
      setTestResult(result);
      if (result.connected) {
        toast.success(`Connected! Found ${result.buckets?.length ?? 0} bucket(s)`);
      } else {
        toast.error(result.error || "Connection failed");
      }
    } catch {
      toast.error("Connection test failed");
    }
  };

  const handleApplyConnection = async () => {
    try {
      const result = await testConnection({
        endpoint: cfgEndpoint || undefined,
        access_key: cfgAccessKey || undefined,
        secret_key: cfgSecretKey || undefined,
        secure: cfgSecure,
        apply: true,
      });
      if (result.connected) {
        toast.success("Connection applied");
        setShowConfig(false);
        setTestResult(null);
        mutateStatus();
        mutateBuckets();
      } else {
        toast.error(result.error || "Failed to apply connection");
      }
    } catch {
      toast.error("Failed to apply connection");
    }
  };

  const handleCreateBucket = async () => {
    if (!newBucketName) return;

    try {
      await createBucket({ name: newBucketName });
      toast.success(`Created bucket: ${newBucketName}`);
      setCreateBucketDialog(false);
      setNewBucketName("");
      mutateBuckets();
    } catch (error) {
      toast.error("Failed to create bucket");
    }
  };

  const handleDeleteObject = async (objectName: string) => {
    if (!selectedBucket) return;
    if (!confirm(`Are you sure you want to delete ${objectName}?`)) return;

    try {
      await deleteObject({ bucket: selectedBucket, object_path: objectName });
      toast.success(`Deleted ${objectName}`);
      mutateObjects();
    } catch (error) {
      toast.error("Failed to delete object");
    }
  };

  const handleDownload = async (objectName: string) => {
    if (!selectedBucket) return;

    try {
      const result = await getPresignedUrl({ bucket: selectedBucket, object_path: objectName });
      window.open(result.url, "_blank");
    } catch (error) {
      toast.error("Failed to generate download URL");
    }
  };

  const navigateToFolder = (folderName: string) => {
    const newPrefix = currentPrefix ? `${currentPrefix}${folderName}` : folderName;
    setCurrentPrefix(newPrefix);
  };

  const navigateUp = () => {
    if (!currentPrefix) return;
    const parts = currentPrefix.split("/").filter(Boolean);
    parts.pop();
    setCurrentPrefix(parts.length > 0 ? parts.join("/") + "/" : "");
  };

  const breadcrumbParts = currentPrefix.split("/").filter(Boolean);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Object Storage</h1>
          <p className="text-muted-foreground">
            Browse and manage MinIO object storage
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={isConnected ? "default" : "destructive"}>
            {isConnected ? "Connected" : "Disconnected"}
          </Badge>
          <Button variant="outline" onClick={() => setShowConfig(!showConfig)}>
            <Settings2 className="size-4 mr-2" />
            Configure
          </Button>
          <Button variant="outline" onClick={() => { mutateStatus(); mutateBuckets(); mutateObjects(); }}>
            <RefreshCw className="size-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Connection Status */}
      {!isConnected && !statusLoading && (
        <Card className="border-destructive bg-destructive/5">
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <XCircle className="size-8 text-destructive" />
              <div>
                <h3 className="font-semibold">Storage Not Connected</h3>
                <p className="text-sm text-muted-foreground">
                  {status?.error || "Configure MinIO connection in Settings to enable storage management."}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Connection Configuration */}
      {showConfig && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <Settings2 className="size-4" />
              MinIO Connection
            </CardTitle>
            <CardDescription>
              Test and apply a new MinIO endpoint configuration
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <Label>Endpoint (host:port)</Label>
                <Input
                  placeholder="localhost:9000"
                  value={cfgEndpoint}
                  onChange={e => setCfgEndpoint(e.target.value)}
                />
              </div>
              <div className="space-y-1.5">
                <Label>Access Key</Label>
                <Input
                  placeholder="minioadmin"
                  value={cfgAccessKey}
                  onChange={e => setCfgAccessKey(e.target.value)}
                />
              </div>
              <div className="space-y-1.5">
                <Label>Secret Key</Label>
                <Input
                  type="password"
                  placeholder="secret"
                  value={cfgSecretKey}
                  onChange={e => setCfgSecretKey(e.target.value)}
                />
              </div>
              <div className="flex items-end gap-2 pb-0.5">
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={cfgSecure}
                    onChange={e => setCfgSecure(e.target.checked)}
                    className="rounded"
                  />
                  Use HTTPS
                </label>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" onClick={handleTestConnection} disabled={isTesting}>
                {isTesting ? <Loader2 className="size-4 mr-2 animate-spin" /> : <CheckCircle className="size-4 mr-2" />}
                Test Connection
              </Button>
              {testResult?.connected && (
                <Button onClick={handleApplyConnection} disabled={isTesting}>
                  Apply &amp; Use This Connection
                </Button>
              )}
              <Button variant="ghost" onClick={() => { setShowConfig(false); setTestResult(null); }}>
                Cancel
              </Button>
            </div>
            {testResult && (
              <div className={`rounded-lg border p-3 text-sm ${testResult.connected ? "border-green-200 bg-green-50 dark:border-green-900 dark:bg-green-950" : "border-red-200 bg-red-50 dark:border-red-900 dark:bg-red-950"}`}>
                {testResult.connected ? (
                  <div className="space-y-1">
                    <div className="flex items-center gap-2 font-medium text-green-700 dark:text-green-400">
                      <CheckCircle className="size-4" />
                      Connected to {testResult.endpoint}
                    </div>
                    <p className="text-green-600 dark:text-green-500">
                      Found {testResult.buckets?.length ?? 0} bucket(s): {testResult.buckets?.join(", ") || "none"}
                    </p>
                  </div>
                ) : (
                  <div className="flex items-center gap-2 text-red-700 dark:text-red-400">
                    <XCircle className="size-4" />
                    {testResult.error}
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {isConnected && (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Buckets List */}
          <Card className="lg:col-span-1">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-base">Buckets</CardTitle>
                <Button size="sm" variant="ghost" onClick={() => setCreateBucketDialog(true)}>
                  <Plus className="size-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {bucketsLoading ? (
                <div className="space-y-2">
                  {[1, 2, 3].map((i) => (
                    <Skeleton key={i} className="h-10 w-full" />
                  ))}
                </div>
              ) : bucketsData?.buckets && bucketsData.buckets.length > 0 ? (
                <div className="space-y-1">
                  {bucketsData.buckets.map((bucket) => (
                    <button
                      key={bucket}
                      onClick={() => {
                        setSelectedBucket(bucket);
                        setCurrentPrefix("");
                      }}
                      className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-left text-sm transition-colors ${
                        selectedBucket === bucket
                          ? "bg-primary text-primary-foreground"
                          : "hover:bg-muted"
                      }`}
                    >
                      <HardDrive className="size-4" />
                      <span className="truncate">{bucket}</span>
                    </button>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No buckets found
                </p>
              )}
            </CardContent>
          </Card>

          {/* Objects Browser */}
          <Card className="lg:col-span-3">
            <CardHeader>
              <CardTitle className="text-base">
                {selectedBucket ? `${selectedBucket}` : "Select a bucket"}
              </CardTitle>
              {selectedBucket && (
                <Breadcrumb>
                  <BreadcrumbList>
                    <BreadcrumbItem>
                      <BreadcrumbLink
                        className="cursor-pointer"
                        onClick={() => setCurrentPrefix("")}
                      >
                        <Home className="size-4" />
                      </BreadcrumbLink>
                    </BreadcrumbItem>
                    {breadcrumbParts.map((part, index) => (
                      <React.Fragment key={index}>
                        <BreadcrumbSeparator />
                        <BreadcrumbItem>
                          <BreadcrumbLink
                            className="cursor-pointer"
                            onClick={() => {
                              const newPrefix = breadcrumbParts.slice(0, index + 1).join("/") + "/";
                              setCurrentPrefix(newPrefix);
                            }}
                          >
                            {part}
                          </BreadcrumbLink>
                        </BreadcrumbItem>
                      </React.Fragment>
                    ))}
                  </BreadcrumbList>
                </Breadcrumb>
              )}
            </CardHeader>
            <CardContent>
              {!selectedBucket ? (
                <div className="text-center py-12 text-muted-foreground">
                  <HardDrive className="size-12 mx-auto mb-4 opacity-50" />
                  <p>Select a bucket to browse objects</p>
                </div>
              ) : objectsLoading ? (
                <div className="space-y-2">
                  {[1, 2, 3].map((i) => (
                    <Skeleton key={i} className="h-12 w-full" />
                  ))}
                </div>
              ) : objectsData?.objects && objectsData.objects.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Size</TableHead>
                      <TableHead>Modified</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {currentPrefix && (
                      <TableRow className="cursor-pointer hover:bg-muted" onClick={navigateUp}>
                        <TableCell className="font-medium">
                          <div className="flex items-center gap-2">
                            <Folder className="size-4 text-muted-foreground" />
                            ..
                          </div>
                        </TableCell>
                        <TableCell>-</TableCell>
                        <TableCell>-</TableCell>
                        <TableCell></TableCell>
                      </TableRow>
                    )}
                    {objectsData.objects.map((obj) => (
                      <TableRow
                        key={obj.name}
                        className={obj.is_dir ? "cursor-pointer hover:bg-muted" : ""}
                        onClick={() => obj.is_dir && navigateToFolder(obj.name.replace(currentPrefix, ""))}
                      >
                        <TableCell className="font-medium">
                          <div className="flex items-center gap-2">
                            {obj.is_dir ? (
                              <Folder className="size-4 text-blue-500" />
                            ) : (
                              <File className="size-4 text-muted-foreground" />
                            )}
                            <span className="truncate max-w-[300px]">
                              {obj.name.replace(currentPrefix, "")}
                            </span>
                          </div>
                        </TableCell>
                        <TableCell>{obj.is_dir ? "-" : formatBytes(obj.size)}</TableCell>
                        <TableCell className="text-xs text-muted-foreground">
                          {formatDate(obj.last_modified)}
                        </TableCell>
                        <TableCell className="text-right">
                          {!obj.is_dir && (
                            <div className="flex items-center justify-end gap-1">
                              <Button
                                variant="ghost"
                                size="icon"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleDownload(obj.name);
                                }}
                              >
                                <Download className="size-4" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="icon"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleDeleteObject(obj.name);
                                }}
                              >
                                <Trash2 className="size-4 text-destructive" />
                              </Button>
                            </div>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="text-center py-12 text-muted-foreground">
                  <Folder className="size-12 mx-auto mb-4 opacity-50" />
                  <p>No objects in this location</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Create Bucket Dialog */}
      <Dialog open={createBucketDialog} onOpenChange={setCreateBucketDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create Bucket</DialogTitle>
            <DialogDescription>
              Create a new storage bucket
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Label htmlFor="bucket-name">Bucket Name</Label>
            <Input
              id="bucket-name"
              placeholder="my-bucket"
              value={newBucketName}
              onChange={(e) => setNewBucketName(e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, "-"))}
              className="mt-2"
            />
            <p className="text-xs text-muted-foreground mt-2">
              Bucket names must be lowercase and can only contain letters, numbers, and hyphens.
            </p>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCreateBucketDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreateBucket} disabled={isCreating || !newBucketName}>
              Create
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
