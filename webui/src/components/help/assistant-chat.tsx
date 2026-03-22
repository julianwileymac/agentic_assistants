"use client";

import * as React from "react";
import { usePathname } from "next/navigation";
import { Loader2, MessageSquare, SendHorizonal, BookOpen, Code2 } from "lucide-react";

import { apiFetch, useAssistantChat } from "@/lib/api";
import { useHelpStore } from "@/lib/store";
import type { AssistantChatMessage, AssistantModelCatalogEntry } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { cn } from "@/lib/utils";
import Link from "next/link";

type AssistantChatProps = {
  projectId?: string;
};

const PROVIDER_OPTIONS = [
  { value: "default", label: "Default" },
  { value: "ollama", label: "Ollama" },
  { value: "huggingface_local", label: "HF local" },
  { value: "openai_compatible", label: "OpenAI-compatible" },
];

export function AssistantChat({ projectId }: AssistantChatProps) {
  const pathname = usePathname();
  const { selectedDocSlug } = useHelpStore();
  const [messages, setMessages] = React.useState<AssistantChatMessage[]>([]);
  const [input, setInput] = React.useState("");
  const [includeCodeContext, setIncludeCodeContext] = React.useState(false);
  const [includeProjectDocs, setIncludeProjectDocs] = React.useState(false);
  const [providerOverride, setProviderOverride] = React.useState("default");
  const [modelOverride, setModelOverride] = React.useState("");
  const [modelCatalog, setModelCatalog] = React.useState<AssistantModelCatalogEntry[]>([]);
  const { trigger, isMutating } = useAssistantChat();
  const messagesEndRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  React.useEffect(() => {
    const loadCatalog = async () => {
      try {
        const data = await apiFetch<{ models: AssistantModelCatalogEntry[] }>("/api/v1/assistant/models/catalog");
        setModelCatalog(data.models || []);
      } catch {
        // ignore
      }
    };
    loadCatalog();
  }, []);

  const availableModels = React.useMemo(() => {
    const selectedProvider = providerOverride === "default" ? null : providerOverride;
    const names = modelCatalog
      .filter((entry) => (selectedProvider ? entry.provider === selectedProvider : true))
      .map((entry) => entry.model)
      .filter(Boolean);
    const deduped = Array.from(new Set(names));
    if (modelOverride && !deduped.includes(modelOverride)) {
      deduped.unshift(modelOverride);
    }
    return deduped;
  }, [modelCatalog, modelOverride, providerOverride]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: AssistantChatMessage = { role: "user", content: input.trim() };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    try {
      const response = await trigger({
        messages: [...messages, userMessage],
        route: pathname,
        project_id: projectId,
        selected_doc_slug: selectedDocSlug || undefined,
        include_code_context: includeCodeContext,
        include_project_docs: includeProjectDocs,
        context_task: includeCodeContext ? "understand" : undefined,
        provider: providerOverride !== "default" ? (providerOverride as "ollama" | "huggingface_local" | "openai_compatible") : undefined,
        model: modelOverride || undefined,
      });
      if (response?.message) {
        setMessages((prev) => [...prev, response.message]);
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, I ran into an issue with the selected assistant provider/model." },
      ]);
    }
  };

  return (
    <div className="flex h-full flex-col rounded-lg border bg-background">
      <div className="flex items-center justify-between border-b px-3 py-2">
        <div className="flex items-center gap-2">
          <MessageSquare className="size-4" />
          <span className="text-sm font-medium">Framework Assistant</span>
        </div>
        {selectedDocSlug ? (
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <BookOpen className="size-3.5" />
            <span className="truncate max-w-[180px]">
              Using doc: <span className="font-medium text-foreground">{selectedDocSlug}</span>
            </span>
          </div>
        ) : (
          <span className="text-xs text-muted-foreground">Tip: pick a doc for better answers.</span>
        )}
      </div>

      <ScrollArea className="flex-1 px-3 py-3">
        <div className="space-y-3">
          {messages.length === 0 && (
            <div className="text-sm text-muted-foreground">
              Ask how to use the control panel, deploy models, or wire agents. I can pull in docs
              for more specific help.
            </div>
          )}
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={cn(
                "rounded-lg px-3 py-2 text-sm",
                msg.role === "user" ? "bg-primary/10 text-foreground ml-auto max-w-[85%]" : "bg-muted text-foreground max-w-[95%]"
              )}
            >
              {msg.content}
            </div>
          ))}
          {isMutating && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Loader2 className="size-4 animate-spin" />
              Thinking...
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      <div className="border-t px-3 py-2">
        <div className="flex items-center justify-between text-[11px] text-muted-foreground mb-2">
          <div className="flex items-center gap-3">
            <label className="flex items-center gap-2">
              <Switch checked={includeCodeContext} onCheckedChange={setIncludeCodeContext} />
              <span className="flex items-center gap-1">
                <Code2 className="size-3" />
                Code context
              </span>
            </label>
            <label className="flex items-center gap-2">
              <Switch checked={includeProjectDocs} onCheckedChange={setIncludeProjectDocs} />
              <span>Project docs</span>
            </label>
            <Select value={providerOverride} onValueChange={setProviderOverride}>
              <SelectTrigger className="h-7 w-[140px] text-[11px]">
                <SelectValue placeholder="Provider" />
              </SelectTrigger>
              <SelectContent>
                {PROVIDER_OPTIONS.map((provider) => (
                  <SelectItem key={provider.value} value={provider.value}>
                    {provider.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select
              value={modelOverride || "__assistant_default__"}
              onValueChange={(value) => setModelOverride(value === "__assistant_default__" ? "" : value)}
            >
              <SelectTrigger className="h-7 w-[170px] text-[11px]">
                <SelectValue placeholder="Model override" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="__assistant_default__">Default model</SelectItem>
                {availableModels.map((model) => (
                  <SelectItem key={model} value={model}>
                    {model}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <Link href="/agents" className="text-xs text-primary hover:underline">
            Open Agent UI
          </Link>
        </div>
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about the framework, docs, or how to build..."
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
              }
            }}
            disabled={isMutating}
          />
          <Button onClick={sendMessage} disabled={isMutating || !input.trim()}>
            {isMutating ? <Loader2 className="size-4 animate-spin" /> : <SendHorizonal className="size-4" />}
          </Button>
        </div>
      </div>
    </div>
  );
}

