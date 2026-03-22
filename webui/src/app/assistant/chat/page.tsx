"use client";

import * as React from "react";
import { usePathname } from "next/navigation";
import {
  Bot,
  Loader2,
  MessageSquare,
  SendHorizonal,
  BookOpen,
  Settings,
  Trash2,
  Sparkles,
  Code2,
} from "lucide-react";

import { useAssistantChat } from "@/lib/api";
import { useHelpStore } from "@/lib/store";
import type { AssistantChatMessage } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { apiFetch } from "@/lib/api";
import type { AssistantModelCatalogEntry } from "@/lib/types";
import { cn } from "@/lib/utils";
import Link from "next/link";

// Available documentation slugs
const DOC_SLUGS = [
  { value: "none", label: "No documentation context" },
  { value: "configuration", label: "Configuration Guide" },
  { value: "adapters", label: "Framework Adapters" },
  { value: "framework_assistant", label: "Framework Assistant" },
  { value: "ollama_finetuning", label: "Ollama Fine-tuning" },
  { value: "usage_analytics", label: "Usage Analytics" },
];

const CONTEXT_TASKS = [
  { value: "understand", label: "Understand codebase" },
  { value: "add_adapter", label: "Add adapter" },
  { value: "add_cli_command", label: "Add CLI command" },
  { value: "add_config", label: "Add config" },
  { value: "debug", label: "Debug issue" },
];

const PROVIDER_OPTIONS = [
  { value: "default", label: "Default provider" },
  { value: "ollama", label: "Ollama" },
  { value: "huggingface_local", label: "HF local" },
  { value: "openai_compatible", label: "OpenAI-compatible" },
];

export default function AssistantChatPage() {
  const pathname = usePathname();
  const { selectedDocSlug, setSelectedDoc } = useHelpStore();
  const [messages, setMessages] = React.useState<AssistantChatMessage[]>([]);
  const [input, setInput] = React.useState("");
  const [includeCodeContext, setIncludeCodeContext] = React.useState(false);
  const [includeProjectDocs, setIncludeProjectDocs] = React.useState(false);
  const [contextTask, setContextTask] = React.useState("understand");
  const [providerOverride, setProviderOverride] = React.useState("default");
  const [modelOverride, setModelOverride] = React.useState("");
  const [endpointOverride, setEndpointOverride] = React.useState("");
  const [modelCatalog, setModelCatalog] = React.useState<AssistantModelCatalogEntry[]>([]);
  const { trigger, isMutating } = useAssistantChat();
  const messagesEndRef = React.useRef<HTMLDivElement>(null);
  const textareaRef = React.useRef<HTMLTextAreaElement>(null);

  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  React.useEffect(() => {
    const loadAssistantMeta = async () => {
      try {
        const [config, catalog] = await Promise.all([
          apiFetch<{ provider?: string; model?: string; endpoint?: string }>("/api/v1/assistant/config"),
          apiFetch<{ models: AssistantModelCatalogEntry[] }>("/api/v1/assistant/models/catalog"),
        ]);
        setProviderOverride("default");
        setModelOverride(config.model || "");
        setEndpointOverride(config.endpoint || "");
        setModelCatalog(catalog.models || []);
      } catch {
        // non-blocking for chat UX
      }
    };
    loadAssistantMeta();
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
    if (!input.trim() || isMutating) return;

    const userMessage: AssistantChatMessage = { role: "user", content: input.trim() };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    try {
      const response = await trigger({
        messages: [...messages, userMessage],
        route: pathname,
        selected_doc_slug: selectedDocSlug || undefined,
        include_code_context: includeCodeContext,
        include_project_docs: includeProjectDocs,
        context_task: includeCodeContext ? contextTask : undefined,
        provider: providerOverride !== "default" ? (providerOverride as "ollama" | "huggingface_local" | "openai_compatible") : undefined,
        model: modelOverride || undefined,
        endpoint: endpointOverride || undefined,
      });
      if (response?.message) {
        setMessages((prev) => [...prev, response.message]);
      }
    } catch (error: unknown) {
      let errorMessage = "The assistant request failed.";
      const detail = error instanceof Error ? error.message : String(error || "");
      if (detail.toLowerCase().includes("timeout")) {
        errorMessage = "The request timed out. Try again or use a smaller model.";
      } else if (detail.includes("503") || detail.includes("502")) {
        errorMessage = "The selected provider endpoint is unavailable.";
      } else if (detail) {
        errorMessage = `Assistant error: ${detail}`;
      }
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: errorMessage },
      ]);
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex h-[calc(100vh-4rem)] flex-col">
      {/* Header */}
      <div className="flex items-center justify-between border-b px-6 py-4">
        <div className="flex items-center gap-4">
          <div className="p-3 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 text-white">
            <Bot className="size-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Framework Assistant</h1>
            <p className="text-sm text-muted-foreground">
              Ask questions about the framework, agents, and configuration
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <div className="flex items-center gap-2 rounded-md border px-3 py-2 text-xs text-muted-foreground">
            <Switch checked={includeCodeContext} onCheckedChange={setIncludeCodeContext} />
            <span className="flex items-center gap-1">
              <Code2 className="size-3.5" />
              Code context
            </span>
          </div>
          <div className="flex items-center gap-2 rounded-md border px-3 py-2 text-xs text-muted-foreground">
            <Switch checked={includeProjectDocs} onCheckedChange={setIncludeProjectDocs} />
            <span>Project docs</span>
          </div>
          <Select
            value={selectedDocSlug || "none"}
            onValueChange={(value) => setSelectedDoc(value === "none" ? null : value)}
          >
            <SelectTrigger className="w-[220px]">
              <BookOpen className="size-4 mr-2" />
              <SelectValue placeholder="Select documentation" />
            </SelectTrigger>
            <SelectContent>
              {DOC_SLUGS.map((doc) => (
                <SelectItem key={doc.value} value={doc.value}>
                  {doc.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {includeCodeContext && (
            <Select value={contextTask} onValueChange={setContextTask}>
              <SelectTrigger className="w-[200px]">
                <SelectValue placeholder="Context task" />
              </SelectTrigger>
              <SelectContent>
                {CONTEXT_TASKS.map((task) => (
                  <SelectItem key={task.value} value={task.value}>
                    {task.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
          <Select value={providerOverride} onValueChange={setProviderOverride}>
            <SelectTrigger className="w-[190px]">
              <SelectValue placeholder="Provider override" />
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
            <SelectTrigger className="w-[220px]">
              <SelectValue placeholder="Model override" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="__assistant_default__">Assistant default model</SelectItem>
              {availableModels.map((model) => (
                <SelectItem key={model} value={model}>
                  {model}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {(providerOverride === "ollama" || providerOverride === "openai_compatible") && (
            <Input
              className="w-[220px]"
              placeholder={providerOverride === "ollama" ? "Endpoint (optional)" : "Endpoint / base URL (optional)"}
              value={endpointOverride}
              onChange={(e) => setEndpointOverride(e.target.value)}
            />
          )}
          <Button variant="outline" size="icon" onClick={clearChat} title="Clear chat">
            <Trash2 className="size-4" />
          </Button>
          <Link href="/assistant">
            <Button variant="outline" size="icon" title="Settings">
              <Settings className="size-4" />
            </Button>
          </Link>
          <Link href="/agents">
            <Button variant="outline" size="icon" title="Open Agent UI">
              <MessageSquare className="size-4" />
            </Button>
          </Link>
        </div>
      </div>

      {/* Chat Area */}
      <ScrollArea className="flex-1 px-6 py-4">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.length === 0 && (
            <Card className="border-dashed">
              <CardContent className="pt-6">
                <div className="text-center space-y-4">
                  <div className="mx-auto p-4 rounded-full bg-violet-500/10 w-fit">
                    <Sparkles className="size-8 text-violet-500" />
                  </div>
                  <div className="space-y-2">
                    <h3 className="text-lg font-semibold">Welcome to the Framework Assistant</h3>
                    <p className="text-muted-foreground max-w-md mx-auto">
                      I can help you understand how to use the Control Panel, configure agents, 
                      set up pipelines, and work with different frameworks like CrewAI, LangGraph, and more.
                    </p>
                  </div>
                  <div className="flex flex-wrap justify-center gap-2 pt-2">
                    {[
                      "How do I create a new project?",
                      "What frameworks are supported?",
                      "How do I configure Ollama?",
                      "Explain agent adapters",
                    ].map((suggestion) => (
                      <Button
                        key={suggestion}
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setInput(suggestion);
                          textareaRef.current?.focus();
                        }}
                      >
                        {suggestion}
                      </Button>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={cn(
                "flex gap-3",
                msg.role === "user" ? "justify-end" : "justify-start"
              )}
            >
              {msg.role === "assistant" && (
                <div className="p-2 rounded-lg bg-violet-500/10 h-fit">
                  <Bot className="size-5 text-violet-500" />
                </div>
              )}
              <div
                className={cn(
                  "rounded-lg px-4 py-3 max-w-[80%]",
                  msg.role === "user"
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted"
                )}
              >
                <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
              </div>
              {msg.role === "user" && (
                <div className="p-2 rounded-lg bg-primary/10 h-fit">
                  <MessageSquare className="size-5 text-primary" />
                </div>
              )}
            </div>
          ))}

          {isMutating && (
            <div className="flex gap-3">
              <div className="p-2 rounded-lg bg-violet-500/10 h-fit">
                <Bot className="size-5 text-violet-500" />
              </div>
              <div className="rounded-lg px-4 py-3 bg-muted">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Loader2 className="size-4 animate-spin" />
                  Thinking...
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      {/* Input Area */}
      <div className="border-t px-6 py-4">
        <div className="max-w-4xl mx-auto">
          {selectedDocSlug && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground mb-2">
              <BookOpen className="size-3.5" />
              <span>
                Using documentation: <Badge variant="secondary" className="ml-1">{selectedDocSlug}</Badge>
              </span>
            </div>
          )}
          <div className="flex gap-2">
            <Textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about the framework, configuration, agents, or how to build pipelines..."
              onKeyDown={handleKeyDown}
              disabled={isMutating}
              className="min-h-[60px] max-h-[200px] resize-none"
              rows={2}
            />
            <Button
              onClick={sendMessage}
              disabled={isMutating || !input.trim()}
              className="h-auto px-6"
            >
              {isMutating ? (
                <Loader2 className="size-5 animate-spin" />
              ) : (
                <SendHorizonal className="size-5" />
              )}
            </Button>
          </div>
          <p className="text-xs text-muted-foreground mt-2">
            Press Enter to send, Shift+Enter for new line
          </p>
        </div>
      </div>
    </div>
  );
}
