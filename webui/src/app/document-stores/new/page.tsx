"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  FileBox,
  ArrowLeft,
  ChevronRight,
  ChevronLeft,
  CheckCircle2,
  FolderOpen,
  Globe,
  GitBranch,
  Layers,
  Timer,
  Tag,
} from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { toast } from "sonner";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

const SOURCE_TYPES = [
  { type: "files" as const, label: "Local Files", icon: FolderOpen, placeholder: "/path/to/documents" },
  { type: "url" as const, label: "Web URL", icon: Globe, placeholder: "https://docs.example.com" },
  { type: "github" as const, label: "GitHub Repository", icon: GitBranch, placeholder: "owner/repo" },
  { type: "api" as const, label: "API Endpoint", icon: Layers, placeholder: "https://api.example.com/docs" },
];

const TTL_OPTIONS = [
  { hours: 0, label: "No expiry" },
  { hours: 1, label: "1 hour" },
  { hours: 6, label: "6 hours" },
  { hours: 24, label: "24 hours" },
  { hours: 72, label: "3 days" },
  { hours: 168, label: "1 week" },
];

const STEPS = [
  { id: "basics", label: "Basics" },
  { id: "source", label: "Source" },
  { id: "options", label: "Options" },
  { id: "review", label: "Review" },
] as const;

export default function NewDocumentStorePage() {
  const router = useRouter();
  const [step, setStep] = React.useState(0);
  const [creating, setCreating] = React.useState(false);

  const [name, setName] = React.useState("");
  const [description, setDescription] = React.useState("");
  const [sourceType, setSourceType] = React.useState<string>("files");
  const [sourceValue, setSourceValue] = React.useState("");
  const [ttlHours, setTtlHours] = React.useState(24);
  const [tags, setTags] = React.useState<string[]>([]);
  const [tagInput, setTagInput] = React.useState("");
  const [populateViaDagster, setPopulateViaDagster] = React.useState(true);

  const canAdvance = step === 0 ? name.trim().length > 0 : true;
  const isLast = step === STEPS.length - 1;

  const addTag = () => {
    if (!tagInput.trim() || tags.includes(tagInput.trim())) return;
    setTags(prev => [...prev, tagInput.trim()]);
    setTagInput("");
  };

  const handleCreate = async () => {
    setCreating(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/document-stores`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name,
          description,
          source_type: sourceType,
          source_value: sourceValue || undefined,
          ttl_hours: ttlHours || undefined,
          tags,
          populate_via_dagster: populateViaDagster && !!sourceValue,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        toast.success(`Document store "${name}" created`);
        router.push(`/document-stores/${data.id || ""}`);
      } else {
        toast.error("Failed to create document store");
      }
    } catch {
      toast.error("Backend unreachable");
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="sm" asChild>
          <Link href="/document-stores"><ArrowLeft className="size-4" /></Link>
        </Button>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">New Document Store</h1>
          <p className="text-muted-foreground text-sm">
            Create a lightweight, ephemeral document collection
          </p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileBox className="size-5 text-orange-500" />
            Document Store Setup
          </CardTitle>
          <CardDescription>
            Step {step + 1} of {STEPS.length}: {STEPS[step].label}
          </CardDescription>
          {/* Step indicators */}
          <div className="flex items-center gap-1 pt-2">
            {STEPS.map((s, i) => (
              <React.Fragment key={s.id}>
                <button
                  onClick={() => i <= step && setStep(i)}
                  className={cn(
                    "px-2 py-1 rounded text-xs font-medium transition-colors",
                    i === step ? "bg-primary text-primary-foreground" :
                    i < step ? "bg-primary/10 text-primary cursor-pointer" :
                    "text-muted-foreground"
                  )}
                >
                  {s.label}
                </button>
                {i < STEPS.length - 1 && <ChevronRight className="size-3 text-muted-foreground" />}
              </React.Fragment>
            ))}
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Step 0: Basics */}
          {step === 0 && (
            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Name</label>
                <Input
                  placeholder="e.g. research-session, interview-prep, quick-analysis"
                  value={name}
                  onChange={e => setName(e.target.value)}
                  autoFocus
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Description</label>
                <Input
                  placeholder="Brief description of what this store contains..."
                  value={description}
                  onChange={e => setDescription(e.target.value)}
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
                {tags.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {tags.map(tag => (
                      <Badge key={tag} variant="secondary" className="cursor-pointer" onClick={() =>
                        setTags(prev => prev.filter(t => t !== tag))
                      }>
                        {tag} &times;
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Step 1: Source */}
          {step === 1 && (
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">Choose the data source for this document store</p>
              <div className="grid grid-cols-2 gap-2">
                {SOURCE_TYPES.map(st => (
                  <button
                    key={st.type}
                    onClick={() => setSourceType(st.type)}
                    className={cn(
                      "text-left p-3 rounded-lg border transition-colors",
                      sourceType === st.type ? "border-primary bg-primary/5" : "hover:border-muted-foreground/30"
                    )}
                  >
                    <div className="flex items-center gap-2">
                      <st.icon className="size-4 text-muted-foreground" />
                      <span className="text-sm font-medium">{st.label}</span>
                    </div>
                  </button>
                ))}
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Source Value</label>
                <Input
                  placeholder={SOURCE_TYPES.find(s => s.type === sourceType)?.placeholder || ""}
                  value={sourceValue}
                  onChange={e => setSourceValue(e.target.value)}
                />
                <p className="text-xs text-muted-foreground">
                  Optional -- you can also populate the store later via Dagster flows.
                </p>
              </div>
            </div>
          )}

          {/* Step 2: Options */}
          {step === 2 && (
            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center gap-2">
                  <Timer className="size-4" /> Time-to-Live (TTL)
                </label>
                <p className="text-xs text-muted-foreground">
                  Document stores auto-expire after the TTL period. Choose how long this store should persist.
                </p>
                <div className="grid grid-cols-3 gap-2">
                  {TTL_OPTIONS.map(opt => (
                    <button
                      key={opt.hours}
                      onClick={() => setTtlHours(opt.hours)}
                      className={cn(
                        "p-2 rounded-lg border text-sm transition-colors",
                        ttlHours === opt.hours ? "border-primary bg-primary/5 font-medium" : "hover:border-muted-foreground/30"
                      )}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
              </div>
              <div className="space-y-2 pt-2">
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={populateViaDagster}
                    onChange={e => setPopulateViaDagster(e.target.checked)}
                    className="rounded"
                  />
                  <span className="font-medium">Populate via Dagster on creation</span>
                </label>
                <p className="text-xs text-muted-foreground ml-6">
                  Automatically launch a Dagster flow to ingest documents from the configured source.
                </p>
              </div>
            </div>
          )}

          {/* Step 3: Review */}
          {step === 3 && (
            <div className="space-y-3">
              <p className="text-sm text-muted-foreground">Review your document store configuration</p>
              <div className="rounded-lg border divide-y">
                <div className="p-3 flex justify-between">
                  <span className="text-sm text-muted-foreground">Name</span>
                  <span className="text-sm font-medium">{name}</span>
                </div>
                {description && (
                  <div className="p-3 flex justify-between">
                    <span className="text-sm text-muted-foreground">Description</span>
                    <span className="text-sm">{description}</span>
                  </div>
                )}
                <div className="p-3 flex justify-between">
                  <span className="text-sm text-muted-foreground">Source Type</span>
                  <span className="text-sm">{SOURCE_TYPES.find(s => s.type === sourceType)?.label}</span>
                </div>
                {sourceValue && (
                  <div className="p-3 flex justify-between">
                    <span className="text-sm text-muted-foreground">Source</span>
                    <span className="text-sm truncate max-w-[250px]">{sourceValue}</span>
                  </div>
                )}
                <div className="p-3 flex justify-between">
                  <span className="text-sm text-muted-foreground">TTL</span>
                  <span className="text-sm">{TTL_OPTIONS.find(o => o.hours === ttlHours)?.label}</span>
                </div>
                <div className="p-3 flex justify-between">
                  <span className="text-sm text-muted-foreground">Auto-populate</span>
                  <span className="text-sm">{populateViaDagster && sourceValue ? "Yes, via Dagster" : "No"}</span>
                </div>
                {tags.length > 0 && (
                  <div className="p-3">
                    <span className="text-sm text-muted-foreground">Tags</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {tags.map(tag => <Badge key={tag} variant="secondary">{tag}</Badge>)}
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
                <Button variant="ghost" size="sm" asChild>
                  <Link href="/document-stores">Cancel</Link>
                </Button>
              )}
            </div>
            <Button
              size="sm"
              disabled={!canAdvance || creating}
              onClick={() => isLast ? handleCreate() : setStep(s => s + 1)}
            >
              {isLast ? (
                creating ? "Creating..." : <>Create Document Store</>
              ) : (
                <>Next <ChevronRight className="size-4 ml-1" /></>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
