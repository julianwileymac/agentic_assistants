"use client";

import * as React from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
import { 
  ArrowLeft, 
  Save, 
  Loader2, 
  Trash2, 
  Bot, 
  GitBranch, 
  FileText, 
  Database, 
  Server, 
  Search, 
  RefreshCw, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  Link2, 
  Sparkles, 
  MoreHorizontal,
  Plus,
  Globe,
  Plug,
  Monitor,
  Container,
  Cpu,
  Cloud,
  ExternalLink,
  Play,
  Pause,
  Activity,
  Code,
  Terminal
} from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Switch } from "@/components/ui/switch";
import { HelpTooltip } from "@/components/help/help-tooltip";
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
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { GenerationModal, useGenerationModal } from "@/components/generation-modal";
import { 
  useProject, 
  useNotes, 
  useCreateNote,
  useDataSources,
  useProjectServices,
  useCreateProjectService,
  useCheckServiceHealth,
  useProjectGitConfig,
  useUpdateProjectGitConfig,
  useSyncProjectGit,
  useProjectIndexingStatus,
  useTriggerProjectIndexing,
  useProjectResources,
  type GitConfig,
} from "@/lib/api";
import { toast } from "sonner";
import { TestingSection } from "@/components/testing/testing-section";

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

      {project && (
        <TestingSection
          resourceType="project"
          resourceId={project.id}
          resourceName={project.name}
          defaultCode={`# Validate project resources\nresult = {\n    \"project_id\": \"${project.id}\",\n    \"status\": \"ok\",\n}\n`}
        />
      )}
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
// Service Types Configuration
// ============================================================================

interface ServiceTypeConfig {
  id: string;
  name: string;
  icon: React.ReactNode;
  description: string;
  color: string;
  category: "frontend" | "backend" | "infrastructure" | "development";
}

const SERVICE_TYPES: ServiceTypeConfig[] = [
  {
    id: "web_ui",
    name: "Web UI",
    icon: <Globe className="size-5" />,
    description: "Frontend web application or dashboard",
    color: "from-blue-500 to-cyan-500",
    category: "frontend",
  },
  {
    id: "api_endpoint",
    name: "API Endpoint",
    icon: <Plug className="size-5" />,
    description: "REST or GraphQL API service",
    color: "from-purple-500 to-pink-500",
    category: "backend",
  },
  {
    id: "ml_deployment",
    name: "ML Deployment",
    icon: <Cpu className="size-5" />,
    description: "Machine learning model serving endpoint",
    color: "from-green-500 to-emerald-500",
    category: "backend",
  },
  {
    id: "model_endpoint",
    name: "Model Endpoint",
    icon: <Bot className="size-5" />,
    description: "LLM or AI model inference endpoint",
    color: "from-orange-500 to-amber-500",
    category: "backend",
  },
  {
    id: "remote_dev_server",
    name: "Remote Dev Server",
    icon: <Terminal className="size-5" />,
    description: "Remote development environment (SSH, VS Code Server)",
    color: "from-gray-600 to-gray-700",
    category: "development",
  },
  {
    id: "container_registry",
    name: "Container Registry",
    icon: <Container className="size-5" />,
    description: "Docker/OCI container image registry",
    color: "from-sky-500 to-blue-600",
    category: "infrastructure",
  },
  {
    id: "file_store",
    name: "File Store",
    icon: <Cloud className="size-5" />,
    description: "Object storage or file server",
    color: "from-teal-500 to-cyan-600",
    category: "infrastructure",
  },
  {
    id: "background_service",
    name: "Background Service",
    icon: <Activity className="size-5" />,
    description: "Worker, scheduler, or background job processor",
    color: "from-indigo-500 to-violet-600",
    category: "backend",
  },
  {
    id: "database",
    name: "Database",
    icon: <Database className="size-5" />,
    description: "Database management interface",
    color: "from-rose-500 to-red-600",
    category: "infrastructure",
  },
];

// ============================================================================
// Add Service Dialog
// ============================================================================

function AddServiceDialog({
  projectId,
  open,
  onOpenChange,
  onCreated,
}: {
  projectId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onCreated: () => void;
}) {
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const { trigger: createService } = useCreateProjectService(projectId);
  
  const [formData, setFormData] = React.useState({
    name: "",
    service_type: "web_ui",
    endpoint_url: "",
    description: "",
    health_endpoint: "",
    auth_type: "none",
  });

  React.useEffect(() => {
    if (open) {
      setFormData({
        name: "",
        service_type: "web_ui",
        endpoint_url: "",
        description: "",
        health_endpoint: "",
        auth_type: "none",
      });
    }
  }, [open]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name.trim()) {
      toast.error("Service name is required");
      return;
    }

    setIsSubmitting(true);
    try {
      await createService({
        name: formData.name.trim(),
        service_type: formData.service_type,
        endpoint_url: formData.endpoint_url.trim(),
        description: formData.description.trim(),
        health_endpoint: formData.health_endpoint.trim() || null,
        auth_type: formData.auth_type === "none" ? null : formData.auth_type,
      });

      toast.success("Service added");
      onOpenChange(false);
      onCreated();
    } catch (error) {
      toast.error("Failed to add service");
    } finally {
      setIsSubmitting(false);
    }
  };

  const selectedType = SERVICE_TYPES.find((t) => t.id === formData.service_type);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Add Service</DialogTitle>
            <DialogDescription>
              Connect a web UI, API, ML deployment, or other service to this project
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            {/* Service Type Selection */}
            <div className="space-y-2">
              <Label>Service Type</Label>
              <div className="grid grid-cols-3 gap-2">
                {SERVICE_TYPES.slice(0, 6).map((type) => (
                  <button
                    key={type.id}
                    type="button"
                    onClick={() => setFormData({ ...formData, service_type: type.id })}
                    className={`p-3 rounded-lg border transition-all text-left ${
                      formData.service_type === type.id
                        ? "border-primary bg-primary/5"
                        : "border-transparent bg-muted/50 hover:bg-muted"
                    }`}
                  >
                    <div className={`p-1.5 rounded-md bg-gradient-to-br ${type.color} text-white w-fit mb-2`}>
                      {type.icon}
                    </div>
                    <p className="text-xs font-medium">{type.name}</p>
                  </button>
                ))}
              </div>
              <Select
                value={formData.service_type}
                onValueChange={(v) => setFormData({ ...formData, service_type: v })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {SERVICE_TYPES.map((type) => (
                    <SelectItem key={type.id} value={type.id}>
                      <div className="flex items-center gap-2">
                        {type.icon}
                        <span>{type.name}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {selectedType && (
                <p className="text-xs text-muted-foreground">{selectedType.description}</p>
              )}
            </div>

            {/* Name */}
            <div className="space-y-2">
              <Label htmlFor="service-name">Name *</Label>
              <Input
                id="service-name"
                placeholder="My Service"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </div>

            {/* Endpoint URL */}
            <div className="space-y-2">
              <Label htmlFor="endpoint-url">Endpoint URL</Label>
              <Input
                id="endpoint-url"
                placeholder="https://api.example.com"
                value={formData.endpoint_url}
                onChange={(e) => setFormData({ ...formData, endpoint_url: e.target.value })}
              />
            </div>

            {/* Description */}
            <div className="space-y-2">
              <Label htmlFor="service-description">Description</Label>
              <Textarea
                id="service-description"
                placeholder="Brief description of this service..."
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={2}
              />
            </div>

            {/* Health Endpoint */}
            <div className="space-y-2">
              <Label htmlFor="health-endpoint">Health Check Endpoint</Label>
              <Input
                id="health-endpoint"
                placeholder="/health or /api/health"
                value={formData.health_endpoint}
                onChange={(e) => setFormData({ ...formData, health_endpoint: e.target.value })}
              />
              <p className="text-xs text-muted-foreground">
                Relative path for health checks (appended to endpoint URL)
              </p>
            </div>

            {/* Auth Type */}
            <div className="space-y-2">
              <Label>Authentication</Label>
              <Select
                value={formData.auth_type}
                onValueChange={(v) => setFormData({ ...formData, auth_type: v })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">None</SelectItem>
                  <SelectItem value="api_key">API Key</SelectItem>
                  <SelectItem value="bearer">Bearer Token</SelectItem>
                  <SelectItem value="basic">Basic Auth</SelectItem>
                  <SelectItem value="oauth">OAuth</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <Loader2 className="size-4 mr-2 animate-spin" />
                  Adding...
                </>
              ) : (
                <>
                  <Plus className="size-4 mr-2" />
                  Add Service
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

// ============================================================================
// Services Tab Component
// ============================================================================

function ProjectServicesTab({ projectId }: { projectId: string }) {
  const { data: services, isLoading, mutate } = useProjectServices(projectId);
  const [addDialogOpen, setAddDialogOpen] = React.useState(false);
  const [checkingHealth, setCheckingHealth] = React.useState<Set<string>>(new Set());

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
    const serviceType = SERVICE_TYPES.find((t) => t.id === type);
    if (serviceType) {
      return (
        <div className={`p-2 rounded-md bg-gradient-to-br ${serviceType.color} text-white`}>
          {serviceType.icon}
        </div>
      );
    }
    return (
      <div className="p-2 rounded-md bg-muted">
        <Server className="size-5" />
      </div>
    );
  };

  const handleCheckHealth = async (serviceId: string) => {
    setCheckingHealth((prev) => new Set([...prev, serviceId]));
    try {
      const response = await fetch(
        `http://localhost:8080/api/v1/projects/${projectId}/services/${serviceId}/health`,
        { method: "POST" }
      );
      const result = await response.json();
      if (result.status === "healthy") {
        toast.success("Service is healthy");
      } else {
        toast.error(result.message || "Service is unhealthy");
      }
      mutate();
    } catch (error) {
      toast.error("Failed to check health");
    } finally {
      setCheckingHealth((prev) => {
        const next = new Set(prev);
        next.delete(serviceId);
        return next;
      });
    }
  };

  const handleDeleteService = async (serviceId: string, serviceName: string) => {
    if (!confirm(`Delete service "${serviceName}"?`)) return;
    
    try {
      const response = await fetch(
        `http://localhost:8080/api/v1/projects/${projectId}/services/${serviceId}`,
        { method: "DELETE" }
      );
      if (response.ok) {
        toast.success("Service deleted");
        mutate();
      } else {
        toast.error("Failed to delete service");
      }
    } catch (error) {
      toast.error("Failed to delete service");
    }
  };

  return (
    <>
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Project Services</CardTitle>
              <CardDescription>
                Web UIs, API endpoints, ML deployments, and development servers
              </CardDescription>
            </div>
            <Button size="sm" onClick={() => setAddDialogOpen(true)}>
              <Plus className="size-4 mr-2" />
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
                  className="group flex items-center justify-between p-4 rounded-lg border bg-card hover:bg-muted/50 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    {getServiceIcon(service.service_type)}
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{service.name}</span>
                        <Badge variant="outline" className="text-xs">
                          {service.service_type.replace(/_/g, " ")}
                        </Badge>
                      </div>
                      {service.endpoint_url && (
                        <p className="text-sm text-muted-foreground flex items-center gap-1">
                          <Link2 className="size-3" />
                          {service.endpoint_url}
                        </p>
                      )}
                      {service.description && (
                        <p className="text-xs text-muted-foreground mt-1 line-clamp-1">
                          {service.description}
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
                    
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="size-8"
                            onClick={() => handleCheckHealth(service.id)}
                            disabled={checkingHealth.has(service.id)}
                          >
                            {checkingHealth.has(service.id) ? (
                              <Loader2 className="size-4 animate-spin" />
                            ) : (
                              <RefreshCw className="size-4" />
                            )}
                          </Button>
                        </TooltipTrigger>
                        <TooltipContent>Check Health</TooltipContent>
                      </Tooltip>
                    </TooltipProvider>

                    {service.endpoint_url && (
                      <TooltipProvider>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Button variant="ghost" size="icon" className="size-8" asChild>
                              <a href={service.endpoint_url} target="_blank" rel="noopener noreferrer">
                                <ExternalLink className="size-4" />
                              </a>
                            </Button>
                          </TooltipTrigger>
                          <TooltipContent>Open in new tab</TooltipContent>
                        </Tooltip>
                      </TooltipProvider>
                    )}

                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="size-8 opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                          <MoreHorizontal className="size-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => handleCheckHealth(service.id)}>
                          <RefreshCw className="size-4 mr-2" />
                          Check Health
                        </DropdownMenuItem>
                        {service.endpoint_url && (
                          <DropdownMenuItem asChild>
                            <a href={service.endpoint_url} target="_blank" rel="noopener noreferrer">
                              <ExternalLink className="size-4 mr-2" />
                              Open Service
                            </a>
                          </DropdownMenuItem>
                        )}
                        <DropdownMenuSeparator />
                        <DropdownMenuItem
                          className="text-destructive"
                          onClick={() => handleDeleteService(service.id, service.name)}
                        >
                          <Trash2 className="size-4 mr-2" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <Server className="size-12 mx-auto mb-4 opacity-50" />
              <p>No services configured</p>
              <p className="text-sm mt-1">Add web UIs, APIs, or ML deployments</p>
              <Button 
                variant="outline" 
                className="mt-4"
                onClick={() => setAddDialogOpen(true)}
              >
                <Plus className="size-4 mr-2" />
                Add First Service
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      <AddServiceDialog
        projectId={projectId}
        open={addDialogOpen}
        onOpenChange={setAddDialogOpen}
        onCreated={() => mutate()}
      />
    </>
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

const API_BASE = "http://localhost:8080/api/v1";

interface GitStatus {
  project_id: string;
  is_git_repo: boolean;
  branch?: string;
  is_clean: boolean;
  staged_files: string[];
  modified_files: string[];
  untracked_files: string[];
  ahead: number;
  behind: number;
  has_remote: boolean;
  remote_url?: string;
}

interface SSHKey {
  name: string;
  path: string;
  has_public_key: boolean;
  public_key?: string;
  created?: string;
}

function useGitStatus(projectId: string) {
  const [data, setData] = React.useState<GitStatus | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);

  const refresh = React.useCallback(() => {
    setIsLoading(true);
    fetch(`${API_BASE}/projects/${projectId}/git/status`)
      .then((res) => res.json())
      .then((data) => {
        setData(data);
        setIsLoading(false);
      })
      .catch(() => {
        setData(null);
        setIsLoading(false);
      });
  }, [projectId]);

  React.useEffect(() => {
    refresh();
  }, [refresh]);

  return { data, isLoading, refresh };
}

function useSSHKeys() {
  const [data, setData] = React.useState<SSHKey[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);

  const refresh = React.useCallback(() => {
    setIsLoading(true);
    fetch(`${API_BASE}/projects/ssh-keys`)
      .then((res) => res.json())
      .then((data) => {
        setData(data || []);
        setIsLoading(false);
      })
      .catch(() => {
        setData([]);
        setIsLoading(false);
      });
  }, []);

  React.useEffect(() => {
    refresh();
  }, [refresh]);

  return { data, isLoading, refresh };
}

function ProjectGitTab({ projectId }: { projectId: string }) {
  const { data: gitConfig, isLoading: isConfigLoading, mutate } = useProjectGitConfig(projectId);
  const { trigger: updateGitConfig, isMutating: isUpdating } = useUpdateProjectGitConfig(projectId);
  const { trigger: syncGit, isMutating: isSyncing } = useSyncProjectGit(projectId);
  const { data: gitStatus, isLoading: isStatusLoading, refresh: refreshStatus } = useGitStatus(projectId);
  const { data: sshKeys, refresh: refreshKeys } = useSSHKeys();

  const [formData, setFormData] = React.useState({
    remote_url: "",
    branch: "main",
    auto_sync: false,
  });

  const [isInitializing, setIsInitializing] = React.useState(false);
  const [isCloning, setIsCloning] = React.useState(false);
  const [cloneUrl, setCloneUrl] = React.useState("");
  const [showCloneDialog, setShowCloneDialog] = React.useState(false);
  const [showKeyDialog, setShowKeyDialog] = React.useState(false);
  const [newKeyName, setNewKeyName] = React.useState("");
  const [isGeneratingKey, setIsGeneratingKey] = React.useState(false);

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
      toast.success("Git sync completed");
      refreshStatus();
    } catch (error) {
      toast.error("Failed to sync repository");
    }
  };

  const handleInit = async () => {
    setIsInitializing(true);
    try {
      const response = await fetch(`${API_BASE}/projects/${projectId}/git/init`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ initial_branch: "main" }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to initialize repository");
      }

      toast.success("Git repository initialized");
      refreshStatus();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to initialize repository");
    } finally {
      setIsInitializing(false);
    }
  };

  const handleClone = async () => {
    if (!cloneUrl.trim()) {
      toast.error("Repository URL is required");
      return;
    }

    setIsCloning(true);
    try {
      const response = await fetch(`${API_BASE}/projects/${projectId}/git/clone`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: cloneUrl.trim() }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to clone repository");
      }

      toast.success("Repository cloned successfully");
      setShowCloneDialog(false);
      setCloneUrl("");
      refreshStatus();
      mutate();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to clone repository");
    } finally {
      setIsCloning(false);
    }
  };

  const handleGenerateKey = async () => {
    if (!newKeyName.trim()) {
      toast.error("Key name is required");
      return;
    }

    setIsGeneratingKey(true);
    try {
      const response = await fetch(`${API_BASE}/projects/ssh-keys`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: newKeyName.trim(), key_type: "ed25519" }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to generate key");
      }

      toast.success("SSH key generated");
      setShowKeyDialog(false);
      setNewKeyName("");
      refreshKeys();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to generate key");
    } finally {
      setIsGeneratingKey(false);
    }
  };

  const handleCopyPublicKey = (publicKey: string) => {
    navigator.clipboard.writeText(publicKey);
    toast.success("Public key copied to clipboard");
  };

  const isLoading = isConfigLoading || isStatusLoading;

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

  const isGitRepo = gitStatus?.is_git_repo ?? false;

  return (
    <div className="space-y-6">
      {/* Repository Status */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <GitBranch className="size-5" />
                Repository Status
              </CardTitle>
              <CardDescription>
                {isGitRepo ? "Git repository is configured" : "No git repository detected"}
              </CardDescription>
            </div>
            {isGitRepo && gitStatus?.has_remote && (
              <Button variant="outline" onClick={handleSync} disabled={isSyncing}>
                {isSyncing ? (
                  <>
                    <Loader2 className="size-4 mr-2 animate-spin" />
                    Syncing...
                  </>
                ) : (
                  <>
                    <RefreshCw className="size-4 mr-2" />
                    Sync
                  </>
                )}
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {!isGitRepo ? (
            <div className="space-y-4">
              <div className="p-6 rounded-lg border-2 border-dashed text-center">
                <GitBranch className="size-10 mx-auto mb-3 text-muted-foreground" />
                <p className="text-sm text-muted-foreground mb-4">
                  This project doesn&apos;t have a git repository yet
                </p>
                <div className="flex items-center justify-center gap-3">
                  <Button onClick={handleInit} disabled={isInitializing}>
                    {isInitializing ? (
                      <>
                        <Loader2 className="size-4 mr-2 animate-spin" />
                        Initializing...
                      </>
                    ) : (
                      <>
                        <Plus className="size-4 mr-2" />
                        Initialize Repository
                      </>
                    )}
                  </Button>
                  <Button variant="outline" onClick={() => setShowCloneDialog(true)}>
                    <Cloud className="size-4 mr-2" />
                    Clone from URL
                  </Button>
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Status Overview */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 rounded-lg border bg-muted/30">
                  <p className="text-sm text-muted-foreground">Branch</p>
                  <p className="font-medium">{gitStatus?.branch || "unknown"}</p>
                </div>
                <div className="p-4 rounded-lg border bg-muted/30">
                  <p className="text-sm text-muted-foreground">Status</p>
                  <div className="flex items-center gap-2">
                    {gitStatus?.is_clean ? (
                      <>
                        <CheckCircle2 className="size-4 text-green-500" />
                        <span className="font-medium">Clean</span>
                      </>
                    ) : (
                      <>
                        <XCircle className="size-4 text-yellow-500" />
                        <span className="font-medium">Modified</span>
                      </>
                    )}
                  </div>
                </div>
                <div className="p-4 rounded-lg border bg-muted/30">
                  <p className="text-sm text-muted-foreground">Ahead/Behind</p>
                  <p className="font-medium">
                    {gitStatus?.ahead || 0} / {gitStatus?.behind || 0}
                  </p>
                </div>
                <div className="p-4 rounded-lg border bg-muted/30">
                  <p className="text-sm text-muted-foreground">Remote</p>
                  <p className="font-medium">{gitStatus?.has_remote ? "Connected" : "None"}</p>
                </div>
              </div>

              {/* Modified Files */}
              {!gitStatus?.is_clean && (
                <div className="p-4 rounded-lg border">
                  <p className="text-sm font-medium mb-2">Changes</p>
                  <div className="space-y-2 text-sm">
                    {(gitStatus?.staged_files || []).map((file) => (
                      <div key={file} className="flex items-center gap-2 text-green-600">
                        <CheckCircle2 className="size-3" />
                        <span>Staged: {file}</span>
                      </div>
                    ))}
                    {(gitStatus?.modified_files || []).map((file) => (
                      <div key={file} className="flex items-center gap-2 text-yellow-600">
                        <Code className="size-3" />
                        <span>Modified: {file}</span>
                      </div>
                    ))}
                    {(gitStatus?.untracked_files || []).slice(0, 5).map((file) => (
                      <div key={file} className="flex items-center gap-2 text-muted-foreground">
                        <Plus className="size-3" />
                        <span>Untracked: {file}</span>
                      </div>
                    ))}
                    {(gitStatus?.untracked_files || []).length > 5 && (
                      <p className="text-xs text-muted-foreground">
                        ...and {gitStatus!.untracked_files.length - 5} more untracked files
                      </p>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Remote Configuration */}
      {isGitRepo && (
        <Card>
          <CardHeader>
            <CardTitle>Remote Configuration</CardTitle>
            <CardDescription>Configure the remote repository connection</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="remote_url">Repository URL</Label>
              <Input
                id="remote_url"
                placeholder="https://github.com/user/repo.git"
                value={formData.remote_url}
                onChange={(e) => setFormData({ ...formData, remote_url: e.target.value })}
              />
              <p className="text-xs text-muted-foreground">HTTPS or SSH URL</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="branch">Default Branch</Label>
              <Input
                id="branch"
                placeholder="main"
                value={formData.branch}
                onChange={(e) => setFormData({ ...formData, branch: e.target.value })}
              />
            </div>

            <div className="flex items-center justify-between p-4 rounded-lg border">
              <div>
                <p className="font-medium">Auto Sync</p>
                <p className="text-sm text-muted-foreground">
                  Automatically sync changes with remote
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
      )}

      {/* SSH Keys */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>SSH Keys</CardTitle>
              <CardDescription>Manage SSH keys for Git authentication</CardDescription>
            </div>
            <Button variant="outline" size="sm" onClick={() => setShowKeyDialog(true)}>
              <Plus className="size-4 mr-2" />
              Generate Key
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {sshKeys.length === 0 ? (
            <div className="text-center py-6 text-muted-foreground">
              <Terminal className="size-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No SSH keys generated yet</p>
            </div>
          ) : (
            <div className="space-y-3">
              {sshKeys.map((key) => (
                <div key={key.name} className="p-4 rounded-lg border bg-muted/30">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium">{key.name}</span>
                    {key.public_key && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleCopyPublicKey(key.public_key!)}
                      >
                        Copy Public Key
                      </Button>
                    )}
                  </div>
                  {key.public_key && (
                    <pre className="text-xs bg-muted p-2 rounded overflow-x-auto">
                      {key.public_key.substring(0, 80)}...
                    </pre>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Clone Dialog */}
      <Dialog open={showCloneDialog} onOpenChange={setShowCloneDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Clone Repository</DialogTitle>
            <DialogDescription>Enter the URL of the repository to clone</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="clone-url">Repository URL</Label>
              <Input
                id="clone-url"
                placeholder="https://github.com/user/repo.git"
                value={cloneUrl}
                onChange={(e) => setCloneUrl(e.target.value)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCloneDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleClone} disabled={isCloning}>
              {isCloning ? (
                <>
                  <Loader2 className="size-4 mr-2 animate-spin" />
                  Cloning...
                </>
              ) : (
                <>
                  <Cloud className="size-4 mr-2" />
                  Clone
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Generate Key Dialog */}
      <Dialog open={showKeyDialog} onOpenChange={setShowKeyDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Generate SSH Key</DialogTitle>
            <DialogDescription>Create a new SSH key for Git authentication</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="key-name">Key Name</Label>
              <Input
                id="key-name"
                placeholder="my-project-key"
                value={newKeyName}
                onChange={(e) => setNewKeyName(e.target.value)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowKeyDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleGenerateKey} disabled={isGeneratingKey}>
              {isGeneratingKey ? (
                <>
                  <Loader2 className="size-4 mr-2 animate-spin" />
                  Generating...
                </>
              ) : (
                "Generate Key"
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
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
              <HelpTooltip content="Send selected note text to the AI generator to draft a component.">
                <Button 
                  size="sm" 
                  variant="secondary"
                  onClick={handleGenerateFromSelection}
                  className="gap-2"
                >
                  <Sparkles className="size-4" />
                  Generate from Selection
                </Button>
              </HelpTooltip>
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
                  <HelpTooltip content="Draft a component directly from this note without saving it first.">
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => generationModal.openWithNotes(newNote)}
                    >
                      <Sparkles className="size-4" />
                    </Button>
                  </HelpTooltip>
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
                    <HelpTooltip content="Turn this note into a starter component with the AI generator.">
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-xs h-7 opacity-0 group-hover:opacity-100 transition-opacity"
                        onClick={() => handleGenerateFromNote(note.content)}
                      >
                        <Sparkles className="size-3 mr-1" />
                        Generate
                      </Button>
                    </HelpTooltip>
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

