"use client";

import * as React from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Save, Loader2, Trash2, Bot, GitBranch, FileText, Database, Server, Search, RefreshCw, CheckCircle2, XCircle, Clock, Link2, Sparkles, MoreHorizontal } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
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
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { GenerationModal, useGenerationModal } from "@/components/generation-modal";
import { 
  useProject, 
  useNotes, 
  useCreateNote,
  useDataSources,
  useProjectServices,
  useProjectGitConfig,
  useUpdateProjectGitConfig,
  useSyncProjectGit,
  useProjectIndexingStatus,
  useTriggerProjectIndexing,
  useProjectResources,
  type GitConfig,
} from "@/lib/api";
import { toast } from "sonner";

export default function ProjectDetailPage() {
  const router = useRouter();
  const params = useParams();
  const projectId = params.id as string;
  
  const { data: project, isLoading, mutate } = useProject(projectId);
  const { data: notes, mutate: mutateNotes } = useNotes("project", projectId);
  const { trigger: createNote } = useCreateNote();
  
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [newNote, setNewNote] = React.useState("");
  
  const [formData, setFormData] = React.useState({
    name: "",
    description: "",
    status: "draft",
    config_yaml: "",
    tags: "",
  });

  // Initialize form data when project loads
  React.useEffect(() => {
    if (project) {
      setFormData({
        name: project.name,
        description: project.description,
        status: project.status,
        config_yaml: project.config_yaml,
        tags: project.tags.join(", "),
      });
    }
  }, [project]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name.trim()) {
      toast.error("Project name is required");
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      const response = await fetch(`http://localhost:8080/api/v1/projects/${projectId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: formData.name.trim(),
          description: formData.description.trim(),
          status: formData.status,
          config_yaml: formData.config_yaml,
          tags: formData.tags
            .split(",")
            .map((t) => t.trim())
            .filter(Boolean),
        }),
      });
      
      if (response.ok) {
        toast.success("Project updated successfully");
        mutate();
      } else {
        const error = await response.json();
        toast.error(error.detail || "Failed to update project");
      }
    } catch (error) {
      toast.error("Failed to update project");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async () => {
    try {
      const response = await fetch(`http://localhost:8080/api/v1/projects/${projectId}`, {
        method: "DELETE",
      });
      
      if (response.ok) {
        toast.success("Project deleted");
        router.push("/projects");
      } else {
        toast.error("Failed to delete project");
      }
    } catch (error) {
      toast.error("Failed to delete project");
    }
  };

  const handleAddNote = async () => {
    if (!newNote.trim()) return;
    
    try {
      await createNote({
        resource_type: "project",
        resource_id: projectId,
        content: newNote.trim(),
      });
      setNewNote("");
      mutateNotes();
      toast.success("Note added");
    } catch (error) {
      toast.error("Failed to add note");
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="flex items-center gap-4">
          <Skeleton className="h-10 w-10" />
          <div>
            <Skeleton className="h-8 w-64" />
            <Skeleton className="h-4 w-48 mt-2" />
          </div>
        </div>
        <Skeleton className="h-96" />
      </div>
    );
  }

  if (!project) {
    return (
      <div className="max-w-4xl mx-auto">
        <Card>
          <CardContent className="pt-6 text-center">
            <p className="text-muted-foreground">Project not found</p>
            <Button asChild className="mt-4">
              <Link href="/projects">Back to Projects</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" asChild>
            <Link href="/projects">
              <ArrowLeft className="size-4" />
            </Link>
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">{project.name}</h1>
            <p className="text-muted-foreground">
              Created {new Date(project.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>
        <AlertDialog>
          <AlertDialogTrigger asChild>
            <Button variant="destructive" size="sm">
              <Trash2 className="size-4 mr-2" />
              Delete
            </Button>
          </AlertDialogTrigger>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Delete Project?</AlertDialogTitle>
              <AlertDialogDescription>
                This will permanently delete &quot;{project.name}&quot; and all associated data.
                This action cannot be undone.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction onClick={handleDelete}>Delete</AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="details">
        <TabsList className="grid w-full grid-cols-8">
          <TabsTrigger value="details">Details</TabsTrigger>
          <TabsTrigger value="agents">Agents</TabsTrigger>
          <TabsTrigger value="flows">Flows</TabsTrigger>
          <TabsTrigger value="notes">Notes</TabsTrigger>
          <TabsTrigger value="datasources">Data Sources</TabsTrigger>
          <TabsTrigger value="services">Services</TabsTrigger>
          <TabsTrigger value="indexing">Indexing</TabsTrigger>
          <TabsTrigger value="git">Git</TabsTrigger>
        </TabsList>

        {/* Details Tab */}
        <TabsContent value="details">
          <form onSubmit={handleSubmit}>
            <Card>
              <CardHeader>
                <CardTitle>Project Details</CardTitle>
                <CardDescription>
                  Edit the project information
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Name */}
                <div className="space-y-2">
                  <Label htmlFor="name">Project Name *</Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) =>
                      setFormData({ ...formData, name: e.target.value })
                    }
                    required
                  />
                </div>

                {/* Description */}
                <div className="space-y-2">
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    rows={3}
                    value={formData.description}
                    onChange={(e) =>
                      setFormData({ ...formData, description: e.target.value })
                    }
                  />
                </div>

                {/* Status */}
                <div className="space-y-2">
                  <Label htmlFor="status">Status</Label>
                  <Select
                    value={formData.status}
                    onValueChange={(value) =>
                      setFormData({ ...formData, status: value })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="draft">Draft</SelectItem>
                      <SelectItem value="active">Active</SelectItem>
                      <SelectItem value="archived">Archived</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Tags */}
                <div className="space-y-2">
                  <Label htmlFor="tags">Tags</Label>
                  <Input
                    id="tags"
                    placeholder="research, nlp, multi-agent (comma separated)"
                    value={formData.tags}
                    onChange={(e) =>
                      setFormData({ ...formData, tags: e.target.value })
                    }
                  />
                </div>

                {/* Config YAML */}
                <div className="space-y-2">
                  <Label htmlFor="config">Configuration (YAML)</Label>
                  <Textarea
                    id="config"
                    rows={8}
                    className="font-mono text-sm"
                    value={formData.config_yaml}
                    onChange={(e) =>
                      setFormData({ ...formData, config_yaml: e.target.value })
                    }
                  />
                </div>

                {/* Save Button */}
                <div className="flex justify-end">
                  <Button type="submit" disabled={isSubmitting}>
                    {isSubmitting ? (
                      <>
                        <Loader2 className="size-4 mr-2 animate-spin" />
                        Saving...
                      </>
                    ) : (
                      <>
                        <Save className="size-4 mr-2" />
                        Save Changes
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </form>
        </TabsContent>

        {/* Agents Tab */}
        <TabsContent value="agents">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Project Agents</CardTitle>
                  <CardDescription>
                    Agents associated with this project
                  </CardDescription>
                </div>
                <Button size="sm" asChild>
                  <Link href={`/agents/new?project_id=${projectId}`}>
                    <Bot className="size-4 mr-2" />
                    Add Agent
                  </Link>
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-muted-foreground">
                <Bot className="size-12 mx-auto mb-4 opacity-50" />
                <p>No agents in this project yet</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Flows Tab */}
        <TabsContent value="flows">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Project Flows</CardTitle>
                  <CardDescription>
                    Multi-agent workflows in this project
                  </CardDescription>
                </div>
                <Button size="sm" asChild>
                  <Link href={`/flows/new?project_id=${projectId}`}>
                    <GitBranch className="size-4 mr-2" />
                    Add Flow
                  </Link>
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-muted-foreground">
                <GitBranch className="size-12 mx-auto mb-4 opacity-50" />
                <p>No flows in this project yet</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Notes Tab */}
        <TabsContent value="notes">
          <NotesTabWithGeneration 
            projectId={projectId} 
            notes={notes || []} 
            onAddNote={handleAddNote}
            newNote={newNote}
            setNewNote={setNewNote}
            mutateNotes={mutateNotes}
          />
        </TabsContent>

        {/* Data Sources Tab */}
        <TabsContent value="datasources">
          <ProjectDataSourcesTab projectId={projectId} />
        </TabsContent>

        {/* Services Tab */}
        <TabsContent value="services">
          <ProjectServicesTab projectId={projectId} />
        </TabsContent>

        {/* Indexing Tab */}
        <TabsContent value="indexing">
          <ProjectIndexingTab projectId={projectId} />
        </TabsContent>

        {/* Git Tab */}
        <TabsContent value="git">
          <ProjectGitTab projectId={projectId} />
        </TabsContent>
      </Tabs>
    </div>
  );
}

// ============================================================================
// Data Sources Tab Component
// ============================================================================

function ProjectDataSourcesTab({ projectId }: { projectId: string }) {
  const { data: dataSources, isLoading, mutate } = useDataSources({ project_id: projectId });
  const { data: projectResources } = useProjectResources(projectId, "datasource");

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Data Sources</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <Skeleton className="h-12 w-full" />
            <Skeleton className="h-12 w-full" />
          </div>
        </CardContent>
      </Card>
    );
  }

  const linkedSourceIds = new Set(
    projectResources?.resources
      ?.filter(r => r.resource_type === "datasource")
      .map(r => r.resource_id) || []
  );

  const projectDataSources = dataSources?.items || [];

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Project Data Sources</CardTitle>
            <CardDescription>
              Manage database connections, file stores, and API integrations
            </CardDescription>
          </div>
          <Button size="sm" asChild>
            <Link href={`/datasources/new?project_id=${projectId}`}>
              <Database className="size-4 mr-2" />
              Add Data Source
            </Link>
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {projectDataSources.length > 0 ? (
          <div className="space-y-3">
            {projectDataSources.map((ds) => (
              <div
                key={ds.id}
                className="flex items-center justify-between p-4 rounded-lg border bg-card hover:bg-muted/50 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div className="p-2 rounded-md bg-primary/10">
                    <Database className="size-5 text-primary" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{ds.name}</span>
                      <Badge variant="outline" className="text-xs">
                        {ds.source_type}
                      </Badge>
                      {ds.is_global && (
                        <Badge variant="secondary" className="text-xs">Global</Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {ds.description || "No description"}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge 
                    variant={ds.connection_status === "connected" ? "default" : "secondary"}
                    className="gap-1"
                  >
                    {ds.connection_status === "connected" ? (
                      <CheckCircle2 className="size-3" />
                    ) : (
                      <XCircle className="size-3" />
                    )}
                    {ds.connection_status || "unknown"}
                  </Badge>
                  <Button variant="ghost" size="sm" asChild>
                    <Link href={`/datasources/${ds.id}`}>
                      View
                    </Link>
                  </Button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-muted-foreground">
            <Database className="size-12 mx-auto mb-4 opacity-50" />
            <p>No data sources in this project</p>
            <p className="text-sm mt-1">Connect to databases, file stores, or APIs</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// ============================================================================
// Services Tab Component
// ============================================================================

function ProjectServicesTab({ projectId }: { projectId: string }) {
  const { data: services, isLoading, mutate } = useProjectServices(projectId);

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Services</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <Skeleton className="h-12 w-full" />
            <Skeleton className="h-12 w-full" />
          </div>
        </CardContent>
      </Card>
    );
  }

  const projectServices = services?.items || [];

  const getServiceIcon = (type: string) => {
    switch (type) {
      case "web_ui": return "🌐";
      case "api": return "🔌";
      case "ml_deployment": return "🤖";
      case "jupyter": return "📓";
      case "mlflow": return "📊";
      case "remote_dev": return "💻";
      default: return "⚙️";
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Project Services</CardTitle>
            <CardDescription>
              Web UIs, API endpoints, ML deployments, and development servers
            </CardDescription>
          </div>
          <Button size="sm">
            <Server className="size-4 mr-2" />
            Add Service
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {projectServices.length > 0 ? (
          <div className="space-y-3">
            {projectServices.map((service) => (
              <div
                key={service.id}
                className="flex items-center justify-between p-4 rounded-lg border bg-card hover:bg-muted/50 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div className="p-2 rounded-md bg-primary/10 text-xl">
                    {getServiceIcon(service.service_type)}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{service.name}</span>
                      <Badge variant="outline" className="text-xs">
                        {service.service_type}
                      </Badge>
                    </div>
                    {service.endpoint_url && (
                      <p className="text-sm text-muted-foreground flex items-center gap-1">
                        <Link2 className="size-3" />
                        {service.endpoint_url}
                      </p>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge 
                    variant={service.status === "healthy" ? "default" : service.status === "unhealthy" ? "destructive" : "secondary"}
                    className="gap-1"
                  >
                    {service.status === "healthy" ? (
                      <CheckCircle2 className="size-3" />
                    ) : service.status === "unhealthy" ? (
                      <XCircle className="size-3" />
                    ) : (
                      <Clock className="size-3" />
                    )}
                    {service.status}
                  </Badge>
                  {service.endpoint_url && (
                    <Button variant="ghost" size="sm" asChild>
                      <a href={service.endpoint_url} target="_blank" rel="noopener noreferrer">
                        Open
                      </a>
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-muted-foreground">
            <Server className="size-12 mx-auto mb-4 opacity-50" />
            <p>No services configured</p>
            <p className="text-sm mt-1">Add web UIs, APIs, or ML deployments</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// ============================================================================
// Indexing Tab Component
// ============================================================================

function ProjectIndexingTab({ projectId }: { projectId: string }) {
  const { data: indexingStatus, isLoading, mutate } = useProjectIndexingStatus(projectId);
  const { trigger: triggerIndexing, isMutating } = useTriggerProjectIndexing(projectId);
  const [forceReindex, setForceReindex] = React.useState(false);

  const handleTriggerIndexing = async () => {
    try {
      await triggerIndexing({ force: forceReindex });
      toast.success("Indexing started");
      mutate();
    } catch (error) {
      toast.error("Failed to start indexing");
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Codebase Indexing</CardTitle>
        </CardHeader>
        <CardContent>
          <Skeleton className="h-32 w-full" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Codebase Indexing</CardTitle>
            <CardDescription>
              Semantic search and code intelligence for your project
            </CardDescription>
          </div>
          <Button 
            onClick={handleTriggerIndexing} 
            disabled={isMutating || indexingStatus?.status === "in_progress"}
          >
            {isMutating || indexingStatus?.status === "in_progress" ? (
              <>
                <Loader2 className="size-4 mr-2 animate-spin" />
                Indexing...
              </>
            ) : (
              <>
                <Search className="size-4 mr-2" />
                {indexingStatus?.needs_reindex ? "Reindex" : "Index Now"}
              </>
            )}
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Status Overview */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-4 rounded-lg border bg-muted/30">
            <p className="text-sm text-muted-foreground">Status</p>
            <div className="flex items-center gap-2 mt-1">
              {indexingStatus?.status === "completed" ? (
                <CheckCircle2 className="size-4 text-green-500" />
              ) : indexingStatus?.status === "in_progress" ? (
                <Loader2 className="size-4 animate-spin text-blue-500" />
              ) : indexingStatus?.status === "failed" ? (
                <XCircle className="size-4 text-red-500" />
              ) : (
                <Clock className="size-4 text-muted-foreground" />
              )}
              <span className="font-medium capitalize">{indexingStatus?.status || "Not indexed"}</span>
            </div>
          </div>
          <div className="p-4 rounded-lg border bg-muted/30">
            <p className="text-sm text-muted-foreground">Files Indexed</p>
            <p className="text-xl font-semibold mt-1">{indexingStatus?.file_count || 0}</p>
          </div>
          <div className="p-4 rounded-lg border bg-muted/30">
            <p className="text-sm text-muted-foreground">Chunks</p>
            <p className="text-xl font-semibold mt-1">{indexingStatus?.chunk_count || 0}</p>
          </div>
          <div className="p-4 rounded-lg border bg-muted/30">
            <p className="text-sm text-muted-foreground">Version</p>
            <p className="text-xl font-semibold mt-1">{indexingStatus?.version || "-"}</p>
          </div>
        </div>

        {/* Last Indexed */}
        {indexingStatus?.last_indexed && (
          <div className="p-4 rounded-lg border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Last Indexed</p>
                <p className="font-medium">
                  {new Date(indexingStatus.last_indexed).toLocaleString()}
                </p>
              </div>
              {indexingStatus.needs_reindex && (
                <Badge variant="secondary" className="gap-1">
                  <RefreshCw className="size-3" />
                  Reindex recommended
                </Badge>
              )}
            </div>
          </div>
        )}

        {/* Reindex Option */}
        <div className="flex items-center justify-between p-4 rounded-lg border">
          <div>
            <p className="font-medium">Force Full Reindex</p>
            <p className="text-sm text-muted-foreground">
              Rebuild the entire index from scratch
            </p>
          </div>
          <Button 
            variant="outline" 
            onClick={() => {
              setForceReindex(true);
              handleTriggerIndexing();
            }}
            disabled={isMutating}
          >
            <RefreshCw className="size-4 mr-2" />
            Force Reindex
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

// ============================================================================
// Git Tab Component
// ============================================================================

function ProjectGitTab({ projectId }: { projectId: string }) {
  const { data: gitConfig, isLoading, mutate } = useProjectGitConfig(projectId);
  const { trigger: updateGitConfig, isMutating: isUpdating } = useUpdateProjectGitConfig(projectId);
  const { trigger: syncGit, isMutating: isSyncing } = useSyncProjectGit(projectId);

  const [formData, setFormData] = React.useState({
    remote_url: "",
    branch: "main",
    auto_sync: false,
  });

  React.useEffect(() => {
    if (gitConfig) {
      setFormData({
        remote_url: gitConfig.remote_url || "",
        branch: gitConfig.branch || "main",
        auto_sync: gitConfig.auto_sync || false,
      });
    }
  }, [gitConfig]);

  const handleSave = async () => {
    try {
      await updateGitConfig(formData);
      toast.success("Git configuration saved");
      mutate();
    } catch (error) {
      toast.error("Failed to save git configuration");
    }
  };

  const handleSync = async () => {
    try {
      await syncGit();
      toast.success("Git sync initiated");
    } catch (error) {
      toast.error("Failed to sync repository");
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Git Configuration</CardTitle>
        </CardHeader>
        <CardContent>
          <Skeleton className="h-32 w-full" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Git Configuration</CardTitle>
            <CardDescription>
              Connect your project to a Git repository
            </CardDescription>
          </div>
          {gitConfig?.remote_url && (
            <Button 
              variant="outline" 
              onClick={handleSync}
              disabled={isSyncing}
            >
              {isSyncing ? (
                <>
                  <Loader2 className="size-4 mr-2 animate-spin" />
                  Syncing...
                </>
              ) : (
                <>
                  <RefreshCw className="size-4 mr-2" />
                  Sync Now
                </>
              )}
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Remote URL */}
        <div className="space-y-2">
          <Label htmlFor="remote_url">Repository URL</Label>
          <Input
            id="remote_url"
            placeholder="https://github.com/user/repo.git"
            value={formData.remote_url}
            onChange={(e) => setFormData({ ...formData, remote_url: e.target.value })}
          />
          <p className="text-xs text-muted-foreground">
            HTTPS or SSH URL for your Git repository
          </p>
        </div>

        {/* Branch */}
        <div className="space-y-2">
          <Label htmlFor="branch">Default Branch</Label>
          <Input
            id="branch"
            placeholder="main"
            value={formData.branch}
            onChange={(e) => setFormData({ ...formData, branch: e.target.value })}
          />
        </div>

        {/* Auto Sync */}
        <div className="flex items-center justify-between p-4 rounded-lg border">
          <div>
            <p className="font-medium">Auto Sync</p>
            <p className="text-sm text-muted-foreground">
              Automatically sync changes with remote repository
            </p>
          </div>
          <Button
            variant={formData.auto_sync ? "default" : "outline"}
            size="sm"
            onClick={() => setFormData({ ...formData, auto_sync: !formData.auto_sync })}
          >
            {formData.auto_sync ? "Enabled" : "Disabled"}
          </Button>
        </div>

        {/* Status */}
        {gitConfig?.last_synced && (
          <div className="p-4 rounded-lg border bg-muted/30">
            <p className="text-sm text-muted-foreground">Last Synced</p>
            <p className="font-medium">
              {new Date(gitConfig.last_synced).toLocaleString()}
            </p>
          </div>
        )}

        {/* Save Button */}
        <div className="flex justify-end">
          <Button onClick={handleSave} disabled={isUpdating}>
            {isUpdating ? (
              <>
                <Loader2 className="size-4 mr-2 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="size-4 mr-2" />
                Save Configuration
              </>
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

// ============================================================================
// Notes Tab Component with Generation Modal Integration
// ============================================================================

interface NotesTabWithGenerationProps {
  projectId: string;
  notes: { id: string; content: string; created_at: string }[];
  onAddNote: () => void;
  newNote: string;
  setNewNote: (value: string) => void;
  mutateNotes: () => void;
}

function NotesTabWithGeneration({ 
  projectId, 
  notes, 
  onAddNote, 
  newNote, 
  setNewNote,
  mutateNotes,
}: NotesTabWithGenerationProps) {
  const generationModal = useGenerationModal();
  const [selectedText, setSelectedText] = React.useState("");

  const handleGenerateFromNote = (noteContent: string) => {
    generationModal.openWithNotes(noteContent);
  };

  const handleGenerateFromSelection = () => {
    if (selectedText) {
      generationModal.openWithNotes(selectedText);
    }
  };

  const handleTextSelection = () => {
    const selection = window.getSelection();
    if (selection && selection.toString().trim()) {
      setSelectedText(selection.toString().trim());
    } else {
      setSelectedText("");
    }
  };

  return (
    <>
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Notes</CardTitle>
              <CardDescription>
                Free-form notes for this project - generate components from your ideas
              </CardDescription>
            </div>
            {selectedText && (
              <Button 
                size="sm" 
                variant="secondary"
                onClick={handleGenerateFromSelection}
                className="gap-2"
              >
                <Sparkles className="size-4" />
                Generate from Selection
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Add Note */}
          <div className="flex gap-2">
            <Textarea
              placeholder="Add a note... (you can later generate components from your notes)"
              value={newNote}
              onChange={(e) => setNewNote(e.target.value)}
              rows={3}
            />
            <div className="flex flex-col gap-2">
              <Button onClick={onAddNote} disabled={!newNote.trim()}>
                Add
              </Button>
              {newNote.trim() && (
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => generationModal.openWithNotes(newNote)}
                >
                  <Sparkles className="size-4" />
                </Button>
              )}
            </div>
          </div>

          {/* Notes List */}
          {notes && notes.length > 0 ? (
            <div className="space-y-3" onMouseUp={handleTextSelection}>
              {notes.map((note) => (
                <div
                  key={note.id}
                  className="group p-4 rounded-lg bg-muted/50 border hover:border-primary/30 transition-colors"
                >
                  <div className="flex items-start justify-between gap-4">
                    <p className="whitespace-pre-wrap flex-1 select-text">{note.content}</p>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button 
                          variant="ghost" 
                          size="icon" 
                          className="opacity-0 group-hover:opacity-100 transition-opacity shrink-0"
                        >
                          <MoreHorizontal className="size-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => handleGenerateFromNote(note.content)}>
                          <Sparkles className="size-4 mr-2" />
                          Generate Component
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => navigator.clipboard.writeText(note.content)}>
                          Copy
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                  <div className="flex items-center justify-between mt-3">
                    <p className="text-xs text-muted-foreground">
                      {new Date(note.created_at).toLocaleString()}
                    </p>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-xs h-7 opacity-0 group-hover:opacity-100 transition-opacity"
                      onClick={() => handleGenerateFromNote(note.content)}
                    >
                      <Sparkles className="size-3 mr-1" />
                      Generate
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <FileText className="size-12 mx-auto mb-4 opacity-50" />
              <p>No notes yet</p>
              <p className="text-sm mt-1">Add notes and generate components from your ideas</p>
            </div>
          )}
        </CardContent>
      </Card>

      <GenerationModal
        open={generationModal.open}
        onOpenChange={generationModal.setOpen}
        initialNotes={generationModal.initialNotes}
        initialComponentType={generationModal.initialType}
        onComponentGenerated={(component) => {
          toast.success(`Component "${component.name}" generated!`);
        }}
      />
    </>
  );
}

