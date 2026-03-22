"use client";

import * as React from "react";
import Link from "next/link";
import { Plus, Search, Filter, Bot, MoreHorizontal, Play, Pencil, Trash2, Rocket } from "lucide-react";

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
import { useAgents } from "@/lib/api";
import type { Agent } from "@/lib/types";
import { toast } from "sonner";
import { TestingSection } from "@/components/testing/testing-section";

const statusColors: Record<string, string> = {
  deployed: "bg-green-500/10 text-green-500 border-green-500/20",
  created: "bg-blue-500/10 text-blue-500 border-blue-500/20",
  drafted: "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
  in_development: "bg-purple-500/10 text-purple-500 border-purple-500/20",
};

const statusLabels: Record<string, string> = {
  deployed: "Deployed",
  created: "Created",
  drafted: "Draft",
  in_development: "In Development",
};

function AgentCard({ agent, onDelete, onDeploy }: { 
  agent: Agent; 
  onDelete: () => void;
  onDeploy: () => void;
}) {
  return (
    <Card className="group hover:shadow-lg transition-all duration-300">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-gradient-to-br from-violet-500 to-purple-500 text-white">
              <Bot className="size-5" />
            </div>
            <div>
              <CardTitle className="text-lg">
                <Link href={`/agents/${agent.id}`} className="hover:underline">
                  {agent.name}
                </Link>
              </CardTitle>
              <CardDescription className="line-clamp-1">
                {agent.role}
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
                <Link href={`/agents/${agent.id}`}>
                  <Pencil className="size-4 mr-2" />
                  Edit
                </Link>
              </DropdownMenuItem>
              {agent.status !== "deployed" && (
                <DropdownMenuItem onClick={onDeploy}>
                  <Rocket className="size-4 mr-2" />
                  Deploy
                </DropdownMenuItem>
              )}
              <DropdownMenuItem>
                <Play className="size-4 mr-2" />
                Run
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
            <Badge variant="outline" className={statusColors[agent.status]}>
              {statusLabels[agent.status]}
            </Badge>
            <span className="text-xs text-muted-foreground">
              {agent.model}
            </span>
          </div>
          
          {agent.goal && (
            <p className="text-sm text-muted-foreground line-clamp-2">
              {agent.goal}
            </p>
          )}

          {agent.tools.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {agent.tools.slice(0, 3).map((tool) => (
                <Badge key={tool} variant="secondary" className="text-xs">
                  {tool}
                </Badge>
              ))}
              {agent.tools.length > 3 && (
                <Badge variant="secondary" className="text-xs">
                  +{agent.tools.length - 3}
                </Badge>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export default function AgentsPage() {
  const [statusFilter, setStatusFilter] = React.useState<string>("all");
  const [searchQuery, setSearchQuery] = React.useState("");
  
  const { data, isLoading, mutate } = useAgents({
    status: statusFilter === "all" ? undefined : statusFilter,
  });

  const handleDelete = async (agentId: string, agentName: string) => {
    if (!confirm(`Are you sure you want to delete "${agentName}"?`)) {
      return;
    }
    
    try {
      const response = await fetch(`http://localhost:8080/api/v1/agents/${agentId}`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        toast.success(`Agent "${agentName}" deleted`);
        mutate();
      } else {
        toast.error("Failed to delete agent");
      }
    } catch (error) {
      toast.error("Failed to delete agent");
    }
  };

  const handleDeploy = async (agentId: string, agentName: string) => {
    try {
      const response = await fetch(`http://localhost:8080/api/v1/agents/${agentId}/deploy`, {
        method: 'POST',
      });
      
      if (response.ok) {
        toast.success(`Agent "${agentName}" deployed`);
        mutate();
      } else {
        toast.error("Failed to deploy agent");
      }
    } catch (error) {
      toast.error("Failed to deploy agent");
    }
  };

  const filteredAgents = React.useMemo(() => {
    if (!data?.items) return [];
    if (!searchQuery) return data.items;
    
    const query = searchQuery.toLowerCase();
    return data.items.filter(
      (a) =>
        a.name.toLowerCase().includes(query) ||
        a.role.toLowerCase().includes(query) ||
        a.goal.toLowerCase().includes(query)
    );
  }, [data?.items, searchQuery]);

  // Group agents by status for the overview
  const agentsByStatus = React.useMemo(() => {
    if (!data?.items) return { deployed: 0, created: 0, drafted: 0, in_development: 0 };
    return {
      deployed: data.items.filter((a) => a.status === "deployed").length,
      created: data.items.filter((a) => a.status === "created").length,
      drafted: data.items.filter((a) => a.status === "drafted").length,
      in_development: data.items.filter((a) => a.status === "in_development").length,
    };
  }, [data?.items]);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Agents</h1>
          <p className="text-muted-foreground">
            Manage your AI agents
          </p>
        </div>
        <Button asChild>
          <Link href="/agents/new">
            <Plus className="size-4 mr-2" />
            New Agent
          </Link>
        </Button>
      </div>

      {/* Status Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Object.entries(agentsByStatus).map(([status, count]) => (
          <Card key={status} className="cursor-pointer hover:bg-muted/50" onClick={() => setStatusFilter(status)}>
            <CardContent className="pt-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-2xl font-bold">{count}</p>
                  <p className="text-sm text-muted-foreground capitalize">
                    {statusLabels[status]}
                  </p>
                </div>
                <Badge variant="outline" className={statusColors[status]}>
                  <Bot className="size-4" />
                </Badge>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Tabs & Filters */}
      <Tabs defaultValue="all" value={statusFilter} onValueChange={setStatusFilter}>
        <div className="flex items-center justify-between">
          <TabsList>
            <TabsTrigger value="all">All</TabsTrigger>
            <TabsTrigger value="deployed">Deployed</TabsTrigger>
            <TabsTrigger value="created">Created</TabsTrigger>
            <TabsTrigger value="drafted">Draft</TabsTrigger>
            <TabsTrigger value="in_development">In Dev</TabsTrigger>
          </TabsList>
          
          <div className="relative w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
            <Input
              placeholder="Search agents..."
              className="pl-9"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>

        {/* Agent Grid */}
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
          ) : filteredAgents.length === 0 ? (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center py-12">
                  <Bot className="size-12 mx-auto mb-4 opacity-50" />
                  <h3 className="text-lg font-semibold mb-2">No agents found</h3>
                  <p className="text-muted-foreground mb-4">
                    {searchQuery
                      ? "Try a different search term"
                      : "Create your first agent to get started"}
                  </p>
                  {!searchQuery && (
                    <Button asChild>
                      <Link href="/agents/new">
                        <Plus className="size-4 mr-2" />
                        Create Agent
                      </Link>
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredAgents.map((agent) => (
                <AgentCard
                  key={agent.id}
                  agent={agent}
                  onDelete={() => handleDelete(agent.id, agent.name)}
                  onDeploy={() => handleDeploy(agent.id, agent.name)}
                />
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>

      <TestingSection
        resourceType="agent"
        resourceName="Agent"
        defaultCode={`# Example agent test\nresult = {\n    \"status\": \"ok\",\n    \"notes\": \"Validate agent configuration here\",\n}\n`}
      />
    </div>
  );
}

