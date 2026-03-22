"use client";

import * as React from "react";
import Link from "next/link";
import { Plus, Search, Puzzle, MoreHorizontal, Copy, Pencil, Trash2, Code } from "lucide-react";

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
import { useComponents } from "@/lib/api";
import type { Component } from "@/lib/types";
import { toast } from "sonner";
import { TestingSection } from "@/components/testing/testing-section";

const categoryColors: Record<string, string> = {
  tool: "bg-blue-500/10 text-blue-500",
  agent: "bg-violet-500/10 text-violet-500",
  task: "bg-emerald-500/10 text-emerald-500",
  pattern: "bg-orange-500/10 text-orange-500",
  utility: "bg-gray-500/10 text-gray-500",
  template: "bg-pink-500/10 text-pink-500",
  snippet: "bg-slate-500/10 text-slate-500",
};

const categoryIcons: Record<string, string> = {
  tool: "🔧",
  agent: "🤖",
  task: "📋",
  pattern: "🧩",
  utility: "⚙️",
  template: "📄",
  snippet: "✂️",
};

function ComponentCard({ component, onDelete }: { component: Component; onDelete: () => void }) {
  const handleCopyCode = async () => {
    await navigator.clipboard.writeText(component.code);
    toast.success("Code copied to clipboard");
  };

  return (
    <Card className="group hover:shadow-lg transition-all duration-300">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-gradient-to-br from-orange-500 to-amber-500 text-white text-lg">
              {categoryIcons[component.category] || "📦"}
            </div>
            <div>
              <CardTitle className="text-lg">
                <Link href={`/library/${component.id}`} className="hover:underline">
                  {component.name}
                </Link>
              </CardTitle>
              <CardDescription className="line-clamp-1">
                {component.description || "No description"}
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
                <Link href={`/library/${component.id}`}>
                  <Pencil className="size-4 mr-2" />
                  Edit
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem onClick={handleCopyCode}>
                <Copy className="size-4 mr-2" />
                Copy Code
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
            <Badge variant="secondary" className={categoryColors[component.category]}>
              {component.category}
            </Badge>
            <span className="text-xs text-muted-foreground">
              v{component.version}
            </span>
          </div>
          
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <Code className="size-3" />
            {component.language}
          </div>

          {component.tags.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {component.tags.slice(0, 3).map((tag) => (
                <Badge key={tag} variant="outline" className="text-xs">
                  {tag}
                </Badge>
              ))}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export default function LibraryPage() {
  const [categoryFilter, setCategoryFilter] = React.useState<string>("all");
  const [searchQuery, setSearchQuery] = React.useState("");
  
  const { data, isLoading, mutate } = useComponents({
    category: categoryFilter === "all" ? undefined : categoryFilter,
    search: searchQuery || undefined,
  });

  const handleDelete = async (componentId: string, componentName: string) => {
    if (!confirm(`Are you sure you want to delete "${componentName}"?`)) {
      return;
    }
    
    try {
      const response = await fetch(`http://localhost:8080/api/v1/components/${componentId}`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        toast.success(`Component "${componentName}" deleted`);
        mutate();
      } else {
        toast.error("Failed to delete component");
      }
    } catch (error) {
      toast.error("Failed to delete component");
    }
  };

  const components = data?.items || [];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Component Library</h1>
          <p className="text-muted-foreground">
            Reusable code snippets and templates
          </p>
        </div>
        <Button asChild>
          <Link href="/library/new">
            <Plus className="size-4 mr-2" />
            New Component
          </Link>
        </Button>
      </div>

      {/* Category Tabs */}
      <Tabs defaultValue="all" value={categoryFilter} onValueChange={setCategoryFilter}>
        <div className="flex items-center justify-between flex-wrap gap-4">
          <TabsList>
            <TabsTrigger value="all">All</TabsTrigger>
            <TabsTrigger value="tool">Tools</TabsTrigger>
            <TabsTrigger value="agent">Agents</TabsTrigger>
            <TabsTrigger value="task">Tasks</TabsTrigger>
            <TabsTrigger value="pattern">Patterns</TabsTrigger>
            <TabsTrigger value="utility">Utilities</TabsTrigger>
            <TabsTrigger value="template">Templates</TabsTrigger>
            <TabsTrigger value="snippet">Snippets</TabsTrigger>
          </TabsList>
          
          <div className="relative w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
            <Input
              placeholder="Search components..."
              className="pl-9"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>

        {/* Components Grid */}
        <TabsContent value={categoryFilter} className="mt-6">
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
          ) : components.length === 0 ? (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center py-12">
                  <Puzzle className="size-12 mx-auto mb-4 opacity-50" />
                  <h3 className="text-lg font-semibold mb-2">No components found</h3>
                  <p className="text-muted-foreground mb-4">
                    {searchQuery
                      ? "Try a different search term"
                      : "Create your first component to get started"}
                  </p>
                  {!searchQuery && (
                    <Button asChild>
                      <Link href="/library/new">
                        <Plus className="size-4 mr-2" />
                        Create Component
                      </Link>
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {components.map((component) => (
                <ComponentCard
                  key={component.id}
                  component={component}
                  onDelete={() => handleDelete(component.id, component.name)}
                />
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>

      <TestingSection
        resourceType="component"
        resourceName="Component Library"
        defaultCode={`# Component library test\nresult = {\n    \"status\": \"ok\",\n    \"notes\": \"Validate component metadata and usage\",\n}\n`}
      />
    </div>
  );
}

