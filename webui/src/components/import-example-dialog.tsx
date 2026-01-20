"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import {
  Download,
  FileText,
  Folder,
  Loader2,
  Tag,
  ChevronRight,
  FileCode,
  Copy,
} from "lucide-react";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Switch } from "@/components/ui/switch";
import { cn } from "@/lib/utils";
import { toast } from "sonner";

const API_BASE = "http://localhost:8080/api/v1";

interface ExampleFile {
  name: string;
  path: string;
  is_directory: boolean;
}

interface ExampleEntry {
  slug: string;
  name: string;
  description: string;
  files: ExampleFile[];
  config_preview: string;
  has_readme: boolean;
  has_config: boolean;
  tags: string[];
}

interface ImportExampleDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

function useExamples() {
  const [data, setData] = React.useState<ExampleEntry[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    fetch(`${API_BASE}/examples`)
      .then((res) => res.json())
      .then((res) => {
        setData(res.items || []);
        setIsLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setIsLoading(false);
      });
  }, []);

  return { data, isLoading, error };
}

export function ImportExampleDialog({ open, onOpenChange }: ImportExampleDialogProps) {
  const router = useRouter();
  const { data: examples, isLoading } = useExamples();

  const [step, setStep] = React.useState<"select" | "configure">("select");
  const [selectedExample, setSelectedExample] = React.useState<ExampleEntry | null>(null);
  const [isImporting, setIsImporting] = React.useState(false);

  const [formData, setFormData] = React.useState({
    projectName: "",
    description: "",
    copyFiles: true,
  });

  // Reset state when dialog opens/closes
  React.useEffect(() => {
    if (open) {
      setStep("select");
      setSelectedExample(null);
      setFormData({
        projectName: "",
        description: "",
        copyFiles: true,
      });
    }
  }, [open]);

  // Pre-fill form when example is selected
  React.useEffect(() => {
    if (selectedExample) {
      setFormData({
        projectName: selectedExample.name,
        description: selectedExample.description,
        copyFiles: true,
      });
    }
  }, [selectedExample]);

  const handleSelectExample = (example: ExampleEntry) => {
    setSelectedExample(example);
    setStep("configure");
  };

  const handleBack = () => {
    setStep("select");
    setSelectedExample(null);
  };

  const handleImport = async () => {
    if (!selectedExample || !formData.projectName.trim()) {
      toast.error("Project name is required");
      return;
    }

    setIsImporting(true);

    try {
      const response = await fetch(`${API_BASE}/examples/import`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          example_slug: selectedExample.slug,
          project_name: formData.projectName.trim(),
          description: formData.description.trim() || null,
          copy_files: formData.copyFiles,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to import example");
      }

      const result = await response.json();
      toast.success(result.message);
      onOpenChange(false);
      router.push(`/projects/${result.project_id}`);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to import example");
    } finally {
      setIsImporting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[700px] max-h-[85vh]">
        {step === "select" ? (
          <>
            <DialogHeader>
              <DialogTitle>Import from Example</DialogTitle>
              <DialogDescription>
                Choose an example template to bootstrap your new project
              </DialogDescription>
            </DialogHeader>

            <ScrollArea className="h-[400px] pr-4">
              {isLoading ? (
                <div className="space-y-3">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="p-4 rounded-lg border">
                      <Skeleton className="h-5 w-1/3 mb-2" />
                      <Skeleton className="h-4 w-full" />
                    </div>
                  ))}
                </div>
              ) : examples.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <Folder className="size-12 mx-auto mb-4 opacity-50" />
                  <p>No example projects found</p>
                  <p className="text-sm mt-1">
                    Add example directories to <code>examples/</code>
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {examples.map((example) => (
                    <button
                      key={example.slug}
                      onClick={() => handleSelectExample(example)}
                      className="w-full text-left p-4 rounded-lg border bg-card hover:bg-muted/50 hover:border-primary/50 transition-all group"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-semibold">{example.name}</span>
                            <ChevronRight className="size-4 text-muted-foreground group-hover:text-primary transition-colors" />
                          </div>
                          {example.description && (
                            <p className="text-sm text-muted-foreground line-clamp-2 mb-2">
                              {example.description}
                            </p>
                          )}
                          <div className="flex items-center gap-3 text-xs text-muted-foreground">
                            <span className="flex items-center gap-1">
                              <FileText className="size-3" />
                              {example.files.length} files
                            </span>
                            {example.has_config && (
                              <span className="flex items-center gap-1">
                                <FileCode className="size-3" />
                                config.yaml
                              </span>
                            )}
                          </div>
                          {example.tags.length > 0 && (
                            <div className="flex items-center gap-1 mt-2">
                              <Tag className="size-3 text-muted-foreground" />
                              {example.tags.map((tag) => (
                                <Badge key={tag} variant="secondary" className="text-xs">
                                  {tag}
                                </Badge>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </ScrollArea>

            <DialogFooter>
              <Button variant="outline" onClick={() => onOpenChange(false)}>
                Cancel
              </Button>
            </DialogFooter>
          </>
        ) : (
          <>
            <DialogHeader>
              <DialogTitle>Configure Import</DialogTitle>
              <DialogDescription>
                Importing from: <strong>{selectedExample?.name}</strong>
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-6 py-4">
              {/* Project Name */}
              <div className="space-y-2">
                <Label htmlFor="project-name">Project Name *</Label>
                <Input
                  id="project-name"
                  value={formData.projectName}
                  onChange={(e) =>
                    setFormData({ ...formData, projectName: e.target.value })
                  }
                  placeholder="My New Project"
                />
              </div>

              {/* Description */}
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) =>
                    setFormData({ ...formData, description: e.target.value })
                  }
                  placeholder="Optional project description..."
                  rows={3}
                />
              </div>

              {/* Copy Files Option */}
              <div className="flex items-center justify-between p-4 rounded-lg border">
                <div className="space-y-0.5">
                  <Label htmlFor="copy-files">Copy Example Files</Label>
                  <p className="text-sm text-muted-foreground">
                    Copy all example files to the project directory
                  </p>
                </div>
                <Switch
                  id="copy-files"
                  checked={formData.copyFiles}
                  onCheckedChange={(checked) =>
                    setFormData({ ...formData, copyFiles: checked })
                  }
                />
              </div>

              {/* Preview */}
              {selectedExample?.config_preview && (
                <div className="space-y-2">
                  <Label>Config Preview</Label>
                  <div className="p-3 rounded-lg bg-muted/50 border font-mono text-xs overflow-x-auto">
                    <pre className="whitespace-pre-wrap">{selectedExample.config_preview}</pre>
                  </div>
                </div>
              )}

              {/* Files List */}
              {selectedExample && selectedExample.files.length > 0 && (
                <div className="space-y-2">
                  <Label>Files to Import</Label>
                  <div className="p-3 rounded-lg border bg-muted/30 max-h-32 overflow-y-auto">
                    <div className="space-y-1">
                      {selectedExample.files.map((file) => (
                        <div
                          key={file.path}
                          className="flex items-center gap-2 text-sm"
                        >
                          {file.is_directory ? (
                            <Folder className="size-4 text-muted-foreground" />
                          ) : (
                            <FileText className="size-4 text-muted-foreground" />
                          )}
                          <span className={cn(file.is_directory && "font-medium")}>
                            {file.name}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={handleBack}>
                Back
              </Button>
              <Button onClick={handleImport} disabled={isImporting}>
                {isImporting ? (
                  <>
                    <Loader2 className="size-4 mr-2 animate-spin" />
                    Importing...
                  </>
                ) : (
                  <>
                    <Download className="size-4 mr-2" />
                    Import Project
                  </>
                )}
              </Button>
            </DialogFooter>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
