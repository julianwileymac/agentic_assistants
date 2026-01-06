"use client";

import * as React from "react";
import Link from "next/link";
import { Plus, Search, GitBranch, MoreHorizontal, Play, Pencil, Trash2, FileUp, FileDown, CheckCircle, XCircle } from "lucide-react";

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
import { useFlows } from "@/lib/api";
import type { Flow } from "@/lib/types";
import { toast } from "sonner";

const statusColors: Record<string, string> = {
  active: "bg-green-500/10 text-green-500 border-green-500/20",
  paused: "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
  draft: "bg-gray-500/10 text-gray-500 border-gray-500/20",
  archived: "bg-red-500/10 text-red-500 border-red-500/20",
};

const typeColors: Record<string, string> = {
  crew: "bg-violet-500/10 text-violet-500",
  pipeline: "bg-blue-500/10 text-blue-500",
  workflow: "bg-emerald-500/10 text-emerald-500",
};

function FlowCard({ flow, onDelete }: { flow: Flow; onDelete: () => void }) {
  return (
    <Card className="group hover:shadow-lg transition-all duration-300">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-500 text-white">
              <GitBranch className="size-5" />
            </div>
            <div>
              <CardTitle className="text-lg">
                <Link href={`/flows/${flow.id}`} className="hover:underline">
                  {flow.name}
                </Link>
              </CardTitle>
              <CardDescription className="line-clamp-1">
                {flow.description || "No description"}
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
                <Link href={`/flows/${flow.id}`}>
                  <Pencil className="size-4 mr-2" />
                  Edit
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem>
                <Play className="size-4 mr-2" />
                Run
              </DropdownMenuItem>
              <DropdownMenuItem>
                <FileDown className="size-4 mr-2" />
                Export YAML
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="text-destructive" onClick={onDelete}>
                <Trash2 className="size-4 mr-2" />
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Badge variant="outline" className={statusColors[flow.status]}>
                {flow.status}
              </Badge>
              <Badge variant="secondary" className={typeColors[flow.flow_type]}>
                {flow.flow_type}
              </Badge>
            </div>
          </div>
          
          {flow.agents.length > 0 && (
            <div className="text-sm text-muted-foreground">
              {flow.agents.length} agent{flow.agents.length !== 1 ? "s" : ""}
            </div>
          )}

          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>Updated {new Date(flow.updated_at).toLocaleDateString()}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default function FlowsPage() {
  const [statusFilter, setStatusFilter] = React.useState<string>("all");
  const [searchQuery, setSearchQuery] = React.useState("");
  
  const { data, isLoading, mutate } = useFlows({
    status: statusFilter === "all" ? undefined : statusFilter,
  });

  const handleDelete = async (flowId: string, flowName: string) => {
    if (!confirm(`Are you sure you want to delete "${flowName}"?`)) {
      return;
    }
    
    try {
      const response = await fetch(`http://localhost:8080/api/v1/flows/${flowId}`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        toast.success(`Flow "${flowName}" deleted`);
        mutate();
      } else {
        toast.error("Failed to delete flow");
      }
    } catch (error) {
      toast.error("Failed to delete flow");
    }
  };

  const handleImportYAML = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.yaml,.yml';
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (!file) return;
      
      const text = await file.text();
      // Navigate to new flow page with YAML content
      // You could use localStorage or a state management solution
      localStorage.setItem('importedFlowYAML', text);
      window.location.href = '/flows/new?import=true';
    };
    input.click();
  };

  const filteredFlows = React.useMemo(() => {
    if (!data?.items) return [];
    if (!searchQuery) return data.items;
    
    const query = searchQuery.toLowerCase();
    return data.items.filter(
      (f) =>
        f.name.toLowerCase().includes(query) ||
        f.description.toLowerCase().includes(query)
    );
  }, [data?.items, searchQuery]);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Flows</h1>
          <p className="text-muted-foreground">
            Multi-agent workflows and data pipelines
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={handleImportYAML}>
            <FileUp className="size-4 mr-2" />
            Import YAML
          </Button>
          <Button asChild>
            <Link href="/flows/new">
              <Plus className="size-4 mr-2" />
              New Flow
            </Link>
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Tabs defaultValue="all" value={statusFilter} onValueChange={setStatusFilter}>
        <div className="flex items-center justify-between">
          <TabsList>
            <TabsTrigger value="all">All</TabsTrigger>
            <TabsTrigger value="active">Active</TabsTrigger>
            <TabsTrigger value="draft">Draft</TabsTrigger>
            <TabsTrigger value="paused">Paused</TabsTrigger>
            <TabsTrigger value="archived">Archived</TabsTrigger>
          </TabsList>
          
          <div className="relative w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
            <Input
              placeholder="Search flows..."
              className="pl-9"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>

        {/* Flows Grid */}
        <TabsContent value={statusFilter} className="mt-6">
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
          ) : filteredFlows.length === 0 ? (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center py-12">
                  <GitBranch className="size-12 mx-auto mb-4 opacity-50" />
                  <h3 className="text-lg font-semibold mb-2">No flows found</h3>
                  <p className="text-muted-foreground mb-4">
                    {searchQuery
                      ? "Try a different search term"
                      : "Create your first flow to get started"}
                  </p>
                  {!searchQuery && (
                    <div className="flex items-center justify-center gap-2">
                      <Button variant="outline" onClick={handleImportYAML}>
                        <FileUp className="size-4 mr-2" />
                        Import YAML
                      </Button>
                      <Button asChild>
                        <Link href="/flows/new">
                          <Plus className="size-4 mr-2" />
                          Create Flow
                        </Link>
                      </Button>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredFlows.map((flow) => (
                <FlowCard
                  key={flow.id}
                  flow={flow}
                  onDelete={() => handleDelete(flow.id, flow.name)}
                />
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}

