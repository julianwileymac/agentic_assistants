"use client";

import * as React from "react";
import {
  Book,
  Search,
  Plus,
  RefreshCw,
  Database,
  Layers,
  Settings2,
  Sparkles,
  Zap,
} from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useCollections } from "@/lib/api";
import { toast } from "sonner";
import { SetupWizard, type KBSetupConfig } from "@/components/knowledge/setup-wizard";
import { KBCard, type KnowledgeBaseInfo } from "@/components/knowledge/kb-card";
import { getBackendUrl } from "@/lib/api-client";

const API_BASE = getBackendUrl();

type TabId = "overview" | "setup" | "configuration";

export default function KnowledgePage() {
  const [searchQuery, setSearchQuery] = React.useState("");
  const [activeTab, setActiveTab] = React.useState<TabId>("overview");
  const [showWizard, setShowWizard] = React.useState(false);
  const [deletingKB, setDeletingKB] = React.useState<string | null>(null);
  const [populatingKB, setPopulatingKB] = React.useState<string | null>(null);
  const { data, isLoading, mutate } = useCollections();

  const collections = data?.collections || [];

  const knowledgeBases: KnowledgeBaseInfo[] = React.useMemo(() => {
    return collections.map(c => ({
      name: c.name,
      document_count: c.document_count,
    }));
  }, [collections]);

  const filteredKBs = React.useMemo(() => {
    if (!searchQuery) return knowledgeBases;
    const query = searchQuery.toLowerCase();
    return knowledgeBases.filter(
      kb => kb.name.toLowerCase().includes(query) ||
            kb.description?.toLowerCase().includes(query)
    );
  }, [knowledgeBases, searchQuery]);

  const handleDelete = async (name: string) => {
    if (!confirm(`Delete knowledge base "${name}"? This cannot be undone.`)) return;
    setDeletingKB(name);
    try {
      const response = await fetch(`${API_BASE}/collections/${name}`, { method: "DELETE" });
      if (response.ok) {
        toast.success(`Knowledge base "${name}" deleted`);
        mutate();
      } else {
        toast.error("Failed to delete knowledge base");
      }
    } catch {
      toast.error("Failed to delete knowledge base");
    } finally {
      setDeletingKB(null);
    }
  };

  const handlePopulate = async (name: string) => {
    setPopulatingKB(name);
    try {
      const response = await fetch(`${API_BASE}/api/v1/dagster/flows/populate-kb`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ collection_name: name }),
      });
      if (response.ok) {
        toast.success(`Dagster population flow launched for "${name}"`);
      } else {
        toast.error("Failed to launch population flow");
      }
    } catch {
      toast.error("Backend unreachable");
    } finally {
      setPopulatingKB(null);
    }
  };

  const handleTrack = async (name: string) => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/catalog/register/kb`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name }),
      });
      if (response.ok) {
        toast.success(`"${name}" registered in DataHub`);
        mutate();
      } else {
        toast.error("Failed to register in DataHub");
      }
    } catch {
      toast.error("DataHub unreachable");
    }
  };

  const handleWizardComplete = async (config: KBSetupConfig) => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/knowledge-bases`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config),
      });
      if (response.ok) {
        toast.success(`Knowledge base "${config.name}" created`);
        setShowWizard(false);
        setActiveTab("overview");
        mutate();
      } else {
        toast.error("Failed to create knowledge base");
      }
    } catch {
      toast.error("Backend unreachable");
    }
  };

  const tabs: { id: TabId; label: string; icon: React.ElementType }[] = [
    { id: "overview", label: "Overview", icon: Layers },
    { id: "setup", label: "Guided Setup", icon: Sparkles },
    { id: "configuration", label: "Configuration", icon: Settings2 },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Knowledge Bases</h1>
          <p className="text-muted-foreground">
            Persistent, multi-topic vector stores for RAG-powered queries and project integration
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={() => mutate()}>
            <RefreshCw className="size-4 mr-2" />
            Refresh
          </Button>
          <Button onClick={() => { setShowWizard(true); setActiveTab("setup"); }}>
            <Plus className="size-4 mr-2" />
            New Knowledge Base
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-1.5 border-b-2 px-3 py-2 text-sm font-medium transition-colors ${
              activeTab === tab.id
                ? "border-primary text-foreground"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            <tab.icon className="size-3.5" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === "overview" && (
        <div className="space-y-4">
          {/* Stats */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Card>
              <CardContent className="p-4 flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Database className="size-5 text-primary" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{knowledgeBases.length}</p>
                  <p className="text-xs text-muted-foreground">Knowledge Bases</p>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                  <Book className="size-5 text-blue-500" />
                </div>
                <div>
                  <p className="text-2xl font-bold">
                    {knowledgeBases.reduce((sum, kb) => sum + kb.document_count, 0)}
                  </p>
                  <p className="text-xs text-muted-foreground">Total Documents</p>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-amber-500/10 flex items-center justify-center">
                  <Zap className="size-5 text-amber-500" />
                </div>
                <div>
                  <p className="text-2xl font-bold">0</p>
                  <p className="text-xs text-muted-foreground">Active Dagster Flows</p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Search */}
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
            <Input
              placeholder="Search knowledge bases..."
              className="pl-9"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
            />
          </div>

          {/* KB Cards */}
          {isLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[1, 2, 3].map(i => <Skeleton key={i} className="h-36 w-full rounded-lg" />)}
            </div>
          ) : filteredKBs.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <Book className="size-12 mx-auto mb-4 opacity-50" />
                <h3 className="text-lg font-semibold mb-2">
                  {searchQuery ? "No matching knowledge bases" : "No knowledge bases yet"}
                </h3>
                <p className="text-muted-foreground mb-4">
                  {searchQuery
                    ? "Try a different search term"
                    : "Create your first knowledge base to enable RAG-powered queries"}
                </p>
                {!searchQuery && (
                  <Button onClick={() => { setShowWizard(true); setActiveTab("setup"); }}>
                    <Plus className="size-4 mr-2" />
                    Create Knowledge Base
                  </Button>
                )}
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filteredKBs.map(kb => (
                <KBCard
                  key={kb.name}
                  kb={kb}
                  onDelete={handleDelete}
                  onPopulate={handlePopulate}
                  onTrack={handleTrack}
                  deleting={deletingKB === kb.name}
                  populating={populatingKB === kb.name}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Setup Tab */}
      {activeTab === "setup" && (
        <div className="max-w-2xl">
          {showWizard ? (
            <SetupWizard
              onComplete={handleWizardComplete}
              onCancel={() => { setShowWizard(false); setActiveTab("overview"); }}
            />
          ) : (
            <Card>
              <CardContent className="py-12 text-center">
                <Sparkles className="size-12 mx-auto mb-4 text-primary/50" />
                <h3 className="text-lg font-semibold mb-2">Guided Knowledge Base Setup</h3>
                <p className="text-muted-foreground mb-4">
                  Walk through a step-by-step wizard to configure your embedding model,
                  vector store, and data sources for a new knowledge base.
                </p>
                <Button onClick={() => setShowWizard(true)}>
                  <Plus className="size-4 mr-2" />
                  Start Setup Wizard
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Configuration Tab */}
      {activeTab === "configuration" && (
        <div className="space-y-4">
          <Card>
            <CardContent className="p-6 space-y-4">
              <h3 className="text-sm font-semibold flex items-center gap-2">
                <Settings2 className="size-4" />
                Global Defaults
              </h3>
              <p className="text-xs text-muted-foreground">
                Default settings applied when creating new knowledge bases. Individual KBs can override these.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-medium">Default Embedding Model</label>
                  <Input value="nomic-embed-text" readOnly className="bg-muted" />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-medium">Default Vector Store</label>
                  <Input value="lancedb" readOnly className="bg-muted" />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-medium">Default Chunk Size</label>
                  <Input type="number" value="512" readOnly className="bg-muted" />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-medium">Default Chunk Overlap</label>
                  <Input type="number" value="50" readOnly className="bg-muted" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6 space-y-4">
              <h3 className="text-sm font-semibold flex items-center gap-2">
                <Zap className="size-4" />
                Dagster Integration
              </h3>
              <p className="text-xs text-muted-foreground">
                Knowledge bases can be automatically populated and refreshed using Dagster orchestration flows.
              </p>
              <div className="rounded-lg border p-3 space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span>Auto-refresh schedule</span>
                  <Badge variant="outline">Not configured</Badge>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span>DataHub tracking</span>
                  <Badge variant="outline">Available</Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-muted/50">
            <CardContent className="pt-6">
              <div className="flex items-start gap-4">
                <Book className="size-8 text-muted-foreground" />
                <div>
                  <h3 className="font-semibold">About Knowledge Bases</h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    Knowledge bases are persistent, versioned vector stores designed for ongoing use.
                    They can contain multiple topics, link to one or more projects, and are backed by
                    Dagster flows for automated ingestion and DataHub for metadata tracking.
                    Unlike document stores, knowledge bases are meant to be long-lived resources.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
