"use client";

import * as React from "react";
import { Book, Search, Database, Plus, RefreshCw, Trash2 } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useCollections } from "@/lib/api";
import { toast } from "sonner";

export default function KnowledgePage() {
  const [searchQuery, setSearchQuery] = React.useState("");
  const { data, isLoading, mutate } = useCollections();

  const collections = data?.collections || [];

  const filteredCollections = React.useMemo(() => {
    if (!searchQuery) return collections;
    const query = searchQuery.toLowerCase();
    return collections.filter((c) => c.name.toLowerCase().includes(query));
  }, [collections, searchQuery]);

  const handleDelete = async (name: string) => {
    if (!confirm(`Are you sure you want to delete collection "${name}"?`)) {
      return;
    }
    
    try {
      const response = await fetch(`http://localhost:8080/collections/${name}`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        toast.success(`Collection "${name}" deleted`);
        mutate();
      } else {
        toast.error("Failed to delete collection");
      }
    } catch (error) {
      toast.error("Failed to delete collection");
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Knowledge Bases</h1>
          <p className="text-muted-foreground">
            Manage vector store collections and indexed content
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={() => mutate()}>
            <RefreshCw className="size-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Search */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
          <Input
            placeholder="Search collections..."
            className="pl-9"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* Collections Table */}
      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-6 space-y-4">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : filteredCollections.length === 0 ? (
            <div className="text-center py-12">
              <Book className="size-12 mx-auto mb-4 opacity-50" />
              <h3 className="text-lg font-semibold mb-2">No collections found</h3>
              <p className="text-muted-foreground mb-4">
                {searchQuery
                  ? "Try a different search term"
                  : "Index a repository to create a knowledge base"}
              </p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Collection Name</TableHead>
                  <TableHead>Documents</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredCollections.map((collection) => (
                  <TableRow key={collection.name}>
                    <TableCell className="font-medium">
                      <div className="flex items-center gap-2">
                        <Database className="size-4 text-muted-foreground" />
                        {collection.name}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="secondary">
                        {collection.document_count} documents
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={() => handleDelete(collection.name)}
                        className="text-destructive hover:text-destructive"
                      >
                        <Trash2 className="size-4 mr-2" />
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

      {/* Info */}
      <Card className="bg-muted/50">
        <CardContent className="pt-6">
          <div className="flex items-start gap-4">
            <Book className="size-8 text-muted-foreground" />
            <div>
              <h3 className="font-semibold">Vector Store Collections</h3>
              <p className="text-sm text-muted-foreground mt-1">
                Collections store indexed code and documentation as vector embeddings. 
                Use the Repository Indexing Crew or the API to add new content. 
                Collections support semantic search for RAG-based queries.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

