"use client";

import * as React from "react";
import {
  Brain,
  Search,
  Plus,
  Trash2,
  RefreshCw,
  Loader2,
  Database,
  Tag,
  Layers,
  MessageSquare,
  BarChart3,
  Eye,
  AlertTriangle,
} from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { apiFetch } from "@/lib/api";
import { toast } from "sonner";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface MemoryStats {
  total: number;
  by_type: Record<string, number>;
  by_scope: Record<string, number>;
}

interface MemoryEntry {
  id: string;
  content: string;
  type: string;
  scope?: string;
  metadata?: Record<string, unknown>;
  created_at?: string;
  score?: number;
}

interface ContextResult {
  context: string;
  sources?: string[];
}

// ---------------------------------------------------------------------------
// Main Page
// ---------------------------------------------------------------------------

export default function MemoryPage() {
  // Stats
  const [stats, setStats] = React.useState<MemoryStats | null>(null);
  const [statsLoading, setStatsLoading] = React.useState(true);

  // Search
  const [searchQuery, setSearchQuery] = React.useState("");
  const [searchResults, setSearchResults] = React.useState<MemoryEntry[]>([]);
  const [searching, setSearching] = React.useState(false);
  const [hasSearched, setHasSearched] = React.useState(false);

  // Browse
  const [memories, setMemories] = React.useState<MemoryEntry[]>([]);
  const [memoriesLoading, setMemoriesLoading] = React.useState(true);
  const [deletingId, setDeletingId] = React.useState<string | null>(null);

  // Add
  const [addContent, setAddContent] = React.useState("");
  const [addType, setAddType] = React.useState("fact");
  const [addScope, setAddScope] = React.useState("global");
  const [addMetadata, setAddMetadata] = React.useState("");
  const [adding, setAdding] = React.useState(false);

  // Context
  const [contextQuery, setContextQuery] = React.useState("");
  const [contextResult, setContextResult] = React.useState<ContextResult | null>(null);
  const [fetchingContext, setFetchingContext] = React.useState(false);

  // -------------------------------------------------------------------------
  // Data fetching
  // -------------------------------------------------------------------------

  const loadStats = React.useCallback(async () => {
    try {
      const data = await apiFetch<MemoryStats>("/api/v1/memory/stats");
      setStats(data);
    } catch {
      /* stats unavailable */
    } finally {
      setStatsLoading(false);
    }
  }, []);

  const loadMemories = React.useCallback(async () => {
    setMemoriesLoading(true);
    try {
      const data = await apiFetch<{ context: string }>("/api/v1/memory/context");
      // The browse endpoint may return memories via context or a list — adapt to response shape
      const searchAll = await apiFetch<{ results: MemoryEntry[] }>("/api/v1/memory/search", {
        method: "POST",
        body: JSON.stringify({ query: "", limit: 50 }),
      });
      setMemories(searchAll.results ?? []);
    } catch {
      toast.error("Failed to load memories");
    } finally {
      setMemoriesLoading(false);
    }
  }, []);

  React.useEffect(() => {
    loadStats();
    loadMemories();
  }, [loadStats, loadMemories]);

  // -------------------------------------------------------------------------
  // Actions
  // -------------------------------------------------------------------------

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setSearching(true);
    setHasSearched(true);
    try {
      const data = await apiFetch<{ results: MemoryEntry[] }>("/api/v1/memory/search", {
        method: "POST",
        body: JSON.stringify({ query: searchQuery }),
      });
      setSearchResults(data.results ?? []);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Search failed");
    } finally {
      setSearching(false);
    }
  };

  const handleAdd = async () => {
    if (!addContent.trim()) return;
    setAdding(true);
    try {
      let metadata: Record<string, unknown> | undefined;
      if (addMetadata.trim()) {
        try {
          metadata = JSON.parse(addMetadata);
        } catch {
          toast.error("Metadata must be valid JSON");
          setAdding(false);
          return;
        }
      }
      await apiFetch("/api/v1/memory/add", {
        method: "POST",
        body: JSON.stringify({
          content: addContent,
          type: addType,
          scope: addScope,
          metadata,
        }),
      });
      toast.success("Memory added");
      setAddContent("");
      setAddMetadata("");
      loadStats();
      loadMemories();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to add memory");
    } finally {
      setAdding(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this memory?")) return;
    setDeletingId(id);
    try {
      await apiFetch(`/api/v1/memory/${id}`, { method: "DELETE" });
      toast.success("Memory deleted");
      loadStats();
      loadMemories();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Delete failed");
    } finally {
      setDeletingId(null);
    }
  };

  const handleClearAll = async () => {
    if (!confirm("Clear ALL memories? This cannot be undone.")) return;
    try {
      await apiFetch("/api/v1/memory/clear", { method: "POST" });
      toast.success("All memories cleared");
      loadStats();
      loadMemories();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Clear failed");
    }
  };

  const handleFetchContext = async () => {
    if (!contextQuery.trim()) return;
    setFetchingContext(true);
    try {
      const data = await apiFetch<ContextResult>("/api/v1/memory/context", {
        params: { query: contextQuery },
      });
      setContextResult(data);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to fetch context");
    } finally {
      setFetchingContext(false);
    }
  };

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Memory Store</h1>
          <p className="text-muted-foreground">
            Semantic memory storage, search, and context retrieval
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            className="text-destructive hover:text-destructive"
            onClick={handleClearAll}
          >
            <AlertTriangle className="size-4 mr-2" />
            Clear All
          </Button>
          <Button variant="outline" onClick={() => { setStatsLoading(true); setMemoriesLoading(true); loadStats(); loadMemories(); }}>
            <RefreshCw className="size-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Stats */}
      {statsLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => <Skeleton key={i} className="h-20 w-full rounded-lg" />)}
        </div>
      ) : stats ? (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Card>
            <CardContent className="p-4 flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                <Database className="size-5 text-primary" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.total}</p>
                <p className="text-xs text-muted-foreground">Total Memories</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                <Tag className="size-5 text-blue-500" />
              </div>
              <div>
                <div className="flex items-center gap-1.5 flex-wrap">
                  {Object.entries(stats.by_type).map(([type, count]) => (
                    <Badge key={type} variant="secondary" className="text-[10px]">
                      {type}: {count}
                    </Badge>
                  ))}
                  {Object.keys(stats.by_type).length === 0 && (
                    <span className="text-sm text-muted-foreground">—</span>
                  )}
                </div>
                <p className="text-xs text-muted-foreground mt-1">By Type</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-amber-500/10 flex items-center justify-center">
                <Layers className="size-5 text-amber-500" />
              </div>
              <div>
                <div className="flex items-center gap-1.5 flex-wrap">
                  {Object.entries(stats.by_scope).map(([scope, count]) => (
                    <Badge key={scope} variant="secondary" className="text-[10px]">
                      {scope}: {count}
                    </Badge>
                  ))}
                  {Object.keys(stats.by_scope).length === 0 && (
                    <span className="text-sm text-muted-foreground">—</span>
                  )}
                </div>
                <p className="text-xs text-muted-foreground mt-1">By Scope</p>
              </div>
            </CardContent>
          </Card>
        </div>
      ) : null}

      <Tabs defaultValue="search" className="space-y-4">
        <TabsList>
          <TabsTrigger value="search">
            <Search className="size-3.5 mr-1.5" />
            Search
          </TabsTrigger>
          <TabsTrigger value="browse">
            <Database className="size-3.5 mr-1.5" />
            Browse
          </TabsTrigger>
          <TabsTrigger value="add">
            <Plus className="size-3.5 mr-1.5" />
            Add
          </TabsTrigger>
          <TabsTrigger value="context">
            <Eye className="size-3.5 mr-1.5" />
            Context
          </TabsTrigger>
        </TabsList>

        {/* ================================================================ */}
        {/* Search Tab */}
        {/* ================================================================ */}
        <TabsContent value="search" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Search className="size-4" />
                Semantic Search
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-3">
                <Input
                  placeholder="Search memories semantically…"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                  className="flex-1"
                />
                <Button onClick={handleSearch} disabled={searching || !searchQuery.trim()}>
                  {searching ? (
                    <Loader2 className="size-4 mr-2 animate-spin" />
                  ) : (
                    <Search className="size-4 mr-2" />
                  )}
                  Search
                </Button>
              </div>

              {searching ? (
                <div className="space-y-3">
                  {[1, 2, 3].map((i) => <Skeleton key={i} className="h-16 w-full rounded-lg" />)}
                </div>
              ) : hasSearched && searchResults.length === 0 ? (
                <div className="py-8 text-center">
                  <Search className="size-10 mx-auto mb-3 opacity-50" />
                  <p className="text-muted-foreground text-sm">No matching memories found</p>
                </div>
              ) : (
                searchResults.map((entry) => (
                  <Card key={entry.id} className="bg-muted/30">
                    <CardContent className="p-4 space-y-2">
                      <div className="flex items-start justify-between gap-3">
                        <p className="text-sm flex-1">{entry.content}</p>
                        {entry.score != null && (
                          <Badge variant="outline" className="shrink-0 text-[10px]">
                            {(entry.score * 100).toFixed(0)}%
                          </Badge>
                        )}
                      </div>
                      <div className="flex items-center gap-2 flex-wrap">
                        <Badge variant="secondary" className="text-[10px]">{entry.type}</Badge>
                        {entry.scope && (
                          <Badge variant="outline" className="text-[10px]">{entry.scope}</Badge>
                        )}
                        <span className="text-[10px] text-muted-foreground font-mono">
                          {entry.id.slice(0, 10)}…
                        </span>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* ================================================================ */}
        {/* Browse Tab */}
        {/* ================================================================ */}
        <TabsContent value="browse" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Database className="size-4" />
                Memory Browser
              </CardTitle>
            </CardHeader>
            <CardContent>
              {memoriesLoading ? (
                <div className="space-y-3">
                  {[1, 2, 3, 4].map((i) => <Skeleton key={i} className="h-14 w-full rounded-lg" />)}
                </div>
              ) : memories.length === 0 ? (
                <div className="py-12 text-center">
                  <Brain className="size-12 mx-auto mb-4 opacity-50" />
                  <h3 className="text-lg font-semibold mb-2">No memories stored</h3>
                  <p className="text-muted-foreground">
                    Add memories using the Add tab
                  </p>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Content</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead>Scope</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {memories.map((mem) => (
                      <TableRow key={mem.id}>
                        <TableCell className="max-w-md">
                          <p className="text-sm truncate">{mem.content}</p>
                          <span className="text-[10px] text-muted-foreground font-mono">
                            {mem.id.slice(0, 10)}…
                          </span>
                        </TableCell>
                        <TableCell>
                          <Badge variant="secondary">{mem.type}</Badge>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">{mem.scope ?? "—"}</Badge>
                        </TableCell>
                        <TableCell className="text-right">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-7 text-xs gap-1 text-destructive hover:text-destructive"
                            onClick={() => handleDelete(mem.id)}
                            disabled={deletingId === mem.id}
                          >
                            {deletingId === mem.id ? (
                              <Loader2 className="size-3 animate-spin" />
                            ) : (
                              <Trash2 className="size-3" />
                            )}
                            Delete
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* ================================================================ */}
        {/* Add Tab */}
        {/* ================================================================ */}
        <TabsContent value="add" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Plus className="size-4" />
                Add Memory
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-medium">Content</label>
                <Textarea
                  placeholder="Enter memory content…"
                  value={addContent}
                  onChange={(e) => setAddContent(e.target.value)}
                  rows={4}
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-medium">Type</label>
                  <Select value={addType} onValueChange={setAddType}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="fact">Fact</SelectItem>
                      <SelectItem value="preference">Preference</SelectItem>
                      <SelectItem value="instruction">Instruction</SelectItem>
                      <SelectItem value="conversation">Conversation</SelectItem>
                      <SelectItem value="knowledge">Knowledge</SelectItem>
                      <SelectItem value="custom">Custom</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-medium">Scope</label>
                  <Select value={addScope} onValueChange={setAddScope}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="global">Global</SelectItem>
                      <SelectItem value="project">Project</SelectItem>
                      <SelectItem value="session">Session</SelectItem>
                      <SelectItem value="user">User</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-medium">Metadata (JSON, optional)</label>
                <Textarea
                  placeholder='{"key": "value"}'
                  value={addMetadata}
                  onChange={(e) => setAddMetadata(e.target.value)}
                  rows={2}
                  className="font-mono text-xs"
                />
              </div>

              <Button onClick={handleAdd} disabled={adding || !addContent.trim()}>
                {adding ? (
                  <Loader2 className="size-4 mr-2 animate-spin" />
                ) : (
                  <Plus className="size-4 mr-2" />
                )}
                Add Memory
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ================================================================ */}
        {/* Context Tab */}
        {/* ================================================================ */}
        <TabsContent value="context" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <MessageSquare className="size-4" />
                Context Viewer
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Enter a query to retrieve the assembled context string the agent would receive.
              </p>
              <div className="flex gap-3">
                <Input
                  placeholder="What context would the agent see for…"
                  value={contextQuery}
                  onChange={(e) => setContextQuery(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleFetchContext()}
                  className="flex-1"
                />
                <Button onClick={handleFetchContext} disabled={fetchingContext || !contextQuery.trim()}>
                  {fetchingContext ? (
                    <Loader2 className="size-4 mr-2 animate-spin" />
                  ) : (
                    <Eye className="size-4 mr-2" />
                  )}
                  Fetch
                </Button>
              </div>

              {fetchingContext ? (
                <Skeleton className="h-40 w-full rounded-lg" />
              ) : contextResult ? (
                <div className="space-y-3">
                  <div>
                    <p className="text-xs font-medium mb-1.5">Context</p>
                    <pre className="p-4 bg-muted rounded-md border text-xs font-mono whitespace-pre-wrap max-h-80 overflow-y-auto">
                      {contextResult.context || "No context returned"}
                    </pre>
                  </div>
                  {contextResult.sources && contextResult.sources.length > 0 && (
                    <div>
                      <p className="text-xs font-medium mb-1.5">Sources</p>
                      <div className="flex gap-1.5 flex-wrap">
                        {contextResult.sources.map((src, i) => (
                          <Badge key={i} variant="outline" className="text-[10px]">
                            {src}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="py-8 text-center">
                  <BarChart3 className="size-10 mx-auto mb-3 opacity-50" />
                  <p className="text-muted-foreground text-sm">
                    Enter a query and click Fetch to preview context
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
