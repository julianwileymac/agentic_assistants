"use client";

import * as React from "react";
import { BookOpen, Loader2, Search } from "lucide-react";
import { useDocsList, useDoc } from "@/lib/api";
import { useHelpStore } from "@/lib/store";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";

export function DocsBrowser() {
  const { data: docs, isLoading } = useDocsList();
  const { selectedDocSlug, setSelectedDoc } = useHelpStore();
  const { data: docContent, isLoading: isDocLoading } = useDoc(selectedDocSlug);
  const [filter, setFilter] = React.useState("");

  React.useEffect(() => {
    if (!selectedDocSlug && docs && docs.length > 0) {
      setSelectedDoc(docs[0].slug);
    }
  }, [docs, selectedDocSlug, setSelectedDoc]);

  const filteredDocs = React.useMemo(() => {
    if (!docs) return [];
    if (!filter.trim()) return docs;
    const term = filter.toLowerCase();
    return docs.filter(
      (doc) =>
        doc.title.toLowerCase().includes(term) ||
        doc.slug.toLowerCase().includes(term)
    );
  }, [docs, filter]);

  return (
    <div className="flex h-full flex-col gap-3">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
        <Input
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          placeholder="Search docs..."
          className="pl-9"
        />
      </div>

      <div className="grid grid-cols-[220px_1fr] gap-3 h-full min-h-[320px]">
        <ScrollArea className="border rounded-lg bg-muted/30">
          <div className="flex flex-col">
            {isLoading && (
              <div className="flex items-center gap-2 p-3 text-sm text-muted-foreground">
                <Loader2 className="size-4 animate-spin" />
                Loading docs...
              </div>
            )}
            {!isLoading && filteredDocs.length === 0 && (
              <p className="p-3 text-sm text-muted-foreground">No docs found.</p>
            )}
            {filteredDocs.map((doc) => {
              const isActive = doc.slug === selectedDocSlug;
              return (
                <Button
                  key={doc.slug}
                  variant={isActive ? "secondary" : "ghost"}
                  className={cn(
                    "justify-start w-full px-3 py-2 rounded-none first:rounded-t-lg last:rounded-b-lg",
                    isActive && "font-medium"
                  )}
                  onClick={() => setSelectedDoc(doc.slug)}
                >
                  <BookOpen className="size-4 mr-2" />
                  <span className="truncate">{doc.title}</span>
                </Button>
              );
            })}
          </div>
        </ScrollArea>

        <div className="border rounded-lg bg-muted/20 p-3 overflow-hidden">
          {isDocLoading && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="size-4 animate-spin" />
              Loading content...
            </div>
          )}
          {!isDocLoading && docContent ? (
            <ScrollArea className="h-full">
              <div className="prose prose-sm dark:prose-invert max-w-none whitespace-pre-wrap">
                <h4 className="font-semibold mb-2">{docContent.title}</h4>
                <p className="text-xs text-muted-foreground mb-4">{docContent.slug}.md</p>
                <div className="text-sm leading-6">{docContent.content}</div>
              </div>
            </ScrollArea>
          ) : null}
          {!isDocLoading && !docContent && (
            <div className="text-sm text-muted-foreground">
              Select a document to view its contents.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

