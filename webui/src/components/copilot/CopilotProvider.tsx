"use client";

import * as React from "react";
import { usePathname } from "next/navigation";
import { getBackendUrl, getApiKey } from "@/lib/api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type CopilotMessageRole = "user" | "assistant" | "system";

export interface CopilotMessage {
  id: string;
  role: CopilotMessageRole;
  content: string;
  structuredData?: StructuredBlock | null;
  createdAt: Date;
}

export interface StructuredBlock {
  type: "chart" | "table" | "code" | "flow";
  title?: string;
  data?: unknown;
  language?: string;
  code?: string;
  columns?: string[];
  rows?: Record<string, unknown>[];
  chartData?: { name: string; value: number }[];
}

export interface CopilotAction {
  name: string;
  description: string;
  parameters?: Record<string, unknown>;
  handler: (params: Record<string, unknown>) => Promise<unknown>;
}

export interface ReadableContext {
  key: string;
  value: unknown;
  description?: string;
}

interface CopilotState {
  messages: CopilotMessage[];
  input: string;
  isLoading: boolean;
  actions: CopilotAction[];
  readableContexts: ReadableContext[];
  currentPage: string;
}

interface CopilotContextValue extends CopilotState {
  setInput: (value: string) => void;
  sendMessage: (content?: string) => Promise<void>;
  clearMessages: () => void;
  registerAction: (action: CopilotAction) => void;
  unregisterAction: (name: string) => void;
  setReadableContext: (ctx: ReadableContext) => void;
  removeReadableContext: (key: string) => void;
}

const CopilotContext = React.createContext<CopilotContextValue | null>(null);

// ---------------------------------------------------------------------------
// Provider
// ---------------------------------------------------------------------------

interface CopilotProviderProps {
  children: React.ReactNode;
  endpoint?: string;
}

let _msgCounter = 0;
function nextId() {
  return `msg_${Date.now()}_${++_msgCounter}`;
}

export function CopilotProvider({
  children,
  endpoint = "/api/v1/assistant/framework-chat",
}: CopilotProviderProps) {
  const pathname = usePathname();
  const [messages, setMessages] = React.useState<CopilotMessage[]>([]);
  const [input, setInput] = React.useState("");
  const [isLoading, setIsLoading] = React.useState(false);
  const [actions, setActions] = React.useState<CopilotAction[]>([]);
  const [readableContexts, setReadableContexts] = React.useState<ReadableContext[]>([]);

  const registerAction = React.useCallback((action: CopilotAction) => {
    setActions((prev) => {
      const filtered = prev.filter((a) => a.name !== action.name);
      return [...filtered, action];
    });
  }, []);

  const unregisterAction = React.useCallback((name: string) => {
    setActions((prev) => prev.filter((a) => a.name !== name));
  }, []);

  const setReadableContext = React.useCallback((ctx: ReadableContext) => {
    setReadableContexts((prev) => {
      const filtered = prev.filter((c) => c.key !== ctx.key);
      return [...filtered, ctx];
    });
  }, []);

  const removeReadableContext = React.useCallback((key: string) => {
    setReadableContexts((prev) => prev.filter((c) => c.key !== key));
  }, []);

  const clearMessages = React.useCallback(() => setMessages([]), []);

  const sendMessage = React.useCallback(
    async (content?: string) => {
      const text = (content ?? input).trim();
      if (!text) return;

      const userMsg: CopilotMessage = {
        id: nextId(),
        role: "user",
        content: text,
        createdAt: new Date(),
      };

      setMessages((prev) => [...prev, userMsg]);
      setInput("");
      setIsLoading(true);

      const assistantMsg: CopilotMessage = {
        id: nextId(),
        role: "assistant",
        content: "",
        createdAt: new Date(),
      };
      setMessages((prev) => [...prev, assistantMsg]);

      try {
        const baseUrl = getBackendUrl();
        const apiKey = getApiKey();
        const headers: Record<string, string> = {
          "Content-Type": "application/json",
        };
        if (apiKey) headers["X-API-Key"] = apiKey;

        const contextSnapshot = readableContexts.reduce<Record<string, unknown>>(
          (acc, c) => {
            acc[c.key] = c.value;
            return acc;
          },
          {},
        );

        const body = JSON.stringify({
          messages: [...messages, userMsg].map((m) => ({
            role: m.role,
            content: m.content,
          })),
          route: pathname,
          context: contextSnapshot,
          stream: true,
        });

        const response = await fetch(`${baseUrl}${endpoint}`, {
          method: "POST",
          headers,
          body,
        });

        if (!response.ok) {
          const errData = await response.json().catch(() => ({}));
          throw new Error(
            (errData as { detail?: string }).detail ?? `API error ${response.status}`,
          );
        }

        if (response.body) {
          const reader = response.body.getReader();
          const decoder = new TextDecoder();
          let accumulated = "";

          while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            const chunk = decoder.decode(value, { stream: true });
            accumulated += chunk;

            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantMsg.id ? { ...m, content: accumulated } : m,
              ),
            );
          }

          const structured = tryParseStructuredBlock(accumulated);
          if (structured) {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantMsg.id
                  ? { ...m, structuredData: structured }
                  : m,
              ),
            );
          }
        } else {
          const data = (await response.json()) as { message?: { content?: string } };
          const text = data?.message?.content ?? "No response received.";
          const structured = tryParseStructuredBlock(text);
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantMsg.id
                ? { ...m, content: text, structuredData: structured }
                : m,
            ),
          );
        }
      } catch (err) {
        const errorText =
          err instanceof Error ? err.message : "An unexpected error occurred.";
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantMsg.id
              ? { ...m, content: `Error: ${errorText}` }
              : m,
          ),
        );
      } finally {
        setIsLoading(false);
      }
    },
    [input, messages, pathname, readableContexts, endpoint],
  );

  const value = React.useMemo<CopilotContextValue>(
    () => ({
      messages,
      input,
      isLoading,
      actions,
      readableContexts,
      currentPage: pathname,
      setInput,
      sendMessage,
      clearMessages,
      registerAction,
      unregisterAction,
      setReadableContext,
      removeReadableContext,
    }),
    [
      messages,
      input,
      isLoading,
      actions,
      readableContexts,
      pathname,
      sendMessage,
      clearMessages,
      registerAction,
      unregisterAction,
      setReadableContext,
      removeReadableContext,
    ],
  );

  return (
    <CopilotContext.Provider value={value}>{children}</CopilotContext.Provider>
  );
}

// ---------------------------------------------------------------------------
// Hooks
// ---------------------------------------------------------------------------

function useCopilotContext() {
  const ctx = React.useContext(CopilotContext);
  if (!ctx) {
    throw new Error("useCopilotChat must be used within a <CopilotProvider>");
  }
  return ctx;
}

export function useCopilotChat() {
  const {
    messages,
    input,
    isLoading,
    setInput,
    sendMessage,
    clearMessages,
  } = useCopilotContext();
  return { messages, input, isLoading, setInput, sendMessage, clearMessages };
}

export function useCopilotReadable(ctx: ReadableContext) {
  const { setReadableContext, removeReadableContext } = useCopilotContext();

  React.useEffect(() => {
    setReadableContext(ctx);
    return () => removeReadableContext(ctx.key);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ctx.key, ctx.value]);
}

export function useCopilotAction(action: CopilotAction) {
  const { registerAction, unregisterAction } = useCopilotContext();

  React.useEffect(() => {
    registerAction(action);
    return () => unregisterAction(action.name);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [action.name]);
}

export function useCopilotContextValues() {
  const { readableContexts, currentPage } = useCopilotContext();
  return { readableContexts, currentPage };
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function tryParseStructuredBlock(text: string): StructuredBlock | null {
  const fenceMatch = text.match(/```structured\s*\n([\s\S]*?)```/);
  if (fenceMatch) {
    try {
      return JSON.parse(fenceMatch[1]) as StructuredBlock;
    } catch {
      return null;
    }
  }

  try {
    const parsed = JSON.parse(text);
    if (
      parsed &&
      typeof parsed === "object" &&
      "type" in parsed &&
      ["chart", "table", "code", "flow"].includes(parsed.type)
    ) {
      return parsed as StructuredBlock;
    }
  } catch {
    // not structured JSON — fine
  }
  return null;
}
