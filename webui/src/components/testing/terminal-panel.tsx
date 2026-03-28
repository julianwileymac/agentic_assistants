"use client";

import * as React from "react";
import dynamic from "next/dynamic";
import { Terminal as TerminalIcon, Trash2, Send } from "lucide-react";

import { getWsUrl } from "@/lib/api-client";
import { apiFetch } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";

type XTermCore = typeof import("@xterm/xterm");
type FitAddonMod = typeof import("@xterm/addon-fit");
type WebLinksAddonMod = typeof import("@xterm/addon-web-links");

type ConnectionStatus = "disconnected" | "connecting" | "connected";

const STATUS_COLORS: Record<ConnectionStatus, string> = {
  disconnected: "bg-red-500",
  connecting: "bg-yellow-500",
  connected: "bg-emerald-500",
};

function TerminalCore() {
  const containerRef = React.useRef<HTMLDivElement>(null);
  const termRef = React.useRef<InstanceType<XTermCore["Terminal"]> | null>(null);
  const fitRef = React.useRef<InstanceType<FitAddonMod["FitAddon"]> | null>(null);
  const wsRef = React.useRef<WebSocket | null>(null);

  const [command, setCommand] = React.useState("");
  const [status, setStatus] = React.useState<ConnectionStatus>("disconnected");
  const [runId, setRunId] = React.useState<string | null>(null);
  const [isRunning, setIsRunning] = React.useState(false);

  React.useEffect(() => {
    let cancelled = false;

    async function init() {
      const [xtermMod, fitMod, webLinksMod] = await Promise.all([
        import("@xterm/xterm"),
        import("@xterm/addon-fit"),
        import("@xterm/addon-web-links"),
      ]);

      await import("@xterm/xterm/css/xterm.css");

      if (cancelled || !containerRef.current) return;

      const term = new xtermMod.Terminal({
        cursorBlink: true,
        fontSize: 13,
        fontFamily: "'JetBrains Mono', 'Cascadia Code', 'Fira Code', monospace",
        theme: {
          background: "#0a0a0a",
          foreground: "#e4e4e7",
          cursor: "#a78bfa",
          selectionBackground: "#3f3f4640",
          black: "#09090b",
          red: "#ef4444",
          green: "#22c55e",
          yellow: "#eab308",
          blue: "#3b82f6",
          magenta: "#a855f7",
          cyan: "#06b6d4",
          white: "#e4e4e7",
        },
        allowProposedApi: true,
        scrollback: 5000,
        convertEol: true,
      });

      const fit = new fitMod.FitAddon();
      const webLinks = new webLinksMod.WebLinksAddon();

      term.loadAddon(fit);
      term.loadAddon(webLinks);
      term.open(containerRef.current);
      fit.fit();

      term.writeln("\x1b[1;35m  Agentic Assistants Terminal\x1b[0m");
      term.writeln("\x1b[2m  Type a command below and press Send or Enter.\x1b[0m");
      term.writeln("");

      termRef.current = term;
      fitRef.current = fit;
    }

    init();

    return () => {
      cancelled = true;
      termRef.current?.dispose();
      termRef.current = null;
      fitRef.current = null;
    };
  }, []);

  React.useEffect(() => {
    const fit = fitRef.current;
    if (!fit) return;

    const onResize = () => {
      try {
        fit.fit();
      } catch {
        /* terminal may not be attached yet */
      }
    };

    const observer = new ResizeObserver(onResize);
    if (containerRef.current) observer.observe(containerRef.current);
    window.addEventListener("resize", onResize);

    return () => {
      observer.disconnect();
      window.removeEventListener("resize", onResize);
    };
  }, []);

  const connectWs = React.useCallback(
    (currentRunId: string) => {
      wsRef.current?.close();
      setStatus("connecting");

      const ws = new WebSocket(getWsUrl("/ws"));
      wsRef.current = ws;

      ws.onopen = () => {
        setStatus("connected");
        ws.send(
          JSON.stringify({
            command: "subscribe",
            params: { topic: `run.${currentRunId}` },
          }),
        );
      };

      ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.type === "run.log" && payload.data?.message) {
            termRef.current?.writeln(payload.data.message);
          }
          if (payload.type === "run.complete") {
            termRef.current?.writeln(
              `\x1b[2m[completed]\x1b[0m`,
            );
          }
        } catch {
          /* ignore */
        }
      };

      ws.onerror = () => setStatus("disconnected");
      ws.onclose = () => setStatus("disconnected");
    },
    [],
  );

  React.useEffect(() => {
    return () => {
      wsRef.current?.close();
    };
  }, []);

  const handleRun = React.useCallback(async () => {
    const cmd = command.trim();
    if (!cmd) return;

    const term = termRef.current;
    term?.writeln(`\x1b[1;36m$ ${cmd}\x1b[0m`);

    setIsRunning(true);
    try {
      const res = await apiFetch<{
        run_id: string;
        status: string;
        message: string;
      }>("/api/v1/execution/scripts/run", {
        method: "POST",
        body: JSON.stringify({
          script_content: cmd,
          script_type: "shell",
        }),
      });

      if (res.run_id) {
        setRunId(res.run_id);
        connectWs(res.run_id);
      }
      if (res.message) {
        term?.writeln(res.message);
      }
    } catch (err) {
      term?.writeln(
        `\x1b[1;31mError: ${err instanceof Error ? err.message : "Unknown error"}\x1b[0m`,
      );
    } finally {
      setIsRunning(false);
      setCommand("");
    }
  }, [command, connectWs]);

  const handleClear = React.useCallback(() => {
    termRef.current?.clear();
    termRef.current?.writeln("\x1b[2mTerminal cleared.\x1b[0m");
  }, []);

  const handleKeyDown = React.useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === "Enter" && !isRunning) {
        e.preventDefault();
        handleRun();
      }
    },
    [handleRun, isRunning],
  );

  return (
    <Card className="flex h-full flex-col">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <TerminalIcon className="size-5 text-emerald-500" />
            Terminal
          </CardTitle>
          <div className="flex items-center gap-2">
            <span
              className={`inline-block size-2 rounded-full ${STATUS_COLORS[status]}`}
            />
            <Badge variant="outline" className="text-xs capitalize">
              {status}
            </Badge>
            {runId && (
              <span className="text-xs text-muted-foreground">
                Run {runId.slice(0, 8)}
              </span>
            )}
          </div>
        </div>
        <CardDescription>
          Run shell commands via the execution layer with real-time output.
        </CardDescription>
      </CardHeader>

      <CardContent className="flex flex-1 flex-col gap-3 overflow-hidden">
        <div
          ref={containerRef}
          className="min-h-[260px] flex-1 overflow-hidden rounded-md border bg-[#0a0a0a] p-1"
        />

        <div className="flex items-center gap-2">
          <Input
            placeholder="Enter a shell command..."
            value={command}
            onChange={(e) => setCommand(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isRunning}
            className="font-mono text-sm"
          />
          <Button
            size="sm"
            onClick={handleRun}
            disabled={!command.trim() || isRunning}
          >
            <Send className="mr-1.5 size-3.5" />
            {isRunning ? "Running..." : "Send"}
          </Button>
          <Button size="sm" variant="outline" onClick={handleClear}>
            <Trash2 className="size-3.5" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

export const TerminalPanel = dynamic(() => Promise.resolve(TerminalCore), {
  ssr: false,
});
