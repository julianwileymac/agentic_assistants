"use client";

import * as React from "react";
import {
  Database,
  ChevronRight,
  ChevronLeft,
  CheckCircle2,
  Loader2,
  FolderOpen,
  Globe,
  GitBranch,
  FileText,
  Cpu,
  HardDrive,
  Layers,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface SetupWizardProps {
  onComplete: (config: KBSetupConfig) => void;
  onCancel: () => void;
}

export interface KBSetupConfig {
  name: string;
  description: string;
  embedding_model: string;
  vector_store: string;
  chunk_size: number;
  chunk_overlap: number;
  sources: KBSource[];
  project_id?: string;
  schedule?: string;
  tags: string[];
}

interface KBSource {
  type: "files" | "url" | "github" | "api";
  value: string;
  label: string;
}

const STEPS = [
  { id: "basics", label: "Basics", icon: FileText },
  { id: "embedding", label: "Embedding", icon: Cpu },
  { id: "storage", label: "Storage", icon: HardDrive },
  { id: "sources", label: "Sources", icon: FolderOpen },
  { id: "review", label: "Review", icon: CheckCircle2 },
] as const;

const EMBEDDING_MODELS = [
  { id: "nomic-embed-text", name: "Nomic Embed Text", description: "Fast, high-quality local embeddings via Ollama", size: "274M" },
  { id: "all-minilm", name: "all-MiniLM-L6-v2", description: "Lightweight sentence transformer", size: "80M" },
  { id: "bge-large", name: "BGE Large EN", description: "High accuracy BAAI embedding model", size: "1.2G" },
  { id: "openai-ada-002", name: "OpenAI Ada 002", description: "OpenAI hosted embedding model (requires API key)", size: "API" },
];

const VECTOR_STORES = [
  { id: "lancedb", name: "LanceDB", description: "Embedded columnar vector store, zero-config", recommended: true },
  { id: "chromadb", name: "ChromaDB", description: "Open-source embedding database", recommended: false },
  { id: "qdrant", name: "Qdrant", description: "High-performance vector search engine", recommended: false },
];

const SOURCE_TYPES = [
  { type: "files" as const, label: "Local Files", icon: FolderOpen, description: "Upload files or point to a directory" },
  { type: "url" as const, label: "Web URL", icon: Globe, description: "Crawl and index web pages" },
  { type: "github" as const, label: "GitHub Repository", icon: GitBranch, description: "Clone and index a repo" },
  { type: "api" as const, label: "API Endpoint", icon: Layers, description: "Fetch documents from an API" },
];

export function SetupWizard({ onComplete, onCancel }: SetupWizardProps) {
  const [step, setStep] = React.useState(0);
  const [config, setConfig] = React.useState<KBSetupConfig>({
    name: "",
    description: "",
    embedding_model: "nomic-embed-text",
    vector_store: "lancedb",
    chunk_size: 512,
    chunk_overlap: 50,
    sources: [],
    tags: [],
  });
  const [newSource, setNewSource] = React.useState({ type: "files" as KBSource["type"], value: "" });
  const [tagInput, setTagInput] = React.useState("");

  const currentStep = STEPS[step];
  const canAdvance = step === 0 ? config.name.trim().length > 0 : true;
  const isLast = step === STEPS.length - 1;

  const addSource = () => {
    if (!newSource.value.trim()) return;
    const sourceType = SOURCE_TYPES.find(s => s.type === newSource.type);
    setConfig(prev => ({
      ...prev,
      sources: [...prev.sources, {
        type: newSource.type,
        value: newSource.value.trim(),
        label: sourceType?.label || newSource.type,
      }],
    }));
    setNewSource(prev => ({ ...prev, value: "" }));
  };

  const removeSource = (idx: number) => {
    setConfig(prev => ({ ...prev, sources: prev.sources.filter((_, i) => i !== idx) }));
  };

  const addTag = () => {
    if (!tagInput.trim() || config.tags.includes(tagInput.trim())) return;
    setConfig(prev => ({ ...prev, tags: [...prev.tags, tagInput.trim()] }));
    setTagInput("");
  };

  return (
    <Card className="border-primary/20">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Database className="size-5" />
          Create Knowledge Base
        </CardTitle>
        <CardDescription>
          Set up a new persistent knowledge base for RAG-powered queries
        </CardDescription>
        {/* Step indicators */}
        <div className="flex items-center gap-1 pt-3">
          {STEPS.map((s, i) => (
            <React.Fragment key={s.id}>
              <button
                onClick={() => i <= step && setStep(i)}
                className={cn(
                  "flex items-center gap-1.5 px-2 py-1 rounded text-xs font-medium transition-colors",
                  i === step ? "bg-primary text-primary-foreground" :
                  i < step ? "bg-primary/10 text-primary cursor-pointer hover:bg-primary/20" :
                  "text-muted-foreground"
                )}
              >
                <s.icon className="size-3" />
                {s.label}
              </button>
              {i < STEPS.length - 1 && (
                <ChevronRight className="size-3 text-muted-foreground" />
              )}
            </React.Fragment>
          ))}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Step 0: Basics */}
        {currentStep.id === "basics" && (
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Name</label>
              <Input
                placeholder="e.g. project-docs, codebase-v2, research-papers"
                value={config.name}
                onChange={e => setConfig(prev => ({ ...prev, name: e.target.value }))}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Description</label>
              <Input
                placeholder="What this knowledge base contains..."
                value={config.description}
                onChange={e => setConfig(prev => ({ ...prev, description: e.target.value }))}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Tags</label>
              <div className="flex gap-2">
                <Input
                  placeholder="Add tag..."
                  value={tagInput}
                  onChange={e => setTagInput(e.target.value)}
                  onKeyDown={e => e.key === "Enter" && (e.preventDefault(), addTag())}
                  className="flex-1"
                />
                <Button variant="outline" size="sm" onClick={addTag}>Add</Button>
              </div>
              {config.tags.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {config.tags.map(tag => (
                    <Badge key={tag} variant="secondary" className="cursor-pointer" onClick={() =>
                      setConfig(prev => ({ ...prev, tags: prev.tags.filter(t => t !== tag) }))
                    }>
                      {tag} &times;
                    </Badge>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Step 1: Embedding Model */}
        {currentStep.id === "embedding" && (
          <div className="space-y-3">
            <p className="text-sm text-muted-foreground">Choose how documents are converted to vector embeddings</p>
            {EMBEDDING_MODELS.map(model => (
              <button
                key={model.id}
                onClick={() => setConfig(prev => ({ ...prev, embedding_model: model.id }))}
                className={cn(
                  "w-full text-left p-3 rounded-lg border transition-colors",
                  config.embedding_model === model.id
                    ? "border-primary bg-primary/5"
                    : "hover:border-muted-foreground/30"
                )}
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">{model.name}</span>
                  <Badge variant="outline" className="text-xs">{model.size}</Badge>
                </div>
                <p className="text-xs text-muted-foreground mt-1">{model.description}</p>
              </button>
            ))}
            <div className="grid grid-cols-2 gap-4 pt-2">
              <div className="space-y-1">
                <label className="text-xs font-medium text-muted-foreground">Chunk Size</label>
                <Input
                  type="number"
                  value={config.chunk_size}
                  onChange={e => setConfig(prev => ({ ...prev, chunk_size: parseInt(e.target.value) || 512 }))}
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium text-muted-foreground">Chunk Overlap</label>
                <Input
                  type="number"
                  value={config.chunk_overlap}
                  onChange={e => setConfig(prev => ({ ...prev, chunk_overlap: parseInt(e.target.value) || 50 }))}
                />
              </div>
            </div>
          </div>
        )}

        {/* Step 2: Vector Store */}
        {currentStep.id === "storage" && (
          <div className="space-y-3">
            <p className="text-sm text-muted-foreground">Select the vector database backend for persistent storage</p>
            {VECTOR_STORES.map(store => (
              <button
                key={store.id}
                onClick={() => setConfig(prev => ({ ...prev, vector_store: store.id }))}
                className={cn(
                  "w-full text-left p-3 rounded-lg border transition-colors",
                  config.vector_store === store.id
                    ? "border-primary bg-primary/5"
                    : "hover:border-muted-foreground/30"
                )}
              >
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">{store.name}</span>
                  {store.recommended && <Badge className="text-[10px]">Recommended</Badge>}
                </div>
                <p className="text-xs text-muted-foreground mt-1">{store.description}</p>
              </button>
            ))}
          </div>
        )}

        {/* Step 3: Data Sources */}
        {currentStep.id === "sources" && (
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">Add one or more data sources to populate the knowledge base</p>
            <div className="grid grid-cols-2 gap-2">
              {SOURCE_TYPES.map(st => (
                <button
                  key={st.type}
                  onClick={() => setNewSource(prev => ({ ...prev, type: st.type }))}
                  className={cn(
                    "text-left p-2.5 rounded-lg border transition-colors",
                    newSource.type === st.type ? "border-primary bg-primary/5" : "hover:border-muted-foreground/30"
                  )}
                >
                  <div className="flex items-center gap-2">
                    <st.icon className="size-3.5 text-muted-foreground" />
                    <span className="text-xs font-medium">{st.label}</span>
                  </div>
                </button>
              ))}
            </div>
            <div className="flex gap-2">
              <Input
                placeholder={
                  newSource.type === "files" ? "/path/to/documents" :
                  newSource.type === "url" ? "https://docs.example.com" :
                  newSource.type === "github" ? "owner/repo" :
                  "https://api.example.com/docs"
                }
                value={newSource.value}
                onChange={e => setNewSource(prev => ({ ...prev, value: e.target.value }))}
                onKeyDown={e => e.key === "Enter" && (e.preventDefault(), addSource())}
                className="flex-1"
              />
              <Button variant="outline" size="sm" onClick={addSource}>Add</Button>
            </div>
            {config.sources.length > 0 && (
              <div className="space-y-1">
                {config.sources.map((src, i) => (
                  <div key={i} className="flex items-center justify-between p-2 rounded bg-muted/50 text-sm">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="text-[10px]">{src.type}</Badge>
                      <span className="truncate max-w-[300px]">{src.value}</span>
                    </div>
                    <Button variant="ghost" size="sm" className="h-6 px-2 text-xs" onClick={() => removeSource(i)}>
                      Remove
                    </Button>
                  </div>
                ))}
              </div>
            )}
            {config.sources.length === 0 && (
              <p className="text-xs text-muted-foreground italic">
                Sources are optional during setup. You can add them later or populate via Dagster flows.
              </p>
            )}
          </div>
        )}

        {/* Step 4: Review */}
        {currentStep.id === "review" && (
          <div className="space-y-3">
            <p className="text-sm text-muted-foreground">Review your knowledge base configuration</p>
            <div className="rounded-lg border divide-y">
              <div className="p-3 flex justify-between">
                <span className="text-sm text-muted-foreground">Name</span>
                <span className="text-sm font-medium">{config.name}</span>
              </div>
              {config.description && (
                <div className="p-3 flex justify-between">
                  <span className="text-sm text-muted-foreground">Description</span>
                  <span className="text-sm">{config.description}</span>
                </div>
              )}
              <div className="p-3 flex justify-between">
                <span className="text-sm text-muted-foreground">Embedding Model</span>
                <span className="text-sm font-medium">{EMBEDDING_MODELS.find(m => m.id === config.embedding_model)?.name}</span>
              </div>
              <div className="p-3 flex justify-between">
                <span className="text-sm text-muted-foreground">Vector Store</span>
                <span className="text-sm font-medium">{VECTOR_STORES.find(s => s.id === config.vector_store)?.name}</span>
              </div>
              <div className="p-3 flex justify-between">
                <span className="text-sm text-muted-foreground">Chunk Size / Overlap</span>
                <span className="text-sm">{config.chunk_size} / {config.chunk_overlap}</span>
              </div>
              <div className="p-3 flex justify-between">
                <span className="text-sm text-muted-foreground">Data Sources</span>
                <span className="text-sm">{config.sources.length} configured</span>
              </div>
              {config.tags.length > 0 && (
                <div className="p-3">
                  <span className="text-sm text-muted-foreground">Tags</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {config.tags.map(tag => <Badge key={tag} variant="secondary">{tag}</Badge>)}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Navigation */}
        <div className="flex items-center justify-between pt-2">
          <div>
            {step > 0 ? (
              <Button variant="outline" size="sm" onClick={() => setStep(s => s - 1)}>
                <ChevronLeft className="size-4 mr-1" /> Back
              </Button>
            ) : (
              <Button variant="ghost" size="sm" onClick={onCancel}>Cancel</Button>
            )}
          </div>
          <Button
            size="sm"
            disabled={!canAdvance}
            onClick={() => isLast ? onComplete(config) : setStep(s => s + 1)}
          >
            {isLast ? (
              <>Create Knowledge Base</>
            ) : (
              <>Next <ChevronRight className="size-4 ml-1" /></>
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
