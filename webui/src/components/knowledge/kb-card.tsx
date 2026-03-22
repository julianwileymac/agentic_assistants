"use client";

import * as React from "react";
import {
  Database,
  ChevronDown,
  ChevronUp,
  Trash2,
  Play,
  Settings2,
  ExternalLink,
  Clock,
  Loader2,
  FileText,
  Tag,
  Link2,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

export interface KnowledgeBaseInfo {
  name: string;
  document_count: number;
  description?: string;
  embedding_model?: string;
  vector_store?: string;
  chunk_size?: number;
  chunk_overlap?: number;
  project_ids?: string[];
  tags?: string[];
  last_updated?: string;
  dagster_schedule?: string;
  dagster_last_run?: string;
  datahub_urn?: string;
}

interface KBCardProps {
  kb: KnowledgeBaseInfo;
  onDelete: (name: string) => void;
  onPopulate: (name: string) => void;
  onTrack: (name: string) => void;
  deleting?: boolean;
  populating?: boolean;
}

export function KBCard({ kb, onDelete, onPopulate, onTrack, deleting, populating }: KBCardProps) {
  const [expanded, setExpanded] = React.useState(false);

  return (
    <Card className={cn("transition-shadow hover:shadow-md", expanded && "ring-1 ring-primary/20")}>
      <CardContent className="p-4 space-y-3">
        {/* Header row */}
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3 min-w-0 flex-1">
            <div className="shrink-0 w-9 h-9 rounded-lg bg-primary/10 flex items-center justify-center">
              <Database className="size-4 text-primary" />
            </div>
            <div className="min-w-0 flex-1">
              <h3 className="text-sm font-semibold truncate">{kb.name}</h3>
              {kb.description && (
                <p className="text-xs text-muted-foreground truncate">{kb.description}</p>
              )}
            </div>
          </div>
          <button onClick={() => setExpanded(!expanded)} className="shrink-0 p-1 hover:bg-muted rounded">
            {expanded ? <ChevronUp className="size-4" /> : <ChevronDown className="size-4" />}
          </button>
        </div>

        {/* Stats row */}
        <div className="flex items-center gap-3 flex-wrap">
          <Badge variant="secondary" className="gap-1">
            <FileText className="size-3" />
            {kb.document_count} docs
          </Badge>
          {kb.embedding_model && (
            <Badge variant="outline" className="gap-1 text-[10px]">
              {kb.embedding_model}
            </Badge>
          )}
          {kb.dagster_schedule && (
            <Badge variant="outline" className="gap-1 text-[10px]">
              <Clock className="size-2.5" />
              {kb.dagster_schedule}
            </Badge>
          )}
          {kb.datahub_urn && (
            <Badge variant="outline" className="gap-1 text-[10px] text-green-600">
              <Link2 className="size-2.5" />
              Tracked
            </Badge>
          )}
          {kb.tags?.map(tag => (
            <Badge key={tag} variant="secondary" className="text-[10px]">
              <Tag className="size-2.5 mr-0.5" />{tag}
            </Badge>
          ))}
        </div>

        {/* Actions row */}
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            className="h-7 text-xs gap-1"
            onClick={() => onPopulate(kb.name)}
            disabled={populating}
          >
            {populating ? <Loader2 className="size-3 animate-spin" /> : <Play className="size-3" />}
            Populate via Dagster
          </Button>
          {!kb.datahub_urn && (
            <Button
              variant="outline"
              size="sm"
              className="h-7 text-xs gap-1"
              onClick={() => onTrack(kb.name)}
            >
              <ExternalLink className="size-3" />
              Track in DataHub
            </Button>
          )}
          <div className="flex-1" />
          <Button
            variant="ghost"
            size="sm"
            className="h-7 text-xs gap-1 text-destructive hover:text-destructive"
            onClick={() => onDelete(kb.name)}
            disabled={deleting}
          >
            {deleting ? <Loader2 className="size-3 animate-spin" /> : <Trash2 className="size-3" />}
            Delete
          </Button>
        </div>

        {/* Expanded configuration panel */}
        {expanded && (
          <div className="border-t pt-3 space-y-2">
            <div className="flex items-center gap-2 text-xs font-medium text-muted-foreground">
              <Settings2 className="size-3" />
              Configuration
            </div>
            <div className="grid grid-cols-2 gap-x-6 gap-y-1.5 text-xs">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Vector Store</span>
                <span>{kb.vector_store || "lancedb"}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Embedding</span>
                <span>{kb.embedding_model || "nomic-embed-text"}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Chunk Size</span>
                <span>{kb.chunk_size || 512}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Overlap</span>
                <span>{kb.chunk_overlap || 50}</span>
              </div>
              {kb.last_updated && (
                <div className="flex justify-between col-span-2">
                  <span className="text-muted-foreground">Last Updated</span>
                  <span>{new Date(kb.last_updated).toLocaleDateString()}</span>
                </div>
              )}
              {kb.dagster_last_run && (
                <div className="flex justify-between col-span-2">
                  <span className="text-muted-foreground">Last Dagster Run</span>
                  <span>{kb.dagster_last_run}</span>
                </div>
              )}
              {kb.datahub_urn && (
                <div className="flex justify-between col-span-2">
                  <span className="text-muted-foreground">DataHub URN</span>
                  <span className="truncate max-w-[200px]" title={kb.datahub_urn}>{kb.datahub_urn}</span>
                </div>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
