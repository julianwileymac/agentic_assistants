"use client";

import * as React from "react";
import {
  Upload,
  FileText,
  Link,
  Github,
  Cloud,
  Search,
  RefreshCw,
  Loader2,
  CheckCircle2,
  XCircle,
  Clock,
  FolderUp,
  X,
  FileType,
  UploadCloud,
  ExternalLink,
  GitBranch,
  HardDrive,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { toast } from "sonner";
import { apiFetch } from "@/lib/api";
import { getBackendUrl } from "@/lib/api-client";

interface UploadJob {
  job_id: string;
  status: "pending" | "processing" | "completed" | "failed";
  filename?: string;
  source?: string;
  progress?: number;
  error?: string;
  created_at?: string;
}

interface SupportedFormat {
  extension: string;
  mime_type: string;
  category: string;
}

const statusConfig: Record<
  string,
  { icon: React.ElementType; color: string; bg: string }
> = {
  pending: { icon: Clock, color: "text-muted-foreground", bg: "bg-muted" },
  processing: { icon: Loader2, color: "text-blue-500", bg: "bg-blue-500/10" },
  completed: {
    icon: CheckCircle2,
    color: "text-green-500",
    bg: "bg-green-500/10",
  },
  failed: { icon: XCircle, color: "text-red-500", bg: "bg-red-500/10" },
};

export default function UploadPage() {
  const [jobs, setJobs] = React.useState<UploadJob[]>([]);
  const [supportedFormats, setSupportedFormats] = React.useState<
    SupportedFormat[]
  >([]);
  const [loadingFormats, setLoadingFormats] = React.useState(true);

  // File upload state
  const [dragActive, setDragActive] = React.useState(false);
  const [selectedFiles, setSelectedFiles] = React.useState<File[]>([]);
  const [uploading, setUploading] = React.useState(false);
  const [uploadProgress, setUploadProgress] = React.useState(0);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  // URL fetch state
  const [fetchUrl, setFetchUrl] = React.useState("");
  const [fetchingUrl, setFetchingUrl] = React.useState(false);

  // GitHub state
  const [ghRepoUrl, setGhRepoUrl] = React.useState("");
  const [ghBranch, setGhBranch] = React.useState("main");
  const [ghPath, setGhPath] = React.useState("");
  const [importingGh, setImportingGh] = React.useState(false);

  // S3 state
  const [s3Bucket, setS3Bucket] = React.useState("");
  const [s3Key, setS3Key] = React.useState("");
  const [s3Endpoint, setS3Endpoint] = React.useState("");
  const [importingS3, setImportingS3] = React.useState(false);

  const loadFormats = React.useCallback(async () => {
    setLoadingFormats(true);
    try {
      const data = await apiFetch<
        SupportedFormat[] | { formats: SupportedFormat[] }
      >("/api/v1/upload/supported-formats");
      setSupportedFormats(
        Array.isArray(data) ? data : data.formats ?? []
      );
    } catch {
      setSupportedFormats([]);
    } finally {
      setLoadingFormats(false);
    }
  }, []);

  const pollJobStatus = React.useCallback(async (jobId: string) => {
    try {
      const data = await apiFetch<UploadJob>(
        `/api/v1/upload/status/${jobId}`
      );
      setJobs((prev) => {
        const idx = prev.findIndex((j) => j.job_id === jobId);
        if (idx >= 0) {
          const next = [...prev];
          next[idx] = data;
          return next;
        }
        return [data, ...prev];
      });
      if (data.status === "processing" || data.status === "pending") {
        setTimeout(() => pollJobStatus(jobId), 2000);
      }
    } catch {
      /* polling error */
    }
  }, []);

  React.useEffect(() => {
    loadFormats();
  }, [loadFormats]);

  // Drag-and-drop handlers
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files?.length) {
      setSelectedFiles((prev) => [
        ...prev,
        ...Array.from(e.dataTransfer.files),
      ]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.length) {
      setSelectedFiles((prev) => [
        ...prev,
        ...Array.from(e.target.files!),
      ]);
    }
  };

  const removeFile = (index: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleUploadFiles = async () => {
    if (selectedFiles.length === 0) return;
    setUploading(true);
    setUploadProgress(0);

    try {
      const baseUrl = getBackendUrl();
      const isMulti = selectedFiles.length > 1;
      const formData = new FormData();

      if (isMulti) {
        selectedFiles.forEach((f) => formData.append("files", f));
      } else {
        formData.append("file", selectedFiles[0]);
      }

      const endpoint = isMulti
        ? "/api/v1/upload/files"
        : "/api/v1/upload/file";

      const xhr = new XMLHttpRequest();
      xhr.open("POST", `${baseUrl}${endpoint}`);

      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable) {
          setUploadProgress(Math.round((e.loaded / e.total) * 100));
        }
      };

      const result = await new Promise<UploadJob>((resolve, reject) => {
        xhr.onload = () => {
          if (xhr.status >= 200 && xhr.status < 300) {
            resolve(JSON.parse(xhr.responseText));
          } else {
            reject(new Error(`Upload failed: ${xhr.status}`));
          }
        };
        xhr.onerror = () => reject(new Error("Network error"));
        xhr.send(formData);
      });

      toast.success("Upload started");
      setJobs((prev) => [result, ...prev]);
      setSelectedFiles([]);
      setUploadProgress(0);

      if (result.job_id) {
        pollJobStatus(result.job_id);
      }
    } catch (err) {
      toast.error(`Upload failed: ${err}`);
    } finally {
      setUploading(false);
    }
  };

  const handleFetchUrl = async () => {
    if (!fetchUrl.trim()) return;
    setFetchingUrl(true);
    try {
      const result = await apiFetch<UploadJob>("/api/v1/upload/fetch/url", {
        method: "POST",
        body: JSON.stringify({ url: fetchUrl }),
      });
      toast.success("URL fetch started");
      setJobs((prev) => [result, ...prev]);
      setFetchUrl("");
      if (result.job_id) pollJobStatus(result.job_id);
    } catch (err) {
      toast.error(`Failed: ${err}`);
    } finally {
      setFetchingUrl(false);
    }
  };

  const handleGithubImport = async () => {
    if (!ghRepoUrl.trim()) return;
    setImportingGh(true);
    try {
      const result = await apiFetch<UploadJob>(
        "/api/v1/upload/fetch/github",
        {
          method: "POST",
          body: JSON.stringify({
            repo_url: ghRepoUrl,
            branch: ghBranch || "main",
            path: ghPath || undefined,
          }),
        }
      );
      toast.success("GitHub import started");
      setJobs((prev) => [result, ...prev]);
      setGhRepoUrl("");
      setGhPath("");
      if (result.job_id) pollJobStatus(result.job_id);
    } catch (err) {
      toast.error(`Failed: ${err}`);
    } finally {
      setImportingGh(false);
    }
  };

  const handleS3Import = async () => {
    if (!s3Bucket.trim() || !s3Key.trim()) return;
    setImportingS3(true);
    try {
      const result = await apiFetch<UploadJob>("/api/v1/upload/fetch/s3", {
        method: "POST",
        body: JSON.stringify({
          bucket: s3Bucket,
          key: s3Key,
          endpoint: s3Endpoint || undefined,
        }),
      });
      toast.success("S3 import started");
      setJobs((prev) => [result, ...prev]);
      setS3Bucket("");
      setS3Key("");
      if (result.job_id) pollJobStatus(result.job_id);
    } catch (err) {
      toast.error(`Failed: ${err}`);
    } finally {
      setImportingS3(false);
    }
  };

  const formatCategories = React.useMemo(() => {
    const map = new Map<string, SupportedFormat[]>();
    supportedFormats.forEach((f) => {
      const group = map.get(f.category) ?? [];
      group.push(f);
      map.set(f.category, group);
    });
    return map;
  }, [supportedFormats]);

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Upload &amp; Import
          </h1>
          <p className="text-muted-foreground">
            Upload files or import from external sources into the knowledge
            base
          </p>
        </div>
        <Button variant="outline" onClick={loadFormats}>
          <RefreshCw className="size-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="file">
        <TabsList>
          <TabsTrigger value="file">
            <FolderUp className="size-4 mr-1.5" />
            File Upload
          </TabsTrigger>
          <TabsTrigger value="url">
            <Link className="size-4 mr-1.5" />
            URL Fetch
          </TabsTrigger>
          <TabsTrigger value="github">
            <Github className="size-4 mr-1.5" />
            GitHub Import
          </TabsTrigger>
          <TabsTrigger value="s3">
            <Cloud className="size-4 mr-1.5" />
            S3 Import
          </TabsTrigger>
        </TabsList>

        {/* File Upload Tab */}
        <TabsContent value="file" className="space-y-4">
          <Card>
            <CardContent className="p-6 space-y-4">
              {/* Drag-and-drop zone */}
              <div
                className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                  dragActive
                    ? "border-primary bg-primary/5"
                    : "border-muted-foreground/25 hover:border-muted-foreground/50"
                }`}
                onDragEnter={handleDrag}
                onDragOver={handleDrag}
                onDragLeave={handleDrag}
                onDrop={handleDrop}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  className="hidden"
                  onChange={handleFileSelect}
                />
                <UploadCloud className="size-10 mx-auto mb-3 text-muted-foreground" />
                <p className="font-medium mb-1">
                  Drag &amp; drop files here
                </p>
                <p className="text-sm text-muted-foreground mb-3">
                  or click to browse
                </p>
                <Button
                  variant="outline"
                  onClick={() => fileInputRef.current?.click()}
                >
                  Browse Files
                </Button>
              </div>

              {/* Selected files */}
              {selectedFiles.length > 0 && (
                <div className="space-y-2">
                  <p className="text-sm font-medium">
                    {selectedFiles.length} file
                    {selectedFiles.length !== 1 && "s"} selected
                  </p>
                  <div className="space-y-1 max-h-48 overflow-y-auto">
                    {selectedFiles.map((file, idx) => (
                      <div
                        key={`${file.name}-${idx}`}
                        className="flex items-center justify-between px-3 py-2 bg-muted rounded-md"
                      >
                        <div className="flex items-center gap-2 min-w-0">
                          <FileText className="size-4 text-muted-foreground shrink-0" />
                          <span className="text-sm truncate">
                            {file.name}
                          </span>
                          <Badge variant="outline" className="text-[10px] shrink-0">
                            {formatSize(file.size)}
                          </Badge>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-6 w-6 p-0 shrink-0"
                          onClick={() => removeFile(idx)}
                        >
                          <X className="size-3" />
                        </Button>
                      </div>
                    ))}
                  </div>

                  {uploading && (
                    <div className="space-y-1">
                      <Progress value={uploadProgress} />
                      <p className="text-xs text-muted-foreground text-right">
                        {uploadProgress}%
                      </p>
                    </div>
                  )}

                  <Button
                    onClick={handleUploadFiles}
                    disabled={uploading}
                    className="w-full"
                  >
                    {uploading ? (
                      <Loader2 className="size-4 mr-2 animate-spin" />
                    ) : (
                      <Upload className="size-4 mr-2" />
                    )}
                    Upload {selectedFiles.length} File
                    {selectedFiles.length !== 1 && "s"}
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* URL Fetch Tab */}
        <TabsContent value="url" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <ExternalLink className="size-4" />
                Fetch from URL
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="fetch-url">URL</Label>
                <div className="flex gap-2">
                  <Input
                    id="fetch-url"
                    placeholder="https://example.com/document.pdf"
                    value={fetchUrl}
                    onChange={(e) => setFetchUrl(e.target.value)}
                    onKeyDown={(e) =>
                      e.key === "Enter" && handleFetchUrl()
                    }
                  />
                  <Button
                    onClick={handleFetchUrl}
                    disabled={!fetchUrl.trim() || fetchingUrl}
                  >
                    {fetchingUrl ? (
                      <Loader2 className="size-4 animate-spin" />
                    ) : (
                      "Fetch"
                    )}
                  </Button>
                </div>
              </div>
              <p className="text-xs text-muted-foreground">
                Fetches content from a URL and ingests it into the knowledge
                base. Supports web pages, PDFs, and other document formats.
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        {/* GitHub Import Tab */}
        <TabsContent value="github" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Github className="size-4" />
                Import from GitHub
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="gh-repo">Repository URL</Label>
                <Input
                  id="gh-repo"
                  placeholder="https://github.com/owner/repo"
                  value={ghRepoUrl}
                  onChange={(e) => setGhRepoUrl(e.target.value)}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="gh-branch">Branch</Label>
                  <div className="relative">
                    <GitBranch className="absolute left-3 top-1/2 -translate-y-1/2 size-3.5 text-muted-foreground" />
                    <Input
                      id="gh-branch"
                      placeholder="main"
                      className="pl-9"
                      value={ghBranch}
                      onChange={(e) => setGhBranch(e.target.value)}
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="gh-path">
                    Path Filter{" "}
                    <span className="text-muted-foreground font-normal">
                      (optional)
                    </span>
                  </Label>
                  <Input
                    id="gh-path"
                    placeholder="docs/"
                    value={ghPath}
                    onChange={(e) => setGhPath(e.target.value)}
                  />
                </div>
              </div>
              <Button
                onClick={handleGithubImport}
                disabled={!ghRepoUrl.trim() || importingGh}
                className="w-full"
              >
                {importingGh ? (
                  <Loader2 className="size-4 mr-2 animate-spin" />
                ) : (
                  <Github className="size-4 mr-2" />
                )}
                Import Repository
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* S3 Import Tab */}
        <TabsContent value="s3" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <HardDrive className="size-4" />
                Import from S3
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="s3-bucket">Bucket</Label>
                  <Input
                    id="s3-bucket"
                    placeholder="my-bucket"
                    value={s3Bucket}
                    onChange={(e) => setS3Bucket(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="s3-key">Key / Prefix</Label>
                  <Input
                    id="s3-key"
                    placeholder="data/documents/"
                    value={s3Key}
                    onChange={(e) => setS3Key(e.target.value)}
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="s3-endpoint">
                  Custom Endpoint{" "}
                  <span className="text-muted-foreground font-normal">
                    (optional, for MinIO etc.)
                  </span>
                </Label>
                <Input
                  id="s3-endpoint"
                  placeholder="https://minio.example.com"
                  value={s3Endpoint}
                  onChange={(e) => setS3Endpoint(e.target.value)}
                />
              </div>
              <Button
                onClick={handleS3Import}
                disabled={
                  !s3Bucket.trim() || !s3Key.trim() || importingS3
                }
                className="w-full"
              >
                {importingS3 ? (
                  <Loader2 className="size-4 mr-2 animate-spin" />
                ) : (
                  <Cloud className="size-4 mr-2" />
                )}
                Import from S3
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Job Status Section */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Upload Jobs</CardTitle>
        </CardHeader>
        <CardContent>
          {jobs.length === 0 ? (
            <div className="text-center py-8">
              <Upload className="size-10 mx-auto mb-3 opacity-40" />
              <p className="text-sm text-muted-foreground">
                No upload jobs yet. Upload a file or import from a source to
                get started.
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {jobs.map((job) => {
                const cfg =
                  statusConfig[job.status] ?? statusConfig.pending;
                const Icon = cfg.icon;
                return (
                  <div
                    key={job.job_id}
                    className="flex items-center justify-between px-3 py-2.5 bg-muted/50 rounded-md"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <div
                        className={`w-8 h-8 rounded-md flex items-center justify-center shrink-0 ${cfg.bg}`}
                      >
                        <Icon
                          className={`size-4 ${cfg.color} ${
                            job.status === "processing"
                              ? "animate-spin"
                              : ""
                          }`}
                        />
                      </div>
                      <div className="min-w-0">
                        <p className="text-sm font-medium truncate">
                          {job.filename ?? job.source ?? job.job_id}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {job.status}
                          {job.error && ` — ${job.error}`}
                        </p>
                      </div>
                    </div>
                    {job.progress != null &&
                      job.status === "processing" && (
                        <div className="w-24 shrink-0 ml-2">
                          <Progress value={job.progress} className="h-1.5" />
                        </div>
                      )}
                    <Badge
                      variant={
                        job.status === "completed"
                          ? "secondary"
                          : job.status === "failed"
                            ? "destructive"
                            : "outline"
                      }
                      className="ml-2 shrink-0"
                    >
                      {job.status}
                    </Badge>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Supported Formats */}
      <Card className="bg-muted/50">
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <FileType className="size-4" />
            Supported Formats
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loadingFormats ? (
            <div className="flex gap-2">
              {[1, 2, 3, 4].map((i) => (
                <Skeleton key={i} className="h-6 w-16 rounded" />
              ))}
            </div>
          ) : supportedFormats.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              Format information unavailable. Start the backend to see
              supported formats.
            </p>
          ) : (
            <div className="space-y-3">
              {Array.from(formatCategories.entries()).map(
                ([category, formats]) => (
                  <div key={category}>
                    <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1.5">
                      {category}
                    </p>
                    <div className="flex flex-wrap gap-1">
                      {formats.map((f) => (
                        <Badge
                          key={f.extension}
                          variant="secondary"
                          className="text-xs"
                        >
                          {f.extension}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
