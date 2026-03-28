"use client";

import * as React from "react";
import Link from "next/link";
import { useSearchParams, useRouter } from "next/navigation";
import {
  BookOpen,
  Search,
  Loader2,
  ChevronRight,
  Clock,
  FileText,
  Hash,
  ArrowLeft,
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";
import { getBackendUrl } from "@/lib/api-client";

const API_BASE = getBackendUrl() + "/api/v1";

interface DocEntry {
  slug: string;
  title: string;
  path: string;
  description: string;
}

interface DocContent {
  slug: string;
  title: string;
  content: string;
  headings: string[];
  word_count: number;
}

interface SearchResult {
  slug: string;
  title: string;
  snippet: string;
  match_count: number;
}

function useDocsList() {
  const [data, setData] = React.useState<DocEntry[] | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    fetch(`${API_BASE}/docs`)
      .then((res) => res.json())
      .then((data) => {
        setData(data);
        setIsLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setIsLoading(false);
      });
  }, []);

  return { data, isLoading, error };
}

function useDocContent(slug: string | null) {
  const [data, setData] = React.useState<DocContent | null>(null);
  const [isLoading, setIsLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (!slug) {
      setData(null);
      return;
    }

    setIsLoading(true);
    fetch(`${API_BASE}/docs/${slug}`)
      .then((res) => res.json())
      .then((data) => {
        setData(data);
        setIsLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setIsLoading(false);
      });
  }, [slug]);

  return { data, isLoading, error };
}

function useDocSearch(query: string) {
  const [data, setData] = React.useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = React.useState(false);

  React.useEffect(() => {
    if (!query || query.length < 2) {
      setData([]);
      return;
    }

    setIsLoading(true);
    const timer = setTimeout(() => {
      fetch(`${API_BASE}/docs/search?q=${encodeURIComponent(query)}`)
        .then((res) => res.json())
        .then((res) => {
          setData(res.results || []);
          setIsLoading(false);
        })
        .catch(() => {
          setData([]);
          setIsLoading(false);
        });
    }, 300);

    return () => clearTimeout(timer);
  }, [query]);

  return { data, isLoading };
}

function TableOfContents({
  headings,
  activeHeading,
}: {
  headings: string[];
  activeHeading: string;
}) {
  if (headings.length === 0) return null;

  return (
    <div className="space-y-2">
      <p className="text-sm font-semibold text-muted-foreground mb-3">On this page</p>
      <nav className="space-y-1">
        {headings.map((heading, idx) => {
          const id = heading.toLowerCase().replace(/\s+/g, "-");
          const isActive = activeHeading === id;
          return (
            <a
              key={idx}
              href={`#${id}`}
              className={cn(
                "block text-sm py-1 px-2 rounded-md transition-colors",
                isActive
                  ? "bg-primary/10 text-primary font-medium"
                  : "text-muted-foreground hover:text-foreground hover:bg-muted"
              )}
            >
              {heading}
            </a>
          );
        })}
      </nav>
    </div>
  );
}

function MarkdownRenderer({ content }: { content: string }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        h1: ({ children }) => {
          const id = String(children).toLowerCase().replace(/\s+/g, "-");
          return (
            <h1 id={id} className="scroll-mt-20 text-3xl font-bold mt-8 mb-4 first:mt-0">
              {children}
            </h1>
          );
        },
        h2: ({ children }) => {
          const id = String(children).toLowerCase().replace(/\s+/g, "-");
          return (
            <h2 id={id} className="scroll-mt-20 text-2xl font-semibold mt-8 mb-3 pb-2 border-b">
              {children}
            </h2>
          );
        },
        h3: ({ children }) => {
          const id = String(children).toLowerCase().replace(/\s+/g, "-");
          return (
            <h3 id={id} className="scroll-mt-20 text-xl font-semibold mt-6 mb-2">
              {children}
            </h3>
          );
        },
        h4: ({ children }) => {
          const id = String(children).toLowerCase().replace(/\s+/g, "-");
          return (
            <h4 id={id} className="scroll-mt-20 text-lg font-semibold mt-4 mb-2">
              {children}
            </h4>
          );
        },
        p: ({ children }) => <p className="mb-4 leading-7">{children}</p>,
        ul: ({ children }) => <ul className="mb-4 ml-6 list-disc space-y-2">{children}</ul>,
        ol: ({ children }) => <ol className="mb-4 ml-6 list-decimal space-y-2">{children}</ol>,
        li: ({ children }) => <li className="leading-7">{children}</li>,
        a: ({ href, children }) => (
          <a
            href={href}
            className="text-primary underline underline-offset-4 hover:text-primary/80"
            target={href?.startsWith("http") ? "_blank" : undefined}
            rel={href?.startsWith("http") ? "noopener noreferrer" : undefined}
          >
            {children}
          </a>
        ),
        code: ({ className, children, ...props }) => {
          const isInline = !className;
          if (isInline) {
            return (
              <code className="px-1.5 py-0.5 rounded bg-muted font-mono text-sm" {...props}>
                {children}
              </code>
            );
          }
          return (
            <code
              className={cn("block overflow-x-auto", className)}
              {...props}
            >
              {children}
            </code>
          );
        },
        pre: ({ children }) => (
          <pre className="mb-4 rounded-lg border bg-muted/50 p-4 overflow-x-auto font-mono text-sm">
            {children}
          </pre>
        ),
        blockquote: ({ children }) => (
          <blockquote className="mb-4 border-l-4 border-primary/30 pl-4 italic text-muted-foreground">
            {children}
          </blockquote>
        ),
        table: ({ children }) => (
          <div className="mb-4 overflow-x-auto">
            <table className="w-full border-collapse border">{children}</table>
          </div>
        ),
        th: ({ children }) => (
          <th className="border bg-muted px-4 py-2 text-left font-semibold">{children}</th>
        ),
        td: ({ children }) => <td className="border px-4 py-2">{children}</td>,
        hr: () => <hr className="my-8 border-t" />,
      }}
    >
      {content}
    </ReactMarkdown>
  );
}

function DocSidebar({
  docs,
  selectedSlug,
  onSelect,
  searchQuery,
  onSearchChange,
  searchResults,
  isSearching,
}: {
  docs: DocEntry[];
  selectedSlug: string | null;
  onSelect: (slug: string) => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  searchResults: SearchResult[];
  isSearching: boolean;
}) {
  const showSearchResults = searchQuery.length >= 2;

  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
          <Input
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search documentation..."
            className="pl-9"
          />
        </div>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-4">
          {showSearchResults ? (
            <div className="space-y-2">
              <p className="text-xs text-muted-foreground mb-3">
                {isSearching ? "Searching..." : `${searchResults.length} results`}
              </p>
              {searchResults.map((result) => (
                <button
                  key={result.slug}
                  onClick={() => {
                    onSelect(result.slug);
                    onSearchChange("");
                  }}
                  className="w-full text-left p-3 rounded-lg border bg-card hover:bg-muted/50 transition-colors"
                >
                  <div className="flex items-center gap-2 mb-1">
                    <FileText className="size-4 text-primary" />
                    <span className="font-medium text-sm">{result.title}</span>
                    <Badge variant="secondary" className="text-xs ml-auto">
                      {result.match_count}
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground line-clamp-2">{result.snippet}</p>
                </button>
              ))}
              {!isSearching && searchResults.length === 0 && (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No results found for &quot;{searchQuery}&quot;
                </p>
              )}
            </div>
          ) : (
            <div className="space-y-1">
              {docs.map((doc) => {
                const isActive = doc.slug === selectedSlug;
                return (
                  <button
                    key={doc.slug}
                    onClick={() => onSelect(doc.slug)}
                    className={cn(
                      "w-full text-left px-3 py-2 rounded-lg transition-colors flex items-center gap-2",
                      isActive
                        ? "bg-primary/10 text-primary font-medium"
                        : "hover:bg-muted text-foreground"
                    )}
                  >
                    <BookOpen className="size-4 shrink-0" />
                    <span className="truncate">{doc.title}</span>
                    {isActive && <ChevronRight className="size-4 ml-auto shrink-0" />}
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </ScrollArea>
    </div>
  );
}

export default function DocsPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const initialSlug = searchParams.get("doc");

  const { data: docs, isLoading: isDocsLoading } = useDocsList();
  const [selectedSlug, setSelectedSlug] = React.useState<string | null>(initialSlug);
  const [searchQuery, setSearchQuery] = React.useState("");
  const [activeHeading, setActiveHeading] = React.useState("");

  const { data: docContent, isLoading: isContentLoading } = useDocContent(selectedSlug);
  const { data: searchResults, isLoading: isSearching } = useDocSearch(searchQuery);

  // Set default doc when docs load
  React.useEffect(() => {
    if (docs && docs.length > 0 && !selectedSlug) {
      // Try to find "index" or use first doc
      const indexDoc = docs.find((d) => d.slug === "index");
      setSelectedSlug(indexDoc?.slug || docs[0].slug);
    }
  }, [docs, selectedSlug]);

  // Update URL when doc changes
  React.useEffect(() => {
    if (selectedSlug) {
      router.replace(`/docs?doc=${selectedSlug}`, { scroll: false });
    }
  }, [selectedSlug, router]);

  // Track active heading for TOC
  React.useEffect(() => {
    if (!docContent?.headings.length) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveHeading(entry.target.id);
          }
        });
      },
      { rootMargin: "-20% 0px -80% 0px" }
    );

    docContent.headings.forEach((heading) => {
      const id = heading.toLowerCase().replace(/\s+/g, "-");
      const element = document.getElementById(id);
      if (element) observer.observe(element);
    });

    return () => observer.disconnect();
  }, [docContent?.headings]);

  const readingTime = docContent ? Math.ceil(docContent.word_count / 200) : 0;

  if (isDocsLoading) {
    return (
      <div className="flex h-[calc(100vh-4rem)]">
        <div className="w-72 border-r">
          <div className="p-4 space-y-2">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-8 w-full" />
            <Skeleton className="h-8 w-full" />
            <Skeleton className="h-8 w-full" />
          </div>
        </div>
        <div className="flex-1 p-8">
          <Skeleton className="h-10 w-1/2 mb-4" />
          <Skeleton className="h-4 w-full mb-2" />
          <Skeleton className="h-4 w-full mb-2" />
          <Skeleton className="h-4 w-3/4" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] -m-6">
      {/* Sidebar */}
      <div className="w-72 border-r bg-muted/30 shrink-0">
        <DocSidebar
          docs={docs || []}
          selectedSlug={selectedSlug}
          onSelect={setSelectedSlug}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          searchResults={searchResults}
          isSearching={isSearching}
        />
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        {isContentLoading ? (
          <div className="p-8">
            <Skeleton className="h-10 w-1/2 mb-4" />
            <Skeleton className="h-4 w-full mb-2" />
            <Skeleton className="h-4 w-full mb-2" />
            <Skeleton className="h-4 w-3/4" />
          </div>
        ) : docContent ? (
          <div className="flex h-full">
            <ScrollArea className="flex-1">
              <article className="max-w-4xl mx-auto p-8">
                {/* Header */}
                <div className="mb-8">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
                    <Link href="/" className="hover:text-foreground">
                      Home
                    </Link>
                    <ChevronRight className="size-4" />
                    <span>Docs</span>
                    <ChevronRight className="size-4" />
                    <span className="text-foreground">{docContent.title}</span>
                  </div>
                  <h1 className="text-4xl font-bold tracking-tight mb-3">{docContent.title}</h1>
                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Clock className="size-4" />
                      {readingTime} min read
                    </span>
                    <span className="flex items-center gap-1">
                      <FileText className="size-4" />
                      {docContent.word_count.toLocaleString()} words
                    </span>
                  </div>
                </div>

                <Separator className="mb-8" />

                {/* Content */}
                <div className="prose prose-slate dark:prose-invert max-w-none">
                  <MarkdownRenderer content={docContent.content} />
                </div>

                {/* Footer Navigation */}
                <div className="mt-12 pt-8 border-t">
                  <div className="flex items-center justify-between">
                    <Button variant="ghost" asChild>
                      <Link href="/">
                        <ArrowLeft className="size-4 mr-2" />
                        Back to Home
                      </Link>
                    </Button>
                  </div>
                </div>
              </article>
            </ScrollArea>

            {/* Table of Contents */}
            {docContent.headings.length > 2 && (
              <div className="w-64 border-l p-6 shrink-0 hidden xl:block">
                <div className="sticky top-6">
                  <TableOfContents
                    headings={docContent.headings.slice(1)} // Skip first heading (title)
                    activeHeading={activeHeading}
                  />
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <BookOpen className="size-12 mx-auto mb-4 text-muted-foreground" />
              <p className="text-muted-foreground">Select a document to view</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
