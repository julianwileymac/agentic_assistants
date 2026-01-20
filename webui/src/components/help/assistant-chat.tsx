"use client";

import * as React from "react";
import { usePathname } from "next/navigation";
import { Loader2, MessageSquare, SendHorizonal, BookOpen } from "lucide-react";

import { useAssistantChat } from "@/lib/api";
import { useHelpStore } from "@/lib/store";
import type { AssistantChatMessage } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";

type AssistantChatProps = {
  projectId?: string;
};

export function AssistantChat({ projectId }: AssistantChatProps) {
  const pathname = usePathname();
  const { selectedDocSlug } = useHelpStore();
  const [messages, setMessages] = React.useState<AssistantChatMessage[]>([]);
  const [input, setInput] = React.useState("");
  const { trigger, isMutating } = useAssistantChat();
  const messagesEndRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

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
      });
      if (response?.message) {
        setMessages((prev) => [...prev, response.message]);
      }
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, I ran into an issue answering that." },
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

