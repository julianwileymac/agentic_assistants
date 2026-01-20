"use client";

import * as React from "react";
import {
  X,
  StickyNote,
  Highlighter,
  FileText,
  Plus,
  Trash2,
  ChevronRight,
  ChevronLeft,
  Upload,
  Loader2,
  MessageSquare,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";
import {
  useLearningAnnotations,
  useCreateAnnotation,
  useDeleteAnnotation,
  useLearningArtifacts,
} from "@/lib/api";
import { useLearningStore } from "@/lib/store";
import { toast } from "sonner";

interface NotesPanelProps {
  className?: string;
}

function NoteItem({
  annotation,
  onDelete,
}: {
  annotation: any;
  onDelete: () => void;
}) {
  const typeIcons: Record<string, React.ElementType> = {
    note: StickyNote,
    highlight: Highlighter,
    question: MessageSquare,
    bookmark: FileText,
  };

  const Icon = typeIcons[annotation.annotation_type] || StickyNote;

  return (
    <div className="group p-3 rounded-lg border bg-card hover:bg-muted/50 transition-colors">
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-start gap-2 flex-1 min-w-0">
          <Icon className="size-4 text-muted-foreground mt-0.5 shrink-0" />
          <div className="flex-1 min-w-0">
            <p className="text-sm whitespace-pre-wrap break-words">{annotation.content}</p>
            <div className="flex items-center gap-2 mt-2">
              <Badge variant="outline" className="text-xs capitalize">
                {annotation.annotation_type}
              </Badge>
              <span className="text-xs text-muted-foreground">
                {new Date(annotation.created_at).toLocaleDateString()}
              </span>
            </div>
          </div>
        </div>
        <Button
          variant="ghost"
          size="icon"
          className="size-6 opacity-0 group-hover:opacity-100 transition-opacity shrink-0"
          onClick={onDelete}
        >
          <Trash2 className="size-3" />
        </Button>
      </div>
    </div>
  );
}

function ArtifactItem({ artifact }: { artifact: any }) {
  return (
    <div className="p-3 rounded-lg border bg-card hover:bg-muted/50 transition-colors">
      <div className="flex items-start gap-3">
        <div className="p-2 rounded bg-muted">
          <FileText className="size-4 text-muted-foreground" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-medium text-sm truncate">{artifact.name}</p>
          {artifact.description && (
            <p className="text-xs text-muted-foreground line-clamp-1">{artifact.description}</p>
          )}
          <div className="flex items-center gap-2 mt-1">
            <Badge variant="secondary" className="text-xs">
              {artifact.file_type || "File"}
            </Badge>
            <span className="text-xs text-muted-foreground">
              {new Date(artifact.created_at).toLocaleDateString()}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

function NewNoteForm({
  resourceType,
  resourceId,
  onSuccess,
}: {
  resourceType: string;
  resourceId: string;
  onSuccess: () => void;
}) {
  const [content, setContent] = React.useState("");
  const [annotationType, setAnnotationType] = React.useState("note");
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const { trigger: createAnnotation } = useCreateAnnotation();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) return;

    setIsSubmitting(true);
    try {
      await createAnnotation({
        resource_type: resourceType,
        resource_id: resourceId,
        content: content.trim(),
        annotation_type: annotationType,
      });
      setContent("");
      toast.success("Note added");
      onSuccess();
    } catch (error) {
      toast.error("Failed to add note");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div className="flex items-center gap-2">
        <Select value={annotationType} onValueChange={setAnnotationType}>
          <SelectTrigger className="w-[120px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="note">Note</SelectItem>
            <SelectItem value="highlight">Highlight</SelectItem>
            <SelectItem value="question">Question</SelectItem>
            <SelectItem value="bookmark">Bookmark</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <Textarea
        placeholder="Add a note..."
        value={content}
        onChange={(e) => setContent(e.target.value)}
        rows={3}
        className="resize-none"
      />
      <Button type="submit" size="sm" disabled={isSubmitting || !content.trim()}>
        {isSubmitting ? (
          <Loader2 className="size-4 mr-1 animate-spin" />
        ) : (
          <Plus className="size-4 mr-1" />
        )}
        Add Note
      </Button>
    </form>
  );
}

export function NotesPanel({ className }: NotesPanelProps) {
  const {
    notesPanelOpen,
    setNotesPanelOpen,
    notesPanelContext,
  } = useLearningStore();

  const resourceType = notesPanelContext?.resourceType || "topic";
  const resourceId = notesPanelContext?.resourceId || "";

  const { data: annotations, mutate: mutateAnnotations } = useLearningAnnotations({
    resource_type: resourceType,
    resource_id: resourceId,
  });
  const { data: artifacts } = useLearningArtifacts({
    topic_id: resourceType === "topic" ? resourceId : undefined,
  });
  const { trigger: deleteAnnotation } = useDeleteAnnotation();

  const handleDeleteNote = async (annotationId: string) => {
    try {
      await deleteAnnotation({ id: annotationId });
      toast.success("Note deleted");
      mutateAnnotations();
    } catch (error) {
      toast.error("Failed to delete note");
    }
  };

  const notesList = annotations?.items || [];
  const artifactsList = artifacts?.items || [];

  return (
    <>
      {/* Toggle Button - Always visible when panel is closed */}
      {!notesPanelOpen && (
        <Button
          variant="outline"
          size="icon"
          className={cn(
            "fixed right-0 top-1/2 -translate-y-1/2 z-50 rounded-l-lg rounded-r-none h-16 w-8 border-r-0",
            className
          )}
          onClick={() => setNotesPanelOpen(true)}
        >
          <ChevronLeft className="size-4" />
        </Button>
      )}

      {/* Panel */}
      <Sheet open={notesPanelOpen} onOpenChange={setNotesPanelOpen}>
        <SheetContent side="right" className="w-[400px] sm:w-[450px] p-0">
          <SheetHeader className="p-4 border-b">
            <div className="flex items-center justify-between">
              <SheetTitle className="flex items-center gap-2">
                <StickyNote className="size-5" />
                Notes & Annotations
              </SheetTitle>
            </div>
            {notesPanelContext && (
              <p className="text-sm text-muted-foreground">
                {notesPanelContext.resourceName || "Current context"}
              </p>
            )}
          </SheetHeader>

          <Tabs defaultValue="notes" className="flex-1">
            <TabsList className="w-full grid grid-cols-3 rounded-none border-b">
              <TabsTrigger value="notes">
                <StickyNote className="size-4 mr-1" />
                Notes
              </TabsTrigger>
              <TabsTrigger value="annotations">
                <Highlighter className="size-4 mr-1" />
                Highlights
              </TabsTrigger>
              <TabsTrigger value="artifacts">
                <FileText className="size-4 mr-1" />
                Files
              </TabsTrigger>
            </TabsList>

            <TabsContent value="notes" className="mt-0 p-4">
              <ScrollArea className="h-[calc(100vh-220px)]">
                <div className="space-y-4">
                  {resourceId && (
                    <NewNoteForm
                      resourceType={resourceType}
                      resourceId={resourceId}
                      onSuccess={() => mutateAnnotations()}
                    />
                  )}

                  {notesList.length > 0 ? (
                    <div className="space-y-2">
                      {notesList
                        .filter((a: any) => a.annotation_type === "note")
                        .map((annotation: any) => (
                          <NoteItem
                            key={annotation.id}
                            annotation={annotation}
                            onDelete={() => handleDeleteNote(annotation.id)}
                          />
                        ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-muted-foreground">
                      <StickyNote className="size-8 mx-auto mb-2 opacity-50" />
                      <p className="text-sm">No notes yet</p>
                    </div>
                  )}
                </div>
              </ScrollArea>
            </TabsContent>

            <TabsContent value="annotations" className="mt-0 p-4">
              <ScrollArea className="h-[calc(100vh-220px)]">
                {notesList.filter((a: any) => a.annotation_type !== "note").length > 0 ? (
                  <div className="space-y-2">
                    {notesList
                      .filter((a: any) => a.annotation_type !== "note")
                      .map((annotation: any) => (
                        <NoteItem
                          key={annotation.id}
                          annotation={annotation}
                          onDelete={() => handleDeleteNote(annotation.id)}
                        />
                      ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    <Highlighter className="size-8 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">No highlights or bookmarks</p>
                  </div>
                )}
              </ScrollArea>
            </TabsContent>

            <TabsContent value="artifacts" className="mt-0 p-4">
              <ScrollArea className="h-[calc(100vh-220px)]">
                <div className="space-y-4">
                  <Button variant="outline" className="w-full">
                    <Upload className="size-4 mr-2" />
                    Upload File
                  </Button>

                  {artifactsList.length > 0 ? (
                    <div className="space-y-2">
                      {artifactsList.map((artifact: any) => (
                        <ArtifactItem key={artifact.id} artifact={artifact} />
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-muted-foreground">
                      <FileText className="size-8 mx-auto mb-2 opacity-50" />
                      <p className="text-sm">No files attached</p>
                    </div>
                  )}
                </div>
              </ScrollArea>
            </TabsContent>
          </Tabs>
        </SheetContent>
      </Sheet>
    </>
  );
}

export default NotesPanel;
