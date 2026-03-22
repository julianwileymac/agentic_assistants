"use client";

import * as React from "react";
import Link from "next/link";
import {
  FileBox,
  Plus,
  RefreshCw,
  Search,
  Trash2,
  Loader2,
  Clock,
  Play,
  ExternalLink,
  FileText,
  AlertTriangle,
  Timer,
} from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

interface DocumentStore {
  id: string;
  name: string;
  description?: string;
  document_count: number;
  source_type?: string;
  ttl_hours?: number;
  created_at: string;
  expires_at?: string;
  status: "active" | "expiring" | "expired";
  tags?: string[];
  dagster_run_id?: string;
  datahub_urn?: string;
}

function getTTLDisplay(store: DocumentStore): { label: string; variant: "default" | "secondary" | "destructive" | "outline" } {
  if (!store.expires_at) return { label: "No expiry", variant: "outline" };
  const remaining = new Date(store.expires_at).getTime() - Date.now();
  if (remaining <= 0) return { label: "Expired", variant: "destructive" };
  const hours = Math.floor(remaining / 3600000);
  if (hours < 1) return { label: `${Math.floor(remaining / 60000)}m left`, variant: "destructive" };
  if (hours < 24) return { label: `${hours}h left`, variant: "secondary" };
  return { label: `${Math.floor(hours / 24)}d left`, variant: "outline" };
}

export default function DocumentStoresPage() {
  const [stores, setStores] = React.useState<DocumentStore[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [searchQuery, setSearchQuery] = React.useState("");
  const [deletingId, setDeletingId] = React.useState<string | null>(null);
  const [populatingId, setPopulatingId] = React.useState<string | null>(null);

  const loadStores = React.useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/document-stores`);
      if (res.ok) {
        const data = await res.json();
        setStores(data.stores || []);
      }
    } catch {
      /* backend unreachable */
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => { loadStores(); }, [loadStores]);

  const filteredStores = React.useMemo(() => {
    if (!searchQuery) return stores;
    const q = searchQuery.toLowerCase();
    return stores.filter(s =>
      s.name.toLowerCase().includes(q) ||
      s.description?.toLowerCase().includes(q)
    );
  }, [stores, searchQuery]);

  const handleDelete = async (id: string, name: string) => {
    if (!confirm(`Delete document store "${name}"?`)) return;
    setDeletingId(id);
    try {
      const res = await fetch(`${API_BASE}/api/v1/document-stores/${id}`, { method: "DELETE" });
      if (res.ok) {
        toast.success(`"${name}" deleted`);
        loadStores();
      } else {
        toast.error("Failed to delete");
      }
    } catch {
      toast.error("Backend unreachable");
    } finally {
      setDeletingId(null);
    }
  };

  const handlePopulate = async (id: string) => {
    setPopulatingId(id);
    try {
      const res = await fetch(`${API_BASE}/api/v1/dagster/flows/populate-docstore`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ store_id: id }),
      });
      if (res.ok) {
        toast.success("Dagster population flow launched");
      } else {
        toast.error("Failed to launch flow");
      }
    } catch {
      toast.error("Backend unreachable");
    } finally {
      setPopulatingId(null);
    }
  };

  const activeCount = stores.filter(s => s.status === "active").length;
  const expiringCount = stores.filter(s => s.status === "expiring").length;
  const totalDocs = stores.reduce((sum, s) => sum + s.document_count, 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Document Stores</h1>
          <p className="text-muted-foreground">
            Ephemeral, lightweight document collections for ad-hoc queries and transient analysis
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={loadStores}>
            <RefreshCw className="size-4 mr-2" />
            Refresh
          </Button>
          <Button asChild>
            <Link href="/document-stores/new">
              <Plus className="size-4 mr-2" />
              New Document Store
            </Link>
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4 flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
              <FileBox className="size-5 text-primary" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stores.length}</p>
              <p className="text-xs text-muted-foreground">Total Stores</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
              <Clock className="size-5 text-green-500" />
            </div>
            <div>
              <p className="text-2xl font-bold">{activeCount}</p>
              <p className="text-xs text-muted-foreground">Active</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-amber-500/10 flex items-center justify-center">
              <AlertTriangle className="size-5 text-amber-500" />
            </div>
            <div>
              <p className="text-2xl font-bold">{expiringCount}</p>
              <p className="text-xs text-muted-foreground">Expiring Soon</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
              <FileText className="size-5 text-blue-500" />
            </div>
            <div>
              <p className="text-2xl font-bold">{totalDocs}</p>
              <p className="text-xs text-muted-foreground">Total Documents</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Search */}
      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
        <Input
          placeholder="Search document stores..."
          className="pl-9"
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
        />
      </div>

      {/* Store List */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[1, 2, 3].map(i => <Skeleton key={i} className="h-32 w-full rounded-lg" />)}
        </div>
      ) : filteredStores.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <FileBox className="size-12 mx-auto mb-4 opacity-50" />
            <h3 className="text-lg font-semibold mb-2">
              {searchQuery ? "No matching document stores" : "No document stores yet"}
            </h3>
            <p className="text-muted-foreground mb-4">
              {searchQuery
                ? "Try a different search term"
                : "Create a document store for quick, transient document indexing"}
            </p>
            {!searchQuery && (
              <Button asChild>
                <Link href="/document-stores/new">
                  <Plus className="size-4 mr-2" /> Create Document Store
                </Link>
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredStores.map(store => {
            const ttl = getTTLDisplay(store);
            return (
              <Card key={store.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-4 space-y-3">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3 min-w-0">
                      <div className="shrink-0 w-9 h-9 rounded-lg bg-orange-500/10 flex items-center justify-center">
                        <FileBox className="size-4 text-orange-500" />
                      </div>
                      <div className="min-w-0">
                        <Link href={`/document-stores/${store.id}`} className="text-sm font-semibold hover:underline truncate block">
                          {store.name}
                        </Link>
                        {store.description && (
                          <p className="text-xs text-muted-foreground truncate">{store.description}</p>
                        )}
                      </div>
                    </div>
                    <Badge variant={ttl.variant} className="gap-1 shrink-0">
                      <Timer className="size-2.5" />
                      {ttl.label}
                    </Badge>
                  </div>

                  <div className="flex items-center gap-2 flex-wrap">
                    <Badge variant="secondary" className="gap-1">
                      <FileText className="size-3" />
                      {store.document_count} docs
                    </Badge>
                    {store.source_type && (
                      <Badge variant="outline" className="text-[10px]">{store.source_type}</Badge>
                    )}
                    {store.datahub_urn && (
                      <Badge variant="outline" className="text-[10px] text-green-600">Tracked</Badge>
                    )}
                    {store.tags?.map(tag => (
                      <Badge key={tag} variant="secondary" className="text-[10px]">{tag}</Badge>
                    ))}
                  </div>

                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline" size="sm" className="h-7 text-xs gap-1"
                      onClick={() => handlePopulate(store.id)}
                      disabled={populatingId === store.id}
                    >
                      {populatingId === store.id
                        ? <Loader2 className="size-3 animate-spin" />
                        : <Play className="size-3" />}
                      Populate via Dagster
                    </Button>
                    <Button variant="outline" size="sm" className="h-7 text-xs gap-1" asChild>
                      <Link href={`/document-stores/${store.id}`}>
                        <ExternalLink className="size-3" /> Browse
                      </Link>
                    </Button>
                    <div className="flex-1" />
                    <Button
                      variant="ghost" size="sm"
                      className="h-7 text-xs gap-1 text-destructive hover:text-destructive"
                      onClick={() => handleDelete(store.id, store.name)}
                      disabled={deletingId === store.id}
                    >
                      {deletingId === store.id
                        ? <Loader2 className="size-3 animate-spin" />
                        : <Trash2 className="size-3" />}
                      Delete
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Info */}
      <Card className="bg-muted/50">
        <CardContent className="pt-6">
          <div className="flex items-start gap-4">
            <FileBox className="size-8 text-muted-foreground" />
            <div>
              <h3 className="font-semibold">About Document Stores</h3>
              <p className="text-sm text-muted-foreground mt-1">
                Document stores are lightweight, ephemeral collections designed for temporary use.
                They support auto-expiring TTLs, are ideal for ad-hoc research, scratch analysis,
                and one-off queries. Use Dagster flows to populate them and DataHub to track lineage.
                For persistent, multi-topic storage, use Knowledge Bases instead.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
