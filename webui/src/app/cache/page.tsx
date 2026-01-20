"use client";

import * as React from "react";
import {
  Database,
  Code,
  Workflow,
  Tag,
  Search,
  Plus,
  MoreHorizontal,
  Trash2,
  Eye,
  Copy,
  Play,
  CheckCircle,
  XCircle,
  Clock,
  RefreshCw,
  Loader2,
  Activity,
  Archive,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
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
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { toast } from "sonner";

interface Solution {
  id: string;
  name: string;
  description: string;
  solution_type: string;
  content: any;
  code: string;
  tags: string[];
  metadata: Record<string, any>;
  use_count: number;
  success_rate: number;
  created_at: string;
  updated_at: string;
  project_id?: string;
  is_global: boolean;
}

interface WorkflowState {
  workflow_id: string;
  name: string;
  status: string;
  current_step: number;
  steps: any[];
  results: Record<string, any>;
  context: Record<string, any>;
  error?: string;
  created_at: string;
  updated_at: string;
}

interface CacheStats {
  total_solutions: number;
  total_tags: number;
  active_workflows: number;
  by_type: Record<string, number>;
  cache_info: Record<string, any>;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const SOLUTION_TYPES = [
  { value: "code", label: "Code", icon: Code },
  { value: "workflow", label: "Workflow", icon: Workflow },
  { value: "pattern", label: "Pattern", icon: Archive },
  { value: "prompt", label: "Prompt", icon: Activity },
];

export default function CachePage() {
  const [activeTab, setActiveTab] = React.useState("solutions");
  const [solutions, setSolutions] = React.useState<Solution[]>([]);
  const [workflows, setWorkflows] = React.useState<WorkflowState[]>([]);
  const [stats, setStats] = React.useState<CacheStats | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [searchQuery, setSearchQuery] = React.useState("");
  const [selectedType, setSelectedType] = React.useState("all");
  const [allTags, setAllTags] = React.useState<string[]>([]);

  // Dialog states
  const [createDialogOpen, setCreateDialogOpen] = React.useState(false);
  const [viewDialogOpen, setViewDialogOpen] = React.useState(false);
  const [selectedSolution, setSelectedSolution] = React.useState<Solution | null>(null);

  // New solution form
  const [newSolution, setNewSolution] = React.useState({
    name: "",
    description: "",
    solution_type: "code",
    code: "",
    tags: [] as string[],
  });
  const [tagInput, setTagInput] = React.useState("");

  const fetchData = async () => {
    setLoading(true);
    try {
      // Fetch solutions
      const solutionsRes = await fetch(`${API_URL}/api/cache/solutions`);
      if (solutionsRes.ok) {
        setSolutions(await solutionsRes.json());
      }

      // Fetch workflows
      const workflowsRes = await fetch(`${API_URL}/api/cache/workflows`);
      if (workflowsRes.ok) {
        setWorkflows(await workflowsRes.json());
      }

      // Fetch stats
      const statsRes = await fetch(`${API_URL}/api/cache/stats`);
      if (statsRes.ok) {
        setStats(await statsRes.json());
      }

      // Fetch tags
      const tagsRes = await fetch(`${API_URL}/api/cache/tags`);
      if (tagsRes.ok) {
        const tagsData = await tagsRes.json();
        setAllTags(tagsData.tags || []);
      }
    } catch (error) {
      console.error("Error fetching cache data:", error);
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    fetchData();
  }, []);

  const handleCreateSolution = async () => {
    try {
      const response = await fetch(`${API_URL}/api/cache/solutions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newSolution),
      });

      if (response.ok) {
        toast.success("Solution created successfully");
        setCreateDialogOpen(false);
        setNewSolution({
          name: "",
          description: "",
          solution_type: "code",
          code: "",
          tags: [],
        });
        fetchData();
      } else {
        toast.error("Failed to create solution");
      }
    } catch (error) {
      toast.error(`Error: ${error}`);
    }
  };

  const handleDeleteSolution = async (name: string) => {
    try {
      const response = await fetch(`${API_URL}/api/cache/solutions/${name}`, {
        method: "DELETE",
      });

      if (response.ok) {
        toast.success("Solution deleted");
        fetchData();
      } else {
        toast.error("Failed to delete solution");
      }
    } catch (error) {
      toast.error(`Error: ${error}`);
    }
  };

  const handleCopySolution = (solution: Solution) => {
    navigator.clipboard.writeText(solution.code || JSON.stringify(solution.content, null, 2));
    toast.success("Copied to clipboard");
  };

  const addTag = () => {
    if (tagInput && !newSolution.tags.includes(tagInput.toLowerCase())) {
      setNewSolution({
        ...newSolution,
        tags: [...newSolution.tags, tagInput.toLowerCase()],
      });
      setTagInput("");
    }
  };

  const removeTag = (tag: string) => {
    setNewSolution({
      ...newSolution,
      tags: newSolution.tags.filter((t) => t !== tag),
    });
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString();
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "failed":
        return <XCircle className="h-4 w-4 text-red-500" />;
      case "running":
        return <Loader2 className="h-4 w-4 animate-spin text-blue-500" />;
      default:
        return <Clock className="h-4 w-4 text-yellow-500" />;
    }
  };

  const getSolutionTypeIcon = (type: string) => {
    const found = SOLUTION_TYPES.find((t) => t.value === type);
    if (found) {
      const Icon = found.icon;
      return <Icon className="h-4 w-4" />;
    }
    return <Code className="h-4 w-4" />;
  };

  const filteredSolutions = solutions.filter((sol) => {
    if (selectedType !== "all" && sol.solution_type !== selectedType) return false;
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      sol.name.toLowerCase().includes(query) ||
      sol.description.toLowerCase().includes(query) ||
      sol.tags.some((t) => t.toLowerCase().includes(query))
    );
  });

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Solution Cache</h1>
          <p className="text-muted-foreground">
            Manage cached solutions, workflows, and reusable patterns
          </p>
        </div>
        <Button onClick={() => setCreateDialogOpen(true)}>
          <Plus className="h-4 w-4 mr-2" />
          New Solution
        </Button>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Total Solutions
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_solutions}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Active Workflows
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.active_workflows}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Tags in Use
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_tags}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Code Snippets
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {stats.by_type?.code || 0}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="solutions">Solutions</TabsTrigger>
          <TabsTrigger value="workflows">Workflows</TabsTrigger>
          <TabsTrigger value="tags">Tags</TabsTrigger>
        </TabsList>

        <TabsContent value="solutions" className="space-y-4">
          {/* Filters */}
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    placeholder="Search solutions..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
                <Select value={selectedType} onValueChange={setSelectedType}>
                  <SelectTrigger className="w-[150px]">
                    <SelectValue placeholder="Type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Types</SelectItem>
                    {SOLUTION_TYPES.map((type) => (
                      <SelectItem key={type.value} value={type.value}>
                        {type.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Button variant="outline" onClick={fetchData}>
                  <RefreshCw className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Solutions Table */}
          <Card>
            <CardHeader>
              <CardTitle>Cached Solutions</CardTitle>
              <CardDescription>
                {filteredSolutions.length} solutions found
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Tags</TableHead>
                    <TableHead>Uses</TableHead>
                    <TableHead>Success Rate</TableHead>
                    <TableHead>Updated</TableHead>
                    <TableHead className="w-[50px]"></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredSolutions.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center py-8">
                        <div className="text-muted-foreground">
                          {loading ? "Loading..." : "No solutions found"}
                        </div>
                      </TableCell>
                    </TableRow>
                  ) : (
                    filteredSolutions.map((sol) => (
                      <TableRow key={sol.id}>
                        <TableCell>
                          <div>
                            <div className="font-medium">{sol.name}</div>
                            <div className="text-xs text-muted-foreground truncate max-w-[200px]">
                              {sol.description}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            {getSolutionTypeIcon(sol.solution_type)}
                            <span className="capitalize">{sol.solution_type}</span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex flex-wrap gap-1">
                            {sol.tags.slice(0, 2).map((tag) => (
                              <Badge key={tag} variant="secondary" className="text-xs">
                                {tag}
                              </Badge>
                            ))}
                            {sol.tags.length > 2 && (
                              <Badge variant="secondary" className="text-xs">
                                +{sol.tags.length - 2}
                              </Badge>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>{sol.use_count}</TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <div
                              className={`h-2 w-2 rounded-full ${
                                sol.success_rate >= 0.8
                                  ? "bg-green-500"
                                  : sol.success_rate >= 0.5
                                  ? "bg-yellow-500"
                                  : "bg-red-500"
                              }`}
                            />
                            {(sol.success_rate * 100).toFixed(0)}%
                          </div>
                        </TableCell>
                        <TableCell className="text-muted-foreground text-sm">
                          {formatDate(sol.updated_at)}
                        </TableCell>
                        <TableCell>
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" size="icon">
                                <MoreHorizontal className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuItem
                                onClick={() => {
                                  setSelectedSolution(sol);
                                  setViewDialogOpen(true);
                                }}
                              >
                                <Eye className="h-4 w-4 mr-2" />
                                View
                              </DropdownMenuItem>
                              <DropdownMenuItem onClick={() => handleCopySolution(sol)}>
                                <Copy className="h-4 w-4 mr-2" />
                                Copy
                              </DropdownMenuItem>
                              <DropdownMenuItem
                                className="text-red-600"
                                onClick={() => handleDeleteSolution(sol.name)}
                              >
                                <Trash2 className="h-4 w-4 mr-2" />
                                Delete
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="workflows" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Active Workflows</CardTitle>
              <CardDescription>
                {workflows.length} workflows in progress
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Workflow</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Progress</TableHead>
                    <TableHead>Started</TableHead>
                    <TableHead>Last Update</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {workflows.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center py-8">
                        <div className="text-muted-foreground">
                          No active workflows
                        </div>
                      </TableCell>
                    </TableRow>
                  ) : (
                    workflows.map((wf) => (
                      <TableRow key={wf.workflow_id}>
                        <TableCell>
                          <div className="font-medium">{wf.name}</div>
                          <div className="text-xs text-muted-foreground">
                            {wf.workflow_id}
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            {getStatusIcon(wf.status)}
                            <span className="capitalize">{wf.status}</span>
                          </div>
                        </TableCell>
                        <TableCell>
                          {wf.current_step + 1} / {wf.steps.length} steps
                        </TableCell>
                        <TableCell className="text-muted-foreground text-sm">
                          {formatDate(wf.created_at)}
                        </TableCell>
                        <TableCell className="text-muted-foreground text-sm">
                          {formatDate(wf.updated_at)}
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="tags" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Tags</CardTitle>
              <CardDescription>
                All tags used in the solution cache
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {allTags.length === 0 ? (
                  <div className="text-muted-foreground">No tags found</div>
                ) : (
                  allTags.map((tag) => (
                    <Badge key={tag} variant="secondary" className="text-sm">
                      <Tag className="h-3 w-3 mr-1" />
                      {tag}
                    </Badge>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Create Solution Dialog */}
      <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
        <DialogContent className="max-w-xl">
          <DialogHeader>
            <DialogTitle>Create New Solution</DialogTitle>
            <DialogDescription>
              Add a reusable solution to the cache
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Name</Label>
              <Input
                placeholder="Solution name"
                value={newSolution.name}
                onChange={(e) =>
                  setNewSolution({ ...newSolution, name: e.target.value })
                }
              />
            </div>
            <div className="space-y-2">
              <Label>Description</Label>
              <Input
                placeholder="Brief description"
                value={newSolution.description}
                onChange={(e) =>
                  setNewSolution({ ...newSolution, description: e.target.value })
                }
              />
            </div>
            <div className="space-y-2">
              <Label>Type</Label>
              <Select
                value={newSolution.solution_type}
                onValueChange={(v) =>
                  setNewSolution({ ...newSolution, solution_type: v })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {SOLUTION_TYPES.map((type) => (
                    <SelectItem key={type.value} value={type.value}>
                      {type.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Code/Content</Label>
              <Textarea
                placeholder="Enter code or content..."
                rows={6}
                value={newSolution.code}
                onChange={(e) =>
                  setNewSolution({ ...newSolution, code: e.target.value })
                }
                className="font-mono text-sm"
              />
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
                <Button variant="outline" onClick={addTag}>
                  Add
                </Button>
              </div>
              {newSolution.tags.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {newSolution.tags.map((tag) => (
                    <Badge key={tag} variant="secondary">
                      {tag}
                      <button
                        onClick={() => removeTag(tag)}
                        className="ml-1 hover:text-red-500"
                      >
                        ×
                      </button>
                    </Badge>
                  ))}
                </div>
              )}
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCreateDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreateSolution}>Create</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* View Solution Dialog */}
      <Dialog open={viewDialogOpen} onOpenChange={setViewDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{selectedSolution?.name}</DialogTitle>
            <DialogDescription>{selectedSolution?.description}</DialogDescription>
          </DialogHeader>
          {selectedSolution && (
            <div className="space-y-4">
              <div className="flex gap-2">
                <Badge>{selectedSolution.solution_type}</Badge>
                {selectedSolution.tags.map((tag) => (
                  <Badge key={tag} variant="secondary">
                    {tag}
                  </Badge>
                ))}
              </div>
              <ScrollArea className="h-[300px]">
                <pre className="p-4 bg-muted rounded-lg font-mono text-sm whitespace-pre-wrap">
                  {selectedSolution.code ||
                    JSON.stringify(selectedSolution.content, null, 2)}
                </pre>
              </ScrollArea>
              <div className="flex justify-between text-sm text-muted-foreground">
                <span>Uses: {selectedSolution.use_count}</span>
                <span>
                  Success Rate: {(selectedSolution.success_rate * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => selectedSolution && handleCopySolution(selectedSolution)}
            >
              <Copy className="h-4 w-4 mr-2" />
              Copy
            </Button>
            <Button onClick={() => setViewDialogOpen(false)}>Close</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
