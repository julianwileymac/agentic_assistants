"use client";

import * as React from "react";
import Link from "next/link";
import { 
  Plus, 
  Search, 
  Filter, 
  MoreHorizontal, 
  Database, 
  Pencil, 
  Trash2,
  Globe,
  FolderClosed,
  RefreshCw,
  CheckCircle2,
  XCircle,
  Clock,
  ArrowUpRight,
  Link2,
  Table2,
  HardDrive,
  Plug
} from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { 
  useDataSources, 
  useTestDataSource, 
  usePromoteDataSource,
  useDeleteDataSource,
  useCreateDataSource,
  useProjects,
} from "@/lib/api";
import type { DataSource } from "@/lib/types";
import { toast } from "sonner";

const sourceTypeIcons: Record<string, React.ReactNode> = {
  database: <Database className="size-5" />,
  file_store: <HardDrive className="size-5" />,
  api: <Plug className="size-5" />,
};

const sourceTypeColors: Record<string, string> = {
  database: "from-blue-500 to-indigo-500",
  file_store: "from-emerald-500 to-teal-500",
  api: "from-purple-500 to-pink-500",
};

const statusBadgeStyles: Record<string, string> = {
  active: "bg-green-500/10 text-green-500 border-green-500/20",
  inactive: "bg-gray-500/10 text-gray-500 border-gray-500/20",
  error: "bg-red-500/10 text-red-500 border-red-500/20",
};

function DataSourceCard({ 
  dataSource, 
  onDelete, 
  onTest,
  onPromote,
  isTestingConnection,
}: { 
  dataSource: DataSource; 
  onDelete: () => void;
  onTest: () => void;
  onPromote: () => void;
  isTestingConnection?: boolean;
}) {
  return (
    <Card className="group hover:shadow-lg transition-all duration-300">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg bg-gradient-to-br ${sourceTypeColors[dataSource.source_type] || 'from-gray-500 to-gray-600'} text-white`}>
              {sourceTypeIcons[dataSource.source_type] || <Database className="size-5" />}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <CardTitle className="text-lg">
                  <Link href={`/datasources/${dataSource.id}`} className="hover:underline">
                    {dataSource.name}
                  </Link>
                </CardTitle>
                {dataSource.is_global && (
                  <Badge variant="secondary" className="text-xs gap-1">
                    <Globe className="size-3" />
                    Global
                  </Badge>
                )}
              </div>
              <CardDescription className="line-clamp-1">
                {dataSource.description || "No description"}
              </CardDescription>
            </div>
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="opacity-0 group-hover:opacity-100 transition-opacity">
                <MoreHorizontal className="size-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem asChild>
                <Link href={`/datasources/${dataSource.id}`}>
                  <Pencil className="size-4 mr-2" />
                  Edit
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem onClick={onTest}>
                <RefreshCw className="size-4 mr-2" />
                Test Connection
              </DropdownMenuItem>
              {!dataSource.is_global && (
                <DropdownMenuItem onClick={onPromote}>
                  <ArrowUpRight className="size-4 mr-2" />
                  Promote to Global
                </DropdownMenuItem>
              )}
              <DropdownMenuSeparator />
              <DropdownMenuItem className="text-destructive" onClick={onDelete}>
                <Trash2 className="size-4 mr-2" />
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-center justify-between">
          <Badge variant="outline" className="gap-1">
            {sourceTypeIcons[dataSource.source_type]}
            {dataSource.source_type.replace('_', ' ')}
          </Badge>
          <div className="flex items-center gap-2">
            {isTestingConnection ? (
              <Badge variant="secondary" className="gap-1">
                <RefreshCw className="size-3 animate-spin" />
                Testing...
              </Badge>
            ) : dataSource.last_test_success !== null ? (
              <Badge 
                variant="outline" 
                className={dataSource.last_test_success ? statusBadgeStyles.active : statusBadgeStyles.error}
              >
                {dataSource.last_test_success ? (
                  <CheckCircle2 className="size-3 mr-1" />
                ) : (
                  <XCircle className="size-3 mr-1" />
                )}
                {dataSource.last_test_success ? 'Connected' : 'Failed'}
              </Badge>
            ) : (
              <Badge variant="outline" className={statusBadgeStyles.inactive}>
                <Clock className="size-3 mr-1" />
                Not tested
              </Badge>
            )}
          </div>
        </div>
        
        {dataSource.project_id && (
          <div className="flex items-center gap-1 text-sm text-muted-foreground">
            <FolderClosed className="size-3" />
            <Link href={`/projects/${dataSource.project_id}`} className="hover:underline">
              Project Scoped
            </Link>
          </div>
        )}

        {dataSource.tags.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {dataSource.tags.slice(0, 3).map((tag) => (
              <Badge key={tag} variant="secondary" className="text-xs">
                {tag}
              </Badge>
            ))}
            {dataSource.tags.length > 3 && (
              <Badge variant="secondary" className="text-xs">
                +{dataSource.tags.length - 3}
              </Badge>
            )}
          </div>
        )}

        <div className="text-xs text-muted-foreground">
          Updated {new Date(dataSource.updated_at).toLocaleDateString()}
        </div>
      </CardContent>
    </Card>
  );
}

function CreateDataSourceDialog({ 
  open, 
  onOpenChange, 
  onCreated 
}: { 
  open: boolean; 
  onOpenChange: (open: boolean) => void;
  onCreated: () => void;
}) {
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const { trigger: createDataSource } = useCreateDataSource();
  const { data: projects } = useProjects();

  const [formData, setFormData] = React.useState({
    name: "",
    source_type: "database",
    description: "",
    is_global: false,
    project_id: "",
    connection_config: "{\n  \n}",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name.trim()) {
      toast.error("Name is required");
      return;
    }

    setIsSubmitting(true);
    try {
      let connectionConfig: Record<string, unknown> = {};
      try {
        connectionConfig = JSON.parse(formData.connection_config);
      } catch {
        toast.error("Invalid JSON in connection config");
        setIsSubmitting(false);
        return;
      }

      await createDataSource({
        name: formData.name.trim(),
        source_type: formData.source_type,
        description: formData.description.trim(),
        is_global: formData.is_global,
        project_id: formData.project_id || undefined,
        connection_config: connectionConfig,
      });

      toast.success("Data source created");
      onOpenChange(false);
      onCreated();
      setFormData({
        name: "",
        source_type: "database",
        description: "",
        is_global: false,
        project_id: "",
        connection_config: "{\n  \n}",
      });
    } catch (error) {
      toast.error("Failed to create data source");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Create Data Source</DialogTitle>
            <DialogDescription>
              Add a new database, file store, or API connection
            </DialogDescription>
          </DialogHeader>
          
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="name">Name *</Label>
              <Input
                id="name"
                placeholder="My Database"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </div>

            <div className="grid gap-2">
              <Label htmlFor="source_type">Type</Label>
              <Select 
                value={formData.source_type} 
                onValueChange={(v) => setFormData({ ...formData, source_type: v })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="database">
                    <div className="flex items-center gap-2">
                      <Database className="size-4" />
                      Database
                    </div>
                  </SelectItem>
                  <SelectItem value="file_store">
                    <div className="flex items-center gap-2">
                      <HardDrive className="size-4" />
                      File Store
                    </div>
                  </SelectItem>
                  <SelectItem value="api">
                    <div className="flex items-center gap-2">
                      <Plug className="size-4" />
                      API
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="grid gap-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                placeholder="Brief description of this data source..."
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={2}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label htmlFor="scope">Scope</Label>
                <Select 
                  value={formData.is_global ? "global" : "project"} 
                  onValueChange={(v) => setFormData({ 
                    ...formData, 
                    is_global: v === "global",
                    project_id: v === "global" ? "" : formData.project_id
                  })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="global">
                      <div className="flex items-center gap-2">
                        <Globe className="size-4" />
                        Global
                      </div>
                    </SelectItem>
                    <SelectItem value="project">
                      <div className="flex items-center gap-2">
                        <FolderClosed className="size-4" />
                        Project
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {!formData.is_global && (
                <div className="grid gap-2">
                  <Label htmlFor="project">Project</Label>
                  <Select 
                    value={formData.project_id} 
                    onValueChange={(v) => setFormData({ ...formData, project_id: v })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select project..." />
                    </SelectTrigger>
                    <SelectContent>
                      {projects?.items.map((project) => (
                        <SelectItem key={project.id} value={project.id}>
                          {project.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}
            </div>

            <div className="grid gap-2">
              <Label htmlFor="connection_config">Connection Config (JSON)</Label>
              <Textarea
                id="connection_config"
                placeholder='{"host": "localhost", "port": 5432}'
                value={formData.connection_config}
                onChange={(e) => setFormData({ ...formData, connection_config: e.target.value })}
                rows={5}
                className="font-mono text-sm"
              />
              <p className="text-xs text-muted-foreground">
                Connection configuration varies by type. Check documentation for required fields.
              </p>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Creating..." : "Create Data Source"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export default function DataSourcesPage() {
  const [typeFilter, setTypeFilter] = React.useState<string>("all");
  const [scopeFilter, setScopeFilter] = React.useState<string>("all");
  const [searchQuery, setSearchQuery] = React.useState("");
  const [createDialogOpen, setCreateDialogOpen] = React.useState(false);
  const [testingIds, setTestingIds] = React.useState<Set<string>>(new Set());

  const { data, isLoading, mutate } = useDataSources({
    source_type: typeFilter === "all" ? undefined : typeFilter,
    is_global: scopeFilter === "all" ? undefined : scopeFilter === "global",
  });

  const handleDelete = async (id: string, name: string) => {
    if (!confirm(`Are you sure you want to delete "${name}"?`)) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8080/api/v1/datasources/${id}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        toast.success(`Data source "${name}" deleted`);
        mutate();
      } else {
        toast.error("Failed to delete data source");
      }
    } catch (error) {
      toast.error("Failed to delete data source");
    }
  };

  const handleTest = async (id: string) => {
    setTestingIds(prev => new Set([...prev, id]));
    try {
      const response = await fetch(`http://localhost:8080/api/v1/datasources/${id}/test`, {
        method: 'POST',
      });

      const result = await response.json();
      if (result.success) {
        toast.success("Connection successful");
      } else {
        toast.error(result.message || "Connection failed");
      }
      mutate();
    } catch (error) {
      toast.error("Failed to test connection");
    } finally {
      setTestingIds(prev => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    }
  };

  const handlePromote = async (id: string, name: string) => {
    if (!confirm(`Promote "${name}" to a global data source?`)) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8080/api/v1/datasources/${id}/promote`, {
        method: 'POST',
      });

      if (response.ok) {
        toast.success(`"${name}" is now a global data source`);
        mutate();
      } else {
        toast.error("Failed to promote data source");
      }
    } catch (error) {
      toast.error("Failed to promote data source");
    }
  };

  const filteredDataSources = React.useMemo(() => {
    if (!data?.items) return [];
    if (!searchQuery) return data.items;

    const query = searchQuery.toLowerCase();
    return data.items.filter(
      (ds) =>
        ds.name.toLowerCase().includes(query) ||
        ds.description.toLowerCase().includes(query) ||
        ds.tags.some((t) => t.toLowerCase().includes(query))
    );
  }, [data?.items, searchQuery]);

  const globalSources = filteredDataSources.filter(ds => ds.is_global);
  const projectSources = filteredDataSources.filter(ds => !ds.is_global);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Data Sources</h1>
          <p className="text-muted-foreground">
            Manage database connections, file stores, and API integrations
          </p>
        </div>
        <Button onClick={() => setCreateDialogOpen(true)}>
          <Plus className="size-4 mr-2" />
          New Data Source
        </Button>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Sources</p>
                <p className="text-2xl font-bold">{data?.total || 0}</p>
              </div>
              <Database className="size-8 text-muted-foreground/30" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Global Sources</p>
                <p className="text-2xl font-bold">{globalSources.length}</p>
              </div>
              <Globe className="size-8 text-muted-foreground/30" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Connected</p>
                <p className="text-2xl font-bold text-green-500">
                  {filteredDataSources.filter(ds => ds.last_test_success).length}
                </p>
              </div>
              <CheckCircle2 className="size-8 text-green-500/30" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Databases</p>
                <p className="text-2xl font-bold">
                  {filteredDataSources.filter(ds => ds.source_type === 'database').length}
                </p>
              </div>
              <Table2 className="size-8 text-muted-foreground/30" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
          <Input
            placeholder="Search data sources..."
            className="pl-9"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <Select value={typeFilter} onValueChange={setTypeFilter}>
          <SelectTrigger className="w-40">
            <Filter className="size-4 mr-2" />
            <SelectValue placeholder="Type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            <SelectItem value="database">Database</SelectItem>
            <SelectItem value="file_store">File Store</SelectItem>
            <SelectItem value="api">API</SelectItem>
          </SelectContent>
        </Select>
        <Select value={scopeFilter} onValueChange={setScopeFilter}>
          <SelectTrigger className="w-40">
            <Globe className="size-4 mr-2" />
            <SelectValue placeholder="Scope" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Scopes</SelectItem>
            <SelectItem value="global">Global</SelectItem>
            <SelectItem value="project">Project</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Tabs for Global vs Project */}
      <Tabs defaultValue="all" className="space-y-4">
        <TabsList>
          <TabsTrigger value="all">All ({filteredDataSources.length})</TabsTrigger>
          <TabsTrigger value="global">Global ({globalSources.length})</TabsTrigger>
          <TabsTrigger value="project">Project ({projectSources.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="all">
          {isLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <Card key={i}>
                  <CardHeader>
                    <Skeleton className="h-6 w-3/4" />
                    <Skeleton className="h-4 w-1/2" />
                  </CardHeader>
                  <CardContent>
                    <Skeleton className="h-4 w-1/4" />
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : filteredDataSources.length === 0 ? (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center py-12">
                  <Database className="size-12 mx-auto mb-4 opacity-50" />
                  <h3 className="text-lg font-semibold mb-2">No data sources found</h3>
                  <p className="text-muted-foreground mb-4">
                    {searchQuery
                      ? "Try a different search term"
                      : "Create your first data source to connect to databases, file stores, or APIs"}
                  </p>
                  {!searchQuery && (
                    <Button onClick={() => setCreateDialogOpen(true)}>
                      <Plus className="size-4 mr-2" />
                      Create Data Source
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredDataSources.map((ds) => (
                <DataSourceCard
                  key={ds.id}
                  dataSource={ds}
                  onDelete={() => handleDelete(ds.id, ds.name)}
                  onTest={() => handleTest(ds.id)}
                  onPromote={() => handlePromote(ds.id, ds.name)}
                  isTestingConnection={testingIds.has(ds.id)}
                />
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="global">
          {globalSources.length === 0 ? (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center py-12">
                  <Globe className="size-12 mx-auto mb-4 opacity-50" />
                  <h3 className="text-lg font-semibold mb-2">No global data sources</h3>
                  <p className="text-muted-foreground mb-4">
                    Global data sources are available to all projects
                  </p>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {globalSources.map((ds) => (
                <DataSourceCard
                  key={ds.id}
                  dataSource={ds}
                  onDelete={() => handleDelete(ds.id, ds.name)}
                  onTest={() => handleTest(ds.id)}
                  onPromote={() => handlePromote(ds.id, ds.name)}
                  isTestingConnection={testingIds.has(ds.id)}
                />
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="project">
          {projectSources.length === 0 ? (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center py-12">
                  <FolderClosed className="size-12 mx-auto mb-4 opacity-50" />
                  <h3 className="text-lg font-semibold mb-2">No project data sources</h3>
                  <p className="text-muted-foreground mb-4">
                    Project-scoped data sources are only available within their associated project
                  </p>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {projectSources.map((ds) => (
                <DataSourceCard
                  key={ds.id}
                  dataSource={ds}
                  onDelete={() => handleDelete(ds.id, ds.name)}
                  onTest={() => handleTest(ds.id)}
                  onPromote={() => handlePromote(ds.id, ds.name)}
                  isTestingConnection={testingIds.has(ds.id)}
                />
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Create Dialog */}
      <CreateDataSourceDialog 
        open={createDialogOpen} 
        onOpenChange={setCreateDialogOpen}
        onCreated={() => mutate()}
      />
    </div>
  );
}



