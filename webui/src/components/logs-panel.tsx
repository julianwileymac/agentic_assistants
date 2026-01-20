"use client";

import * as React from "react";
import {
  ScrollText,
  Pause,
  Play,
  Trash2,
  Download,
  Filter,
  X,
  AlertCircle,
  AlertTriangle,
  Info,
  Bug,
  ChevronRight,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";

// === Types ===

interface LogEntry {
  timestamp: string;
  level: string;
  logger: string;
  message: string;
  context?: Record<string, unknown>;
}

type LogLevel = "DEBUG" | "INFO" | "WARNING" | "ERROR" | "CRITICAL" | "ALL";

// === WebSocket Hook ===

const WS_URL = "ws://localhost:8080/ws/logs";

function useLogStream() {
  const [logs, setLogs] = React.useState<LogEntry[]>([]);
  const [isConnected, setIsConnected] = React.useState(false);
  const [isPaused, setIsPaused] = React.useState(false);
  const wsRef = React.useRef<WebSocket | null>(null);
  const logsBufferRef = React.useRef<LogEntry[]>([]);

  const connect = React.useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      setIsConnected(true);
      console.log("Log stream connected");
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        
        if (message.type === "log.entry" && message.data) {
          const logEntry: LogEntry = {
            timestamp: message.data.timestamp || new Date().toISOString(),
            level: message.data.level || "INFO",
            logger: message.data.logger || "unknown",
            message: message.data.message || "",
            context: message.data.context,
          };

          if (!isPaused) {
            setLogs((prev) => [...prev.slice(-499), logEntry]); // Keep last 500 logs
          } else {
            // Buffer logs while paused
            logsBufferRef.current.push(logEntry);
            if (logsBufferRef.current.length > 500) {
              logsBufferRef.current.shift();
            }
          }
        }
      } catch (e) {
        console.error("Failed to parse log message:", e);
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      console.log("Log stream disconnected");
      // Reconnect after delay
      setTimeout(connect, 3000);
    };

    ws.onerror = () => {
      console.error("Log stream error: Failed to connect to WebSocket at", WS_URL);
    };

    wsRef.current = ws;
  }, [isPaused]);

  const disconnect = React.useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  const pause = React.useCallback(() => {
    setIsPaused(true);
  }, []);

  const resume = React.useCallback(() => {
    // Merge buffered logs
    if (logsBufferRef.current.length > 0) {
      setLogs((prev) => [...prev, ...logsBufferRef.current].slice(-500));
      logsBufferRef.current = [];
    }
    setIsPaused(false);
  }, []);

  const clear = React.useCallback(() => {
    setLogs([]);
    logsBufferRef.current = [];
  }, []);

  React.useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    logs,
    isConnected,
    isPaused,
    connect,
    disconnect,
    pause,
    resume,
    clear,
  };
}

// === Log Level Badge ===

function LogLevelBadge({ level }: { level: string }) {
  const config: Record<string, { icon: React.ReactNode; className: string }> = {
    DEBUG: {
      icon: <Bug className="size-3" />,
      className: "bg-slate-500/10 text-slate-500 border-slate-500/20",
    },
    INFO: {
      icon: <Info className="size-3" />,
      className: "bg-blue-500/10 text-blue-500 border-blue-500/20",
    },
    WARNING: {
      icon: <AlertTriangle className="size-3" />,
      className: "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
    },
    ERROR: {
      icon: <AlertCircle className="size-3" />,
      className: "bg-red-500/10 text-red-500 border-red-500/20",
    },
    CRITICAL: {
      icon: <AlertCircle className="size-3" />,
      className: "bg-red-600/20 text-red-600 border-red-600/30",
    },
  };

  const { icon, className } = config[level.toUpperCase()] || config.INFO;

  return (
    <Badge variant="outline" className={cn("gap-1 font-mono text-xs", className)}>
      {icon}
      {level}
    </Badge>
  );
}

// === Log Entry Row ===

function LogEntryRow({ entry, expanded, onToggle }: { 
  entry: LogEntry; 
  expanded: boolean;
  onToggle: () => void;
}) {
  const time = new Date(entry.timestamp).toLocaleTimeString();
  const hasContext = entry.context && Object.keys(entry.context).length > 0;

  return (
    <div 
      className={cn(
        "py-2 px-3 border-b border-border/50 hover:bg-muted/30 transition-colors",
        entry.level === "ERROR" && "bg-red-500/5",
        entry.level === "WARNING" && "bg-yellow-500/5",
      )}
    >
      <div 
        className="flex items-start gap-3 cursor-pointer"
        onClick={hasContext ? onToggle : undefined}
      >
        {hasContext && (
          <ChevronRight 
            className={cn(
              "size-4 mt-0.5 text-muted-foreground transition-transform",
              expanded && "rotate-90"
            )} 
          />
        )}
        <span className="text-xs text-muted-foreground font-mono w-20 shrink-0">
          {time}
        </span>
        <LogLevelBadge level={entry.level} />
        <span className="text-xs text-muted-foreground font-mono truncate w-32 shrink-0">
          {entry.logger.split(".").pop()}
        </span>
        <span className="text-sm flex-1 break-words">{entry.message}</span>
      </div>
      
      {expanded && hasContext && (
        <div className="mt-2 ml-28 p-2 rounded bg-muted/50 text-xs font-mono">
          <pre className="whitespace-pre-wrap">
            {JSON.stringify(entry.context, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

// === Logs Panel Component ===

interface LogsPanelProps {
  trigger?: React.ReactNode;
}

export function LogsPanel({ trigger }: LogsPanelProps) {
  const { logs, isConnected, isPaused, connect, disconnect, pause, resume, clear } = useLogStream();
  const [isOpen, setIsOpen] = React.useState(false);
  const [filter, setFilter] = React.useState("");
  const [levelFilter, setLevelFilter] = React.useState<LogLevel>("ALL");
  const [expandedIds, setExpandedIds] = React.useState<Set<number>>(new Set());
  const scrollRef = React.useRef<HTMLDivElement>(null);
  const autoScrollRef = React.useRef(true);

  // Connect when panel opens
  React.useEffect(() => {
    if (isOpen && !isConnected) {
      connect();
    }
  }, [isOpen, isConnected, connect]);

  // Auto-scroll to bottom
  React.useEffect(() => {
    if (autoScrollRef.current && scrollRef.current && !isPaused) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs, isPaused]);

  // Handle scroll to detect if user scrolled up
  const handleScroll = () => {
    if (scrollRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = scrollRef.current;
      autoScrollRef.current = scrollHeight - scrollTop - clientHeight < 50;
    }
  };

  // Filter logs
  const filteredLogs = React.useMemo(() => {
    return logs.filter((log) => {
      // Level filter
      if (levelFilter !== "ALL" && log.level.toUpperCase() !== levelFilter) {
        return false;
      }
      // Text filter
      if (filter) {
        const searchText = filter.toLowerCase();
        return (
          log.message.toLowerCase().includes(searchText) ||
          log.logger.toLowerCase().includes(searchText)
        );
      }
      return true;
    });
  }, [logs, filter, levelFilter]);

  const toggleExpanded = (index: number) => {
    setExpandedIds((prev) => {
      const next = new Set(prev);
      if (next.has(index)) {
        next.delete(index);
      } else {
        next.add(index);
      }
      return next;
    });
  };

  const handleDownload = () => {
    const content = filteredLogs
      .map((log) => `[${log.timestamp}] [${log.level}] [${log.logger}] ${log.message}`)
      .join("\n");
    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `logs-${new Date().toISOString()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <Sheet open={isOpen} onOpenChange={setIsOpen}>
      <SheetTrigger asChild>
        {trigger || (
          <Button variant="ghost" size="icon">
            <ScrollText className="size-5" />
          </Button>
        )}
      </SheetTrigger>
      <SheetContent side="bottom" className="h-[60vh] flex flex-col">
        <SheetHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <SheetTitle className="flex items-center gap-2">
                <ScrollText className="size-5" />
                System Logs
              </SheetTitle>
              <Badge variant={isConnected ? "default" : "secondary"}>
                {isConnected ? "Connected" : "Disconnected"}
              </Badge>
              {isPaused && (
                <Badge variant="secondary">Paused</Badge>
              )}
            </div>
            <div className="flex items-center gap-2">
              {isPaused ? (
                <Button variant="ghost" size="icon" onClick={resume}>
                  <Play className="size-4" />
                </Button>
              ) : (
                <Button variant="ghost" size="icon" onClick={pause}>
                  <Pause className="size-4" />
                </Button>
              )}
              <Button variant="ghost" size="icon" onClick={clear}>
                <Trash2 className="size-4" />
              </Button>
              <Button variant="ghost" size="icon" onClick={handleDownload}>
                <Download className="size-4" />
              </Button>
            </div>
          </div>
          <SheetDescription className="sr-only">
            Real-time log stream from the backend server
          </SheetDescription>
        </SheetHeader>

        {/* Filters */}
        <div className="flex items-center gap-3 py-3 border-b">
          <div className="relative flex-1 max-w-sm">
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
            <Input
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              placeholder="Filter logs..."
              className="pl-9"
            />
            {filter && (
              <Button
                variant="ghost"
                size="icon"
                className="absolute right-1 top-1/2 -translate-y-1/2 size-6"
                onClick={() => setFilter("")}
              >
                <X className="size-3" />
              </Button>
            )}
          </div>
          <Select value={levelFilter} onValueChange={(v) => setLevelFilter(v as LogLevel)}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ALL">All Levels</SelectItem>
              <SelectItem value="DEBUG">Debug</SelectItem>
              <SelectItem value="INFO">Info</SelectItem>
              <SelectItem value="WARNING">Warning</SelectItem>
              <SelectItem value="ERROR">Error</SelectItem>
              <SelectItem value="CRITICAL">Critical</SelectItem>
            </SelectContent>
          </Select>
          <span className="text-sm text-muted-foreground">
            {filteredLogs.length} / {logs.length} logs
          </span>
        </div>

        {/* Log List */}
        <ScrollArea 
          className="flex-1" 
          ref={scrollRef}
          onScrollCapture={handleScroll}
        >
          {filteredLogs.length === 0 ? (
            <div className="flex items-center justify-center h-full text-muted-foreground">
              <div className="text-center">
                <ScrollText className="size-10 mx-auto mb-2 opacity-50" />
                <p>No logs to display</p>
                {!isConnected && (
                  <Button variant="link" size="sm" onClick={connect} className="mt-2">
                    Connect to log stream
                  </Button>
                )}
              </div>
            </div>
          ) : (
            <div className="divide-y divide-border/50">
              {filteredLogs.map((log, index) => (
                <LogEntryRow
                  key={`${log.timestamp}-${index}`}
                  entry={log}
                  expanded={expandedIds.has(index)}
                  onToggle={() => toggleExpanded(index)}
                />
              ))}
            </div>
          )}
        </ScrollArea>
      </SheetContent>
    </Sheet>
  );
}

// === Floating Logs Button ===

export function LogsButton() {
  return (
    <LogsPanel
      trigger={
        <Button
          variant="outline"
          size="icon"
          className="fixed bottom-6 right-6 size-12 rounded-full shadow-lg z-50"
        >
          <ScrollText className="size-5" />
        </Button>
      }
    />
  );
}
