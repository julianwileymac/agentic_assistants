"use client";

import * as React from "react";
import {
  Search,
  Download,
  RefreshCw,
  FileText,
  Database,
  Brain,
  ExternalLink,
  CheckCircle2,
  XCircle,
  Loader2,
  Eye,
  EyeOff,
  KeyRound,
} from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { apiFetch } from "@/lib/api";

interface HFModel {
  id: string;
  author: string | null;
  downloads: number;
  likes: number;
  tags: string[];
  pipeline_tag: string | null;
  library_name: string | null;
  created_at: string | null;
  last_modified: string | null;
}

interface HFDataset {
  id: string;
  author: string | null;
  downloads: number;
  likes: number;
  tags: string[];
}

interface HFStatus {
  hub_available: boolean;
  token_set: boolean;
  authenticated: boolean;
  user: { name: string; fullname: string } | null;
  storage_backend: string;
}

interface HFPaper {
  id?: string;
  title?: string;
  summary?: string;
  authors?: Array<string | { name?: string }> | string;
  url?: string;
}

export default function HuggingFacePage() {
  const [status, setStatus] = React.useState<HFStatus | null>(null);
  const [models, setModels] = React.useState<HFModel[]>([]);
  const [datasets, setDatasets] = React.useState<HFDataset[]>([]);
  const [papers, setPapers] = React.useState<HFPaper[]>([]);
  const [searchQuery, setSearchQuery] = React.useState("");
  const [taskFilter, setTaskFilter] = React.useState("all");
  const [loading, setLoading] = React.useState(false);
  const [pulling, setPulling] = React.useState<string | null>(null);
  const [activeTab, setActiveTab] = React.useState("models");

  const [tokenInput, setTokenInput] = React.useState("");
  const [showToken, setShowToken] = React.useState(false);
  const [savingToken, setSavingToken] = React.useState(false);
  const [showCredentials, setShowCredentials] = React.useState(false);

  const handleSaveToken = async () => {
    if (!tokenInput.trim()) return;
    setSavingToken(true);
    try {
      await apiFetch("/api/v1/huggingface/credentials", {
        method: "POST",
        body: JSON.stringify({ token: tokenInput.trim() }),
      });
      setTokenInput("");
      setShowCredentials(false);
      fetchStatus();
    } catch {
      /* validation failed, status will reflect it */
    } finally {
      setSavingToken(false);
    }
  };

  const handleClearToken = async () => {
    try {
      await apiFetch("/api/v1/huggingface/credentials", { method: "DELETE" });
      fetchStatus();
    } catch {
      /* ignore */
    }
  };

  const fetchStatus = React.useCallback(async () => {
    try {
      const data = await apiFetch<HFStatus>("/api/v1/huggingface/status");
      setStatus(data);
    } catch {
      setStatus(null);
    }
  }, []);

  React.useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  const searchModels = React.useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (searchQuery) params.set("query", searchQuery);
      if (taskFilter && taskFilter !== "all") params.set("task", taskFilter);
      params.set("limit", "30");
      const data = await apiFetch<{ models: HFModel[] }>(`/api/v1/huggingface/models?${params}`);
      setModels(data.models || []);
    } catch (err) {
      console.error("Failed to search models:", err);
    } finally {
      setLoading(false);
    }
  }, [searchQuery, taskFilter]);

  const searchDatasets = React.useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (searchQuery) params.set("query", searchQuery);
      params.set("limit", "30");
      const data = await apiFetch<{ datasets: HFDataset[] }>(`/api/v1/huggingface/datasets?${params}`);
      setDatasets(data.datasets || []);
    } catch (err) {
      console.error("Failed to search datasets:", err);
    } finally {
      setLoading(false);
    }
  }, [searchQuery]);

  const searchPapers = React.useCallback(async () => {
    if (!searchQuery) return;
    setLoading(true);
    try {
      const data = await apiFetch<{ papers: HFPaper[] }>(
        `/api/v1/huggingface/papers?query=${encodeURIComponent(searchQuery)}&limit=20`
      );
      setPapers(data.papers || []);
    } catch (err) {
      console.error("Failed to search papers:", err);
    } finally {
      setLoading(false);
    }
  }, [searchQuery]);

  const handleSearch = () => {
    if (activeTab === "models") searchModels();
    else if (activeTab === "datasets") searchDatasets();
    else if (activeTab === "papers") searchPapers();
  };

  const handlePullModel = async (repoId: string) => {
    setPulling(repoId);
    try {
      await apiFetch("/api/v1/huggingface/models/pull", {
        method: "POST",
        body: JSON.stringify({ repo_id: repoId }),
      });
    } catch (err) {
      console.error("Failed to pull model:", err);
    } finally {
      setPulling(null);
    }
  };

  const handlePullDataset = async (repoId: string) => {
    setPulling(repoId);
    try {
      await apiFetch("/api/v1/huggingface/datasets/pull", {
        method: "POST",
        body: JSON.stringify({ repo_id: repoId }),
      });
    } catch (err) {
      console.error("Failed to pull dataset:", err);
    } finally {
      setPulling(null);
    }
  };

  const formatNumber = (n: number) => {
    if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
    if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
    return String(n);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">HuggingFace Hub</h1>
          <p className="text-muted-foreground">
            Browse and manage models, datasets, and papers from HuggingFace
          </p>
        </div>
        <div className="flex items-center gap-2">
          {status && (
            <Badge variant={status.authenticated ? "default" : "secondary"}>
              {status.authenticated ? (
                <><CheckCircle2 className="size-3 mr-1" /> {status.user?.name || "Connected"}</>
              ) : status.hub_available ? (
                <><XCircle className="size-3 mr-1" /> Not authenticated</>
              ) : (
                <><XCircle className="size-3 mr-1" /> Hub unavailable</>
              )}
            </Badge>
          )}
          <Button variant="outline" size="sm" onClick={() => setShowCredentials(!showCredentials)}>
            <KeyRound className="size-4 mr-1" />
            Credentials
          </Button>
          <Button variant="outline" size="sm" onClick={fetchStatus}>
            <RefreshCw className="size-4" />
          </Button>
        </div>
      </div>

      {/* Credentials Section */}
      {showCredentials && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <KeyRound className="size-4" />
              HuggingFace Credentials
            </CardTitle>
            <CardDescription>
              Provide your HuggingFace API token for accessing private repos, gated models, and push operations.
              Tokens are stored in-memory only and are never persisted to disk or committed to git.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Current auth status */}
            <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
              {status?.authenticated ? (
                <>
                  <CheckCircle2 className="size-5 text-green-500 shrink-0" />
                  <div className="text-sm">
                    <span className="font-medium">Authenticated</span>
                    {status.user?.name && <span className="text-muted-foreground"> as {status.user.fullname || status.user.name}</span>}
                  </div>
                  <div className="flex-1" />
                  <Button variant="outline" size="sm" onClick={handleClearToken}>
                    Clear Token
                  </Button>
                </>
              ) : (
                <>
                  <XCircle className="size-5 text-muted-foreground shrink-0" />
                  <span className="text-sm text-muted-foreground">
                    {status?.hub_available ? "Not authenticated -- provide a token below" : "Hub unavailable"}
                  </span>
                </>
              )}
            </div>

            {/* Token input */}
            {!status?.authenticated && (
              <div className="flex gap-2">
                <div className="relative flex-1">
                  <Input
                    type={showToken ? "text" : "password"}
                    placeholder="hf_..."
                    value={tokenInput}
                    onChange={e => setTokenInput(e.target.value)}
                    onKeyDown={e => e.key === "Enter" && handleSaveToken()}
                  />
                  <button
                    type="button"
                    onClick={() => setShowToken(!showToken)}
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  >
                    {showToken ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
                  </button>
                </div>
                <Button onClick={handleSaveToken} disabled={savingToken || !tokenInput.trim()}>
                  {savingToken ? <Loader2 className="size-4 animate-spin mr-1" /> : null}
                  Save
                </Button>
              </div>
            )}

            <p className="text-xs text-muted-foreground">
              Get your token from{" "}
              <a href="https://huggingface.co/settings/tokens" target="_blank" rel="noopener noreferrer" className="underline">
                huggingface.co/settings/tokens
              </a>.
              For persistent configuration, set <code className="bg-muted px-1 rounded">HF_TOKEN</code> in your <code className="bg-muted px-1 rounded">.env</code> file.
            </p>
          </CardContent>
        </Card>
      )}

      {/* Search Bar */}
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-2.5 top-2.5 size-4 text-muted-foreground" />
          <Input
            placeholder={`Search ${activeTab}...`}
            className="pl-8"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          />
        </div>
        {activeTab === "models" && (
          <Select value={taskFilter} onValueChange={setTaskFilter}>
            <SelectTrigger className="w-[200px]">
              <SelectValue placeholder="Filter by task" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All tasks</SelectItem>
              <SelectItem value="text-generation">Text Generation</SelectItem>
              <SelectItem value="text-classification">Text Classification</SelectItem>
              <SelectItem value="token-classification">Token Classification</SelectItem>
              <SelectItem value="question-answering">Question Answering</SelectItem>
              <SelectItem value="summarization">Summarization</SelectItem>
              <SelectItem value="translation">Translation</SelectItem>
              <SelectItem value="feature-extraction">Feature Extraction</SelectItem>
              <SelectItem value="image-classification">Image Classification</SelectItem>
            </SelectContent>
          </Select>
        )}
        <Button onClick={handleSearch} disabled={loading}>
          {loading ? <Loader2 className="size-4 animate-spin" /> : <Search className="size-4" />}
          <span className="ml-2">Search</span>
        </Button>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="models" className="gap-1">
            <Brain className="size-4" /> Models
          </TabsTrigger>
          <TabsTrigger value="datasets" className="gap-1">
            <Database className="size-4" /> Datasets
          </TabsTrigger>
          <TabsTrigger value="papers" className="gap-1">
            <FileText className="size-4" /> Papers
          </TabsTrigger>
        </TabsList>

        {/* Models Tab */}
        <TabsContent value="models" className="space-y-4">
          {loading ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {Array.from({ length: 6 }).map((_, i) => (
                <Card key={i}><CardContent className="p-6"><Skeleton className="h-24 w-full" /></CardContent></Card>
              ))}
            </div>
          ) : models.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center text-muted-foreground">
                Search for models on HuggingFace Hub
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {models.map((model) => (
                <Card key={model.id} className="flex flex-col">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium truncate" title={model.id}>
                      {model.id}
                    </CardTitle>
                    <CardDescription className="text-xs">
                      {model.author && `by ${model.author}`}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="flex-1 space-y-3">
                    <div className="flex gap-2 flex-wrap">
                      {model.pipeline_tag && (
                        <Badge variant="secondary" className="text-xs">{model.pipeline_tag}</Badge>
                      )}
                      {model.library_name && (
                        <Badge variant="outline" className="text-xs">{model.library_name}</Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                      <span>Downloads: {formatNumber(model.downloads)}</span>
                      <span>Likes: {formatNumber(model.likes)}</span>
                    </div>
                    <div className="flex gap-2 pt-2">
                      <Button
                        size="sm"
                        variant="outline"
                        className="flex-1"
                        onClick={() => handlePullModel(model.id)}
                        disabled={pulling === model.id}
                      >
                        {pulling === model.id ? (
                          <Loader2 className="size-3 mr-1 animate-spin" />
                        ) : (
                          <Download className="size-3 mr-1" />
                        )}
                        Pull
                      </Button>
                      <Button size="sm" variant="ghost" asChild>
                        <a href={`https://huggingface.co/${model.id}`} target="_blank" rel="noopener noreferrer">
                          <ExternalLink className="size-3" />
                        </a>
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        {/* Datasets Tab */}
        <TabsContent value="datasets" className="space-y-4">
          {loading ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {Array.from({ length: 6 }).map((_, i) => (
                <Card key={i}><CardContent className="p-6"><Skeleton className="h-24 w-full" /></CardContent></Card>
              ))}
            </div>
          ) : datasets.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center text-muted-foreground">
                Search for datasets on HuggingFace Hub
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {datasets.map((ds) => (
                <Card key={ds.id} className="flex flex-col">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium truncate" title={ds.id}>
                      {ds.id}
                    </CardTitle>
                    <CardDescription className="text-xs">
                      {ds.author && `by ${ds.author}`}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="flex-1 space-y-3">
                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                      <span>Downloads: {formatNumber(ds.downloads)}</span>
                      <span>Likes: {formatNumber(ds.likes)}</span>
                    </div>
                    <div className="flex gap-2 pt-2">
                      <Button
                        size="sm"
                        variant="outline"
                        className="flex-1"
                        onClick={() => handlePullDataset(ds.id)}
                        disabled={pulling === ds.id}
                      >
                        {pulling === ds.id ? (
                          <Loader2 className="size-3 mr-1 animate-spin" />
                        ) : (
                          <Download className="size-3 mr-1" />
                        )}
                        Pull
                      </Button>
                      <Button size="sm" variant="ghost" asChild>
                        <a href={`https://huggingface.co/datasets/${ds.id}`} target="_blank" rel="noopener noreferrer">
                          <ExternalLink className="size-3" />
                        </a>
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        {/* Papers Tab */}
        <TabsContent value="papers" className="space-y-4">
          {loading ? (
            <div className="space-y-4">
              {Array.from({ length: 4 }).map((_, i) => (
                <Card key={i}><CardContent className="p-6"><Skeleton className="h-16 w-full" /></CardContent></Card>
              ))}
            </div>
          ) : papers.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center text-muted-foreground">
                Search for papers on HuggingFace
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-3">
              {papers.map((paper, idx) => (
                <Card key={paper.id || idx}>
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <h3 className="font-medium text-sm truncate">
                          {paper.title || paper.id || `Paper ${idx + 1}`}
                        </h3>
                        {paper.summary && (
                          <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                            {paper.summary}
                          </p>
                        )}
                        {paper.authors && (
                          <p className="text-xs text-muted-foreground mt-1">
                            {Array.isArray(paper.authors)
                              ? paper.authors
                                  .slice(0, 3)
                                  .map((author) =>
                                    typeof author === "string" ? author : (author.name || "")
                                  )
                                  .filter(Boolean)
                                  .join(", ")
                              : paper.authors}
                          </p>
                        )}
                      </div>
                      <Button size="sm" variant="ghost" asChild>
                        <a
                          href={paper.url || `https://huggingface.co/papers/${paper.id}`}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          <ExternalLink className="size-3" />
                        </a>
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
