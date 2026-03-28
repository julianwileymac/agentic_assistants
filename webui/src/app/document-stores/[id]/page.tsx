"use client";

import * as React from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  FileBox,
  ArrowLeft,
  RefreshCw,
  Trash2,
  Loader2,
  Search,
  FileText,
  Play,
  ExternalLink,
  Clock,
  Timer,
  Download,
  Tag,
} from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { getBackendUrl } from "@/lib/api-client";

const API_BASE = getBackendUrl();

interface DocumentStore {
  id: string;
  name: string;
  description?: string;
  document_count: number;
  source_type?: string;
  ttl_hours?: number;
  created_at: string;
  expires_at?: string;
  status: string;
  tags?: string[];
  dagster_run_id?: string;
  datahub_urn?: string;
  config?: Record<string, unknown>;
}

interface Document {
  id: string;
  title: string;
  content_preview?: string;
  source?: string;
  created_at: string;
  metadata?: Record<string, unknown>;
}

export default function DocumentStoreDetailPage() {
  const params = useParams();
  const router = useRouter();
  const storeId = params.id as string;

  const [store, setStore] = React.useState<DocumentStore | null>(null);
  const [documents, setDocuments] = React.useState<Document[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [searchQuery, setSearchQuery] = React.useState("");
  const [searchResults, setSearchResults] = React.useState<Document[] | null>(null);
  const [searching, setSearching] = React.useState(false);
  const [populating, setPopulating] = React.useState(false);

  const loadStore = React.useCallback(async () => {
    setLoading(true);
    try {
      const [storeRes, docsRes] = await Promise.all([
        fetch(`${API_BASE}/api/v1/document-stores/${storeId}`),
        fetch(`${API_BASE}/api/v1/document-stores/${storeId}/documents`),
      ]);
      if (storeRes.ok) setStore(await storeRes.json());
      if (docsRes.ok) {
        const data = await docsRes.json();
        setDocuments(data.documents || []);
      }
    } catch {
      /* backend unreachable */
    } finally {
      setLoading(false);
    }
  }, [storeId]);

  React.useEffect(() => { loadStore(); }, [loadStore]);

  const handleSearch = async () => {
    if (!searchQuery.trim()) { setSearchResults(null); return; }
    setSearching(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/document-stores/${storeId}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: searchQuery, top_k: 10 }),
      });
      if (res.ok) {
        const data = await res.json();
        setSearchResults(data.results || []);
      }
    } catch {
      toast.error("Search failed");
    } finally {
      setSearching(false);
    }
  };

  const handleDelete = async () => {
    if (!store || !confirm(`Delete document store "${store.name}"?`)) return;
    try {
      const res = await fetch(`${API_BASE}/api/v1/document-stores/${storeId}`, { method: "DELETE" });
      if (res.ok) {
        toast.success("Document store deleted");
        router.push("/document-stores");
      }
    } catch {
      toast.error("Failed to delete");
    }
  };

  const handlePopulate = async () => {
    setPopulating(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/dagster/flows/populate-docstore`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ store_id: storeId }),
      });
      if (res.ok) toast.success("Dagster population flow launched");
      else toast.error("Failed to launch flow");
    } catch {
      toast.error("Backend unreachable");
    } finally {
      setPopulating(false);
    }
  };

  const handleTrack = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/catalog/register/docstore`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ store_id: storeId, name: store?.name }),
      });
      if (res.ok) {
        toast.success("Registered in DataHub");
        loadStore();
      }
    } catch {
      toast.error("DataHub unreachable");
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-48 w-full" />
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  if (!store) {
    return (
      <div className="text-center py-12">
        <FileBox className="size-12 mx-auto mb-4 opacity-50" />
        <h3 className="text-lg font-semibold">Document store not found</h3>
        <Button variant="outline" className="mt-4" asChild>
          <Link href="/document-stores"><ArrowLeft className="size-4 mr-2" />Back to Document Stores</Link>
        </Button>
      </div>
    );
  }

  const displayDocs = searchResults ?? documents;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="sm" asChild>
          <Link href="/document-stores"><ArrowLeft className="size-4" /></Link>
        </Button>
        <div className="flex-1">
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <FileBox className="size-6 text-orange-500" />
            {store.name}
          </h1>
          {store.description && (
            <p className="text-muted-foreground text-sm mt-1">{store.description}</p>
          )}
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={loadStore}>
            <RefreshCw className="size-4 mr-1" /> Refresh
          </Button>
          <Button variant="outline" size="sm" onClick={handlePopulate} disabled={populating}>
            {populating ? <Loader2 className="size-4 mr-1 animate-spin" /> : <Play className="size-4 mr-1" />}
            Populate
          </Button>
          {!store.datahub_urn && (
            <Button variant="outline" size="sm" onClick={handleTrack}>
              <ExternalLink className="size-4 mr-1" /> Track in DataHub
            </Button>
          )}
          <Button variant="destructive" size="sm" onClick={handleDelete}>
            <Trash2 className="size-4 mr-1" /> Delete
          </Button>
        </div>
      </div>

      {/* Info Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <p className="text-xs text-muted-foreground">Documents</p>
            <p className="text-2xl font-bold">{store.document_count}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-xs text-muted-foreground">Status</p>
            <Badge variant={store.status === "active" ? "default" : "secondary"} className="mt-1">
              {store.status}
            </Badge>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-xs text-muted-foreground">TTL</p>
            <p className="text-sm font-medium mt-1">
              {store.ttl_hours ? `${store.ttl_hours} hours` : "No expiry"}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-xs text-muted-foreground">Created</p>
            <p className="text-sm font-medium mt-1">
              {new Date(store.created_at).toLocaleDateString()}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Metadata */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm">Details</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="grid grid-cols-2 gap-2 text-sm">
            {store.source_type && (
              <div className="flex justify-between">
                <span className="text-muted-foreground">Source Type</span>
                <span>{store.source_type}</span>
              </div>
            )}
            {store.expires_at && (
              <div className="flex justify-between">
                <span className="text-muted-foreground">Expires</span>
                <span>{new Date(store.expires_at).toLocaleString()}</span>
              </div>
            )}
            {store.dagster_run_id && (
              <div className="flex justify-between">
                <span className="text-muted-foreground">Dagster Run</span>
                <code className="text-xs bg-muted px-1 rounded">{store.dagster_run_id.slice(0, 8)}</code>
              </div>
            )}
            {store.datahub_urn && (
              <div className="flex justify-between col-span-2">
                <span className="text-muted-foreground">DataHub URN</span>
                <span className="truncate max-w-[300px] text-xs" title={store.datahub_urn}>{store.datahub_urn}</span>
              </div>
            )}
          </div>
          {store.tags && store.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 pt-1">
              {store.tags.map(tag => (
                <Badge key={tag} variant="secondary" className="text-[10px]">
                  <Tag className="size-2.5 mr-0.5" />{tag}
                </Badge>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Search */}
      <div className="flex gap-2">
        <div className="relative flex-1 max-w-lg">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
          <Input
            placeholder="Search documents in this store..."
            className="pl-9"
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleSearch()}
          />
        </div>
        <Button variant="outline" onClick={handleSearch} disabled={searching}>
          {searching ? <Loader2 className="size-4 animate-spin" /> : <Search className="size-4" />}
        </Button>
        {searchResults && (
          <Button variant="ghost" onClick={() => { setSearchResults(null); setSearchQuery(""); }}>
            Clear
          </Button>
        )}
      </div>

      {/* Documents */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm flex items-center justify-between">
            <span>{searchResults ? `Search Results (${searchResults.length})` : `Documents (${documents.length})`}</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {displayDocs.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <FileText className="size-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">
                {searchResults ? "No matching documents" : "No documents yet. Populate via Dagster to add content."}
              </p>
            </div>
          ) : (
            <div className="divide-y">
              {displayDocs.map(doc => (
                <div key={doc.id} className="py-3 space-y-1">
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-medium">{doc.title}</h4>
                    <span className="text-xs text-muted-foreground">
                      {new Date(doc.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  {doc.content_preview && (
                    <p className="text-xs text-muted-foreground line-clamp-2">{doc.content_preview}</p>
                  )}
                  {doc.source && (
                    <Badge variant="outline" className="text-[10px]">{doc.source}</Badge>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
