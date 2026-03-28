"use client";

import * as React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import {
  MessageSquare,
  Send,
  Bot,
  User,
  Sparkles,
  Loader2,
  X,
  Plus,
} from "lucide-react";

import {
  useCopilotChat,
  useCopilotContextValues,
  type CopilotMessage,
  type StructuredBlock,
} from "./CopilotProvider";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Card } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

// ---------------------------------------------------------------------------
// Quick actions the user can fire with a single click
// ---------------------------------------------------------------------------

const QUICK_ACTIONS = [
  { label: "Run Pipeline", prompt: "Run the current pipeline and show me the status." },
  { label: "Deploy Model", prompt: "Deploy the latest trained model to production." },
  { label: "Check Health", prompt: "Check the system health and report any issues." },
] as const;

// ---------------------------------------------------------------------------
// Main chat widget
// ---------------------------------------------------------------------------

interface CopilotChatProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function CopilotChat({ open, onOpenChange }: CopilotChatProps) {
  const {
    messages,
    input,
    isLoading,
    setInput,
    sendMessage,
    clearMessages,
  } = useCopilotChat();
  const { readableContexts, currentPage } = useCopilotContextValues();
  const scrollRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage();
  };

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent
        side="right"
        className="flex w-full flex-col gap-0 p-0 sm:max-w-lg"
      >
        {/* ---- Header ---- */}
        <SheetHeader className="border-b px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="size-5 text-primary" />
              <SheetTitle className="text-base">AI Copilot</SheetTitle>
              <Badge variant="secondary" className="text-[10px]">
                beta
              </Badge>
            </div>
            <div className="flex items-center gap-1">
              <Button
                variant="ghost"
                size="icon"
                className="size-7"
                onClick={clearMessages}
                title="New conversation"
              >
                <Plus className="size-3.5" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="size-7"
                onClick={() => onOpenChange(false)}
              >
                <X className="size-3.5" />
              </Button>
            </div>
          </div>
          <SheetDescription className="sr-only">
            Chat with the AI copilot assistant
          </SheetDescription>
        </SheetHeader>

        {/* ---- Context bar ---- */}
        <div className="flex flex-wrap items-center gap-1.5 border-b px-4 py-2 text-[11px] text-muted-foreground">
          <span className="font-medium">Context:</span>
          <Badge variant="outline" className="text-[10px]">
            {currentPage}
          </Badge>
          {readableContexts.slice(0, 4).map((c) => (
            <Badge key={c.key} variant="outline" className="text-[10px]">
              {c.description ?? c.key}
            </Badge>
          ))}
          {readableContexts.length > 4 && (
            <Badge variant="outline" className="text-[10px]">
              +{readableContexts.length - 4} more
            </Badge>
          )}
        </div>

        {/* ---- Messages ---- */}
        <ScrollArea className="flex-1">
          <div className="flex flex-col gap-4 px-4 py-4">
            {messages.length === 0 && <EmptyState onAction={sendMessage} />}

            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}

            {isLoading && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="size-4 animate-spin" />
                Thinking…
              </div>
            )}

            <div ref={scrollRef} />
          </div>
        </ScrollArea>

        {/* ---- Quick actions ---- */}
        <div className="flex gap-1.5 overflow-x-auto border-t px-4 py-2">
          {QUICK_ACTIONS.map((qa) => (
            <Button
              key={qa.label}
              variant="outline"
              size="sm"
              className="shrink-0 text-xs"
              disabled={isLoading}
              onClick={() => sendMessage(qa.prompt)}
            >
              {qa.label}
            </Button>
          ))}
        </div>

        {/* ---- Input ---- */}
        <form
          onSubmit={handleSubmit}
          className="flex items-center gap-2 border-t px-4 py-3"
        >
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask anything about your workspace…"
            disabled={isLoading}
            className="flex-1"
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
              }
            }}
          />
          <Button
            type="submit"
            size="icon"
            disabled={isLoading || !input.trim()}
          >
            {isLoading ? (
              <Loader2 className="size-4 animate-spin" />
            ) : (
              <Send className="size-4" />
            )}
          </Button>
        </form>
      </SheetContent>
    </Sheet>
  );
}

// ---------------------------------------------------------------------------
// Trigger button (FAB-style)
// ---------------------------------------------------------------------------

interface CopilotTriggerProps {
  onClick: () => void;
}

export function CopilotTrigger({ onClick }: CopilotTriggerProps) {
  return (
    <Button
      onClick={onClick}
      size="icon"
      className="fixed bottom-6 right-6 z-50 size-12 rounded-full shadow-lg"
    >
      <MessageSquare className="size-5" />
    </Button>
  );
}

// ---------------------------------------------------------------------------
// Empty state
// ---------------------------------------------------------------------------

function EmptyState({ onAction }: { onAction: (content: string) => void }) {
  return (
    <div className="flex flex-col items-center gap-4 py-12 text-center">
      <div className="flex size-14 items-center justify-center rounded-full bg-primary/10">
        <Sparkles className="size-7 text-primary" />
      </div>
      <div>
        <p className="font-medium">AI Copilot</p>
        <p className="mt-1 text-sm text-muted-foreground">
          Ask me about your pipelines, models, agents, or anything in your
          workspace.
        </p>
      </div>
      <div className="flex flex-wrap justify-center gap-2">
        {QUICK_ACTIONS.map((qa) => (
          <Button
            key={qa.label}
            variant="outline"
            size="sm"
            className="text-xs"
            onClick={() => onAction(qa.prompt)}
          >
            {qa.label}
          </Button>
        ))}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Individual message bubble
// ---------------------------------------------------------------------------

function MessageBubble({ message }: { message: CopilotMessage }) {
  const isUser = message.role === "user";

  return (
    <div className={cn("flex gap-3", isUser && "flex-row-reverse")}>
      <Avatar className="mt-0.5 size-7 shrink-0">
        <AvatarFallback
          className={cn(
            "text-xs",
            isUser
              ? "bg-primary text-primary-foreground"
              : "bg-muted text-muted-foreground",
          )}
        >
          {isUser ? <User className="size-3.5" /> : <Bot className="size-3.5" />}
        </AvatarFallback>
      </Avatar>

      <div
        className={cn(
          "max-w-[85%] rounded-lg px-3 py-2 text-sm",
          isUser
            ? "bg-primary text-primary-foreground"
            : "bg-muted text-foreground",
        )}
      >
        {message.content ? (
          isUser ? (
            <p className="whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className="prose prose-sm dark:prose-invert max-w-none [&_pre]:overflow-x-auto [&_pre]:rounded [&_pre]:bg-background/50 [&_pre]:p-2 [&_code]:rounded [&_code]:bg-background/50 [&_code]:px-1 [&_code]:text-xs">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content}
              </ReactMarkdown>
            </div>
          )
        ) : (
          <Skeleton className="h-4 w-32" />
        )}

        {message.structuredData && (
          <StructuredRenderer block={message.structuredData} />
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Generative UI — structured block renderer
// ---------------------------------------------------------------------------

function StructuredRenderer({ block }: { block: StructuredBlock }) {
  switch (block.type) {
    case "chart":
      return <ChartBlock block={block} />;
    case "table":
      return <TableBlock block={block} />;
    case "code":
      return <CodeBlock block={block} />;
    default:
      return null;
  }
}

function ChartBlock({ block }: { block: StructuredBlock }) {
  const data = block.chartData ?? [];
  if (data.length === 0) return null;

  return (
    <Card className="mt-3 p-3">
      {block.title && (
        <p className="mb-2 text-xs font-medium">{block.title}</p>
      )}
      <ResponsiveContainer width="100%" height={180}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
          <XAxis
            dataKey="name"
            tick={{ fontSize: 10 }}
            className="fill-muted-foreground"
          />
          <YAxis tick={{ fontSize: 10 }} className="fill-muted-foreground" />
          <Tooltip
            contentStyle={{
              backgroundColor: "hsl(var(--popover))",
              border: "1px solid hsl(var(--border))",
              borderRadius: 6,
              fontSize: 12,
            }}
          />
          <Bar
            dataKey="value"
            fill="hsl(var(--primary))"
            radius={[4, 4, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );
}

function TableBlock({ block }: { block: StructuredBlock }) {
  const columns = block.columns ?? [];
  const rows = block.rows ?? [];
  if (columns.length === 0) return null;

  return (
    <Card className="mt-3 overflow-hidden">
      {block.title && (
        <p className="px-3 pt-3 text-xs font-medium">{block.title}</p>
      )}
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b bg-muted/50">
              {columns.map((col) => (
                <th
                  key={col}
                  className="px-3 py-2 text-left font-medium text-muted-foreground"
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr key={i} className="border-b last:border-0">
                {columns.map((col) => (
                  <td key={col} className="px-3 py-1.5">
                    {String(row[col] ?? "")}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}

function CodeBlock({ block }: { block: StructuredBlock }) {
  const code = block.code ?? "";
  if (!code) return null;

  return (
    <Card className="mt-3 overflow-hidden">
      {block.title && (
        <div className="flex items-center justify-between border-b px-3 py-1.5">
          <p className="text-xs font-medium">{block.title}</p>
          {block.language && (
            <Badge variant="secondary" className="text-[10px]">
              {block.language}
            </Badge>
          )}
        </div>
      )}
      <pre className="overflow-x-auto p-3 text-xs leading-relaxed">
        <code>{code}</code>
      </pre>
    </Card>
  );
}
