"use client";

import * as React from "react";
import {
  Upload,
  FileText,
  Link,
  Github,
  Cloud,
  X,
  Check,
  Loader2,
  FolderOpen,
  AlertCircle,
  Tag,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { toast } from "sonner";

interface UploadedFile {
  file_id: string;
  filename: string;
  size_bytes: number;
  content_type: string;
  path: string;
  status: "pending" | "uploading" | "success" | "error";
  error?: string;
}

interface DocumentUploadProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  projectId?: string;
  collection?: string;
  onUploadComplete?: (files: UploadedFile[]) => void;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function DocumentUpload({
  open,
  onOpenChange,
  projectId,
  collection = "default",
  onUploadComplete,
}: DocumentUploadProps) {
  const [activeTab, setActiveTab] = React.useState("file");
  const [uploading, setUploading] = React.useState(false);
  const [uploadProgress, setUploadProgress] = React.useState(0);
  const [uploadedFiles, setUploadedFiles] = React.useState<UploadedFile[]>([]);
  const [tags, setTags] = React.useState<string[]>([]);
  const [tagInput, setTagInput] = React.useState("");
  const [selectedCollection, setSelectedCollection] = React.useState(collection);
  const [processImmediately, setProcessImmediately] = React.useState(true);

  // URL fetch state
  const [fetchUrl, setFetchUrl] = React.useState("");

  // GitHub fetch state
  const [githubUrl, setGithubUrl] = React.useState("");
  const [githubBranch, setGithubBranch] = React.useState("main");
  const [githubPaths, setGithubPaths] = React.useState("");

  // File drop state
  const [dragActive, setDragActive] = React.useState(false);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      await handleFileUpload(Array.from(e.dataTransfer.files));
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      await handleFileUpload(Array.from(e.target.files));
    }
  };

  const handleFileUpload = async (files: File[]) => {
    setUploading(true);
    setUploadProgress(0);

    const newFiles: UploadedFile[] = files.map((f) => ({
      file_id: "",
      filename: f.name,
      size_bytes: f.size,
      content_type: f.type,
      path: "",
      status: "pending" as const,
    }));

    setUploadedFiles(newFiles);

    try {
      const formData = new FormData();
      files.forEach((file) => {
        formData.append("files", file);
      });
      if (selectedCollection) formData.append("collection", selectedCollection);
      if (projectId) formData.append("project_id", projectId);
      if (tags.length > 0) formData.append("tags", tags.join(","));
      formData.append("process_immediately", processImmediately.toString());

      const response = await fetch(`${API_URL}/api/upload/files`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const result = await response.json();

      const updatedFiles: UploadedFile[] = result.files.map((f: any) => ({
        ...f,
        status: "success" as const,
      }));

      setUploadedFiles(updatedFiles);
      setUploadProgress(100);

      toast.success(`Uploaded ${result.total_files} files successfully`);

      if (onUploadComplete) {
        onUploadComplete(updatedFiles);
      }
    } catch (error) {
      toast.error(`Upload failed: ${error}`);
      setUploadedFiles(
        newFiles.map((f) => ({
          ...f,
          status: "error" as const,
          error: String(error),
        }))
      );
    } finally {
      setUploading(false);
    }
  };

  const handleUrlFetch = async () => {
    if (!fetchUrl) {
      toast.error("Please enter a URL");
      return;
    }

    setUploading(true);

    try {
      const response = await fetch(`${API_URL}/api/upload/fetch/url`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          url: fetchUrl,
          collection: selectedCollection,
          project_id: projectId,
          tags: tags,
          process_immediately: processImmediately,
        }),
      });

      if (!response.ok) {
        throw new Error(`Fetch failed: ${response.statusText}`);
      }

      const result = await response.json();

      if (result.success) {
        toast.success(`Fetched ${result.files_fetched} files from URL`);
        setFetchUrl("");
      } else {
        toast.error(`Fetch failed: ${result.errors?.join(", ")}`);
      }
    } catch (error) {
      toast.error(`Fetch failed: ${error}`);
    } finally {
      setUploading(false);
    }
  };

  const handleGitHubFetch = async () => {
    if (!githubUrl) {
      toast.error("Please enter a GitHub URL");
      return;
    }

    setUploading(true);

    try {
      const response = await fetch(`${API_URL}/api/upload/fetch/github`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          repo_url: githubUrl,
          branch: githubBranch,
          paths: githubPaths ? githubPaths.split(",").map((p) => p.trim()) : [],
          collection: selectedCollection,
          project_id: projectId,
          tags: tags,
          process_immediately: processImmediately,
        }),
      });

      if (!response.ok) {
        throw new Error(`Fetch failed: ${response.statusText}`);
      }

      const result = await response.json();

      if (result.success) {
        toast.success(`Fetched ${result.files_fetched} files from GitHub`);
        setGithubUrl("");
        setGithubPaths("");
      } else {
        toast.error(`Fetch failed: ${result.errors?.join(", ")}`);
      }
    } catch (error) {
      toast.error(`Fetch failed: ${error}`);
    } finally {
      setUploading(false);
    }
  };

  const addTag = () => {
    if (tagInput && !tags.includes(tagInput.toLowerCase())) {
      setTags([...tags, tagInput.toLowerCase()]);
      setTagInput("");
    }
  };

  const removeTag = (tag: string) => {
    setTags(tags.filter((t) => t !== tag));
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            Upload Documents
          </DialogTitle>
          <DialogDescription>
            Upload documents to the knowledge base for indexing and retrieval.
          </DialogDescription>
        </DialogHeader>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="file" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Files
            </TabsTrigger>
            <TabsTrigger value="url" className="flex items-center gap-2">
              <Link className="h-4 w-4" />
              URL
            </TabsTrigger>
            <TabsTrigger value="github" className="flex items-center gap-2">
              <Github className="h-4 w-4" />
              GitHub
            </TabsTrigger>
          </TabsList>

          <TabsContent value="file" className="space-y-4">
            {/* Drop Zone */}
            <div
              className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                dragActive
                  ? "border-primary bg-primary/5"
                  : "border-muted-foreground/25"
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <input
                ref={fileInputRef}
                type="file"
                multiple
                onChange={handleFileSelect}
                className="hidden"
                accept=".txt,.md,.pdf,.docx,.json,.yaml,.yml,.py,.js,.ts,.html,.css,.xml,.csv"
              />
              <FolderOpen className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
              <p className="text-lg font-medium mb-2">
                Drop files here or click to browse
              </p>
              <p className="text-sm text-muted-foreground mb-4">
                Supports TXT, MD, PDF, DOCX, JSON, YAML, Python, JS/TS, HTML,
                CSS, XML, CSV
              </p>
              <Button
                variant="outline"
                onClick={() => fileInputRef.current?.click()}
              >
                Select Files
              </Button>
            </div>

            {/* Uploaded Files List */}
            {uploadedFiles.length > 0 && (
              <ScrollArea className="h-40">
                <div className="space-y-2">
                  {uploadedFiles.map((file, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-2 rounded-lg bg-muted/50"
                    >
                      <div className="flex items-center gap-2">
                        <FileText className="h-4 w-4" />
                        <span className="text-sm font-medium">
                          {file.filename}
                        </span>
                        <span className="text-xs text-muted-foreground">
                          ({formatFileSize(file.size_bytes)})
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        {file.status === "pending" && (
                          <Badge variant="secondary">Pending</Badge>
                        )}
                        {file.status === "uploading" && (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        )}
                        {file.status === "success" && (
                          <Check className="h-4 w-4 text-green-500" />
                        )}
                        {file.status === "error" && (
                          <AlertCircle className="h-4 w-4 text-red-500" />
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            )}
          </TabsContent>

          <TabsContent value="url" className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="fetch-url">URL</Label>
              <Input
                id="fetch-url"
                placeholder="https://example.com/document.pdf"
                value={fetchUrl}
                onChange={(e) => setFetchUrl(e.target.value)}
              />
            </div>
            <Button
              onClick={handleUrlFetch}
              disabled={uploading || !fetchUrl}
              className="w-full"
            >
              {uploading ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <Link className="h-4 w-4 mr-2" />
              )}
              Fetch from URL
            </Button>
          </TabsContent>

          <TabsContent value="github" className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="github-url">Repository URL</Label>
              <Input
                id="github-url"
                placeholder="https://github.com/owner/repo"
                value={githubUrl}
                onChange={(e) => setGithubUrl(e.target.value)}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="github-branch">Branch</Label>
                <Input
                  id="github-branch"
                  placeholder="main"
                  value={githubBranch}
                  onChange={(e) => setGithubBranch(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="github-paths">Paths (comma-separated)</Label>
                <Input
                  id="github-paths"
                  placeholder="src/, docs/"
                  value={githubPaths}
                  onChange={(e) => setGithubPaths(e.target.value)}
                />
              </div>
            </div>
            <Button
              onClick={handleGitHubFetch}
              disabled={uploading || !githubUrl}
              className="w-full"
            >
              {uploading ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <Github className="h-4 w-4 mr-2" />
              )}
              Fetch from GitHub
            </Button>
          </TabsContent>
        </Tabs>

        {/* Common Options */}
        <div className="space-y-4 pt-4 border-t">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="collection">Collection</Label>
              <Select
                value={selectedCollection}
                onValueChange={setSelectedCollection}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select collection" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="default">Default</SelectItem>
                  <SelectItem value="documents">Documents</SelectItem>
                  <SelectItem value="code">Code</SelectItem>
                  <SelectItem value="research">Research</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Tags</Label>
              <div className="flex gap-2">
                <Input
                  placeholder="Add tag..."
                  value={tagInput}
                  onChange={(e) => setTagInput(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && addTag()}
                />
                <Button variant="outline" size="icon" onClick={addTag}>
                  <Tag className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>

          {tags.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {tags.map((tag) => (
                <Badge
                  key={tag}
                  variant="secondary"
                  className="flex items-center gap-1"
                >
                  {tag}
                  <X
                    className="h-3 w-3 cursor-pointer"
                    onClick={() => removeTag(tag)}
                  />
                </Badge>
              ))}
            </div>
          )}
        </div>

        {uploading && <Progress value={uploadProgress} className="w-full" />}

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export default DocumentUpload;
