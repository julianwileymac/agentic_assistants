"use client";

import * as React from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
import { 
  ArrowLeft, 
  Save, 
  Loader2, 
  Trash2, 
  Database,
  HardDrive,
  Plug,
  Globe,
  FolderClosed,
  RefreshCw,
  CheckCircle2,
  XCircle,
  Clock,
  ArrowUpRight,
  Table2,
  Eye,
  EyeOff,
} from "lucide-react";

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
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { 
  useDataSource, 
  useDataSourceSchema,
  useProjects,
} from "@/lib/api";
import { toast } from "sonner";

const sourceTypeIcons: Record<string, React.ReactNode> = {
  database: <Database className="size-5" />,
  file_store: <HardDrive className="size-5" />,
  api: <Plug className="size-5" />,
};

export default function DataSourceDetailPage() {
  const router = useRouter();
  const params = useParams();
  const dataSourceId = params.id as string;

  const { data: dataSource, isLoading, mutate } = useDataSource(dataSourceId);
  const { data: schema, isLoading: isLoadingSchema, mutate: mutateSchema } = useDataSourceSchema(dataSourceId);
  const { data: projects } = useProjects();

  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [isTesting, setIsTesting] = React.useState(false);
  const [showConnectionConfig, setShowConnectionConfig] = React.useState(false);

  const [formData, setFormData] = React.useState({
    name: "",
    source_type: "database",
    description: "",
    is_global: false,
    project_id: "",
    connection_config: "{}",
    tags: "",
  });

  React.useEffect(() => {
    if (dataSource) {
      setFormData({
        name: dataSource.name,
        source_type: dataSource.source_type,
        description: dataSource.description,
        is_global: dataSource.is_global,
        project_id: dataSource.project_id || "",
        connection_config: dataSource.connection_config || "{}",
        tags: dataSource.tags.join(", "),
      });
    }
  }, [dataSource]);

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

      const response = await fetch(`http://localhost:8080/api/v1/datasources/${dataSourceId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: formData.name.trim(),
          source_type: formData.source_type,
          description: formData.description.trim(),
          is_global: formData.is_global,
          project_id: formData.project_id || null,
          connection_config: connectionConfig,
          tags: formData.tags
            .split(",")
            .map((t) => t.trim())
            .filter(Boolean),
        }),
      });

      if (response.ok) {
        toast.success("Data source updated successfully");
        mutate();
      } else {
        const error = await response.json();
        toast.error(error.detail || "Failed to update data source");
      }
    } catch (error) {
      toast.error("Failed to update data source");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async () => {
    try {
      const response = await fetch(`http://localhost:8080/api/v1/datasources/${dataSourceId}`, {
        method: "DELETE",
      });

      if (response.ok) {
        toast.success("Data source deleted");
        router.push("/datasources");
      } else {
        toast.error("Failed to delete data source");
      }
    } catch (error) {
      toast.error("Failed to delete data source");
    }
  };

  const handleTestConnection = async () => {
    setIsTesting(true);
    try {
      const response = await fetch(`http://localhost:8080/api/v1/datasources/${dataSourceId}/test`, {
        method: "POST",
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
      setIsTesting(false);
    }
  };

  const handlePromote = async () => {
    try {
      const response = await fetch(`http://localhost:8080/api/v1/datasources/${dataSourceId}/promote`, {
        method: "POST",
      });

      if (response.ok) {
        toast.success("Data source promoted to global");
        mutate();
      } else {
        toast.error("Failed to promote data source");
      }
    } catch (error) {
      toast.error("Failed to promote data source");
    }
  };

  const handleDiscoverSchema = async () => {
    try {
      toast.info("Discovering schema...");
      mutateSchema();
      toast.success("Schema updated");
    } catch (error) {
      toast.error("Failed to discover schema");
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

  if (!dataSource) {
    return (
      <div className="max-w-4xl mx-auto">
        <Card>
          <CardContent className="pt-6 text-center">
            <p className="text-muted-foreground">Data source not found</p>
            <Button asChild className="mt-4">
              <Link href="/datasources">Back to Data Sources</Link>
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
            <Link href="/datasources">
              <ArrowLeft className="size-4" />
            </Link>
          </Button>
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-500 text-white">
              {sourceTypeIcons[dataSource.source_type] || <Database className="size-5" />}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-3xl font-bold tracking-tight">{dataSource.name}</h1>
                {dataSource.is_global && (
                  <Badge variant="secondary" className="gap-1">
                    <Globe className="size-3" />
                    Global
                  </Badge>
                )}
              </div>
              <p className="text-muted-foreground">
                {dataSource.source_type.replace('_', ' ')} • Created {new Date(dataSource.created_at).toLocaleDateString()}
              </p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={handleTestConnection} disabled={isTesting}>
            {isTesting ? (
              <>
                <Loader2 className="size-4 mr-2 animate-spin" />
                Testing...
              </>
            ) : (
              <>
                <RefreshCw className="size-4 mr-2" />
                Test Connection
              </>
            )}
          </Button>
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button variant="destructive" size="sm">
                <Trash2 className="size-4 mr-2" />
                Delete
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Delete Data Source?</AlertDialogTitle>
                <AlertDialogDescription>
                  This will permanently delete &quot;{dataSource.name}&quot; and remove it from all projects.
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
      </div>

      {/* Connection Status Banner */}
      <Card className={`border-l-4 ${
        dataSource.last_test_success 
          ? 'border-l-green-500 bg-green-500/5' 
          : dataSource.last_test_success === false
          ? 'border-l-red-500 bg-red-500/5'
          : 'border-l-gray-400 bg-gray-500/5'
      }`}>
        <CardContent className="py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {dataSource.last_test_success ? (
                <CheckCircle2 className="size-5 text-green-500" />
              ) : dataSource.last_test_success === false ? (
                <XCircle className="size-5 text-red-500" />
              ) : (
                <Clock className="size-5 text-muted-foreground" />
              )}
              <div>
                <p className="font-medium">
                  {dataSource.last_test_success 
                    ? 'Connected' 
                    : dataSource.last_test_success === false 
                    ? 'Connection Failed'
                    : 'Not Tested'}
                </p>
                {dataSource.last_tested && (
                  <p className="text-sm text-muted-foreground">
                    Last tested {new Date(dataSource.last_tested).toLocaleString()}
                  </p>
                )}
              </div>
            </div>
            {!dataSource.is_global && (
              <Button variant="outline" size="sm" onClick={handlePromote}>
                <ArrowUpRight className="size-4 mr-2" />
                Promote to Global
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Tabs */}
      <Tabs defaultValue="details">
        <TabsList>
          <TabsTrigger value="details">Details</TabsTrigger>
          <TabsTrigger value="schema">Schema</TabsTrigger>
          <TabsTrigger value="usage">Usage</TabsTrigger>
        </TabsList>

        {/* Details Tab */}
        <TabsContent value="details">
          <form onSubmit={handleSubmit}>
            <Card>
              <CardHeader>
                <CardTitle>Data Source Details</CardTitle>
                <CardDescription>
                  Edit the connection configuration
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Name */}
                <div className="space-y-2">
                  <Label htmlFor="name">Name *</Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                  />
                </div>

                {/* Type */}
                <div className="space-y-2">
                  <Label htmlFor="source_type">Type</Label>
                  <Select
                    value={formData.source_type}
                    onValueChange={(v) => setFormData({ ...formData, source_type: v })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="database">Database</SelectItem>
                      <SelectItem value="file_store">File Store</SelectItem>
                      <SelectItem value="api">API</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Description */}
                <div className="space-y-2">
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    rows={3}
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  />
                </div>

                {/* Scope */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="scope">Scope</Label>
                    <Select
                      value={formData.is_global ? "global" : "project"}
                      onValueChange={(v) => setFormData({ 
                        ...formData, 
                        is_global: v === "global",
                        project_id: v === "global" ? "" : formData.project_id,
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
                    <div className="space-y-2">
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

                {/* Tags */}
                <div className="space-y-2">
                  <Label htmlFor="tags">Tags</Label>
                  <Input
                    id="tags"
                    placeholder="postgres, production (comma separated)"
                    value={formData.tags}
                    onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                  />
                </div>

                {/* Connection Config */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="connection_config">Connection Config (JSON)</Label>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => setShowConnectionConfig(!showConnectionConfig)}
                    >
                      {showConnectionConfig ? (
                        <>
                          <EyeOff className="size-4 mr-2" />
                          Hide
                        </>
                      ) : (
                        <>
                          <Eye className="size-4 mr-2" />
                          Show
                        </>
                      )}
                    </Button>
                  </div>
                  {showConnectionConfig ? (
                    <Textarea
                      id="connection_config"
                      rows={8}
                      className="font-mono text-sm"
                      value={formData.connection_config}
                      onChange={(e) => setFormData({ ...formData, connection_config: e.target.value })}
                    />
                  ) : (
                    <div className="p-4 rounded-md bg-muted/50 border text-sm text-muted-foreground">
                      Connection configuration hidden for security. Click &quot;Show&quot; to view and edit.
                    </div>
                  )}
                  <p className="text-xs text-muted-foreground">
                    Store sensitive values like passwords as environment variable references
                  </p>
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

        {/* Schema Tab */}
        <TabsContent value="schema">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Schema Discovery</CardTitle>
                  <CardDescription>
                    View discovered tables, columns, and data types
                  </CardDescription>
                </div>
                <Button variant="outline" onClick={handleDiscoverSchema}>
                  <RefreshCw className="size-4 mr-2" />
                  Refresh Schema
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {isLoadingSchema ? (
                <div className="space-y-4">
                  <Skeleton className="h-12 w-full" />
                  <Skeleton className="h-12 w-full" />
                  <Skeleton className="h-12 w-full" />
                </div>
              ) : schema?.tables && schema.tables.length > 0 ? (
                <Accordion type="single" collapsible className="w-full">
                  {schema.tables.map((table, index) => (
                    <AccordionItem key={index} value={table.name}>
                      <AccordionTrigger>
                        <div className="flex items-center gap-2">
                          <Table2 className="size-4" />
                          <span className="font-medium">{table.name}</span>
                          <Badge variant="secondary" className="text-xs ml-2">
                            {table.columns?.length || 0} columns
                          </Badge>
                          {table.row_count !== undefined && (
                            <Badge variant="outline" className="text-xs">
                              {table.row_count.toLocaleString()} rows
                            </Badge>
                          )}
                        </div>
                      </AccordionTrigger>
                      <AccordionContent>
                        <div className="border rounded-md overflow-hidden">
                          <table className="w-full text-sm">
                            <thead className="bg-muted/50">
                              <tr>
                                <th className="px-4 py-2 text-left font-medium">Column</th>
                                <th className="px-4 py-2 text-left font-medium">Type</th>
                                <th className="px-4 py-2 text-left font-medium">Nullable</th>
                                <th className="px-4 py-2 text-left font-medium">Key</th>
                              </tr>
                            </thead>
                            <tbody>
                              {table.columns?.map((col, colIndex) => (
                                <tr key={colIndex} className="border-t">
                                  <td className="px-4 py-2 font-mono">{col.name}</td>
                                  <td className="px-4 py-2">
                                    <Badge variant="outline" className="font-mono text-xs">
                                      {col.data_type}
                                    </Badge>
                                  </td>
                                  <td className="px-4 py-2">
                                    {col.nullable ? (
                                      <span className="text-muted-foreground">Yes</span>
                                    ) : (
                                      <span className="text-orange-500">No</span>
                                    )}
                                  </td>
                                  <td className="px-4 py-2">
                                    {col.primary_key && (
                                      <Badge variant="default" className="text-xs">PK</Badge>
                                    )}
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </AccordionContent>
                    </AccordionItem>
                  ))}
                </Accordion>
              ) : (
                <div className="text-center py-12 text-muted-foreground">
                  <Table2 className="size-12 mx-auto mb-4 opacity-50" />
                  <p>No schema discovered yet</p>
                  <p className="text-sm mt-1">Test the connection first, then click &quot;Refresh Schema&quot;</p>
                </div>
              )}

              {schema?.discovered_at && (
                <p className="text-xs text-muted-foreground mt-4">
                  Last discovered: {new Date(schema.discovered_at).toLocaleString()}
                </p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Usage Tab */}
        <TabsContent value="usage">
          <Card>
            <CardHeader>
              <CardTitle>Usage & Access</CardTitle>
              <CardDescription>
                Projects and components using this data source
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12 text-muted-foreground">
                <FolderClosed className="size-12 mx-auto mb-4 opacity-50" />
                <p>No usage information available yet</p>
                <p className="text-sm mt-1">Link this data source to projects to see usage</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}



