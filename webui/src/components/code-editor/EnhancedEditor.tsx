"use client";

import dynamic from "next/dynamic";
import * as React from "react";
import type { editor } from "monaco-editor";
import {
  Play,
  Square,
  AlertTriangle,
  X,
  Plus,
  FileCode2,
  ChevronDown,
  Sparkles,
  Bot,
  GripHorizontal,
  Loader2,
  Copy,
  Trash2,
  PanelRightOpen,
  PanelRightClose,
  Send,
} from "lucide-react";

import { apiFetch } from "@/lib/api";
import { getWsUrl } from "@/lib/api-client";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";

// ---------------------------------------------------------------------------
// Dynamic Monaco import (SSR disabled)
// ---------------------------------------------------------------------------

const MonacoEditor = dynamic(() => import("@monaco-editor/react"), {
  ssr: false,
  loading: () => (
    <div className="flex flex-col items-center justify-center gap-3 h-full bg-[#1e1e1e]">
      <Skeleton className="h-4 w-48 bg-zinc-800" />
      <Skeleton className="h-4 w-36 bg-zinc-800" />
      <Skeleton className="h-4 w-52 bg-zinc-800" />
    </div>
  ),
});

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type SupportedLanguage =
  | "python"
  | "javascript"
  | "typescript"
  | "yaml"
  | "json"
  | "bash";

interface EditorTab {
  id: string;
  label: string;
  language: SupportedLanguage;
  value: string;
  isDirty: boolean;
}

interface LintDiagnostic {
  line: number;
  column: number;
  end_line?: number;
  end_column?: number;
  severity: "error" | "warning" | "info" | "hint";
  message: string;
  code?: string;
  source?: string;
}

interface LintResponse {
  diagnostics: LintDiagnostic[];
  summary?: { errors: number; warnings: number; info: number };
}

interface RunResponse {
  run_id: string;
  status: string;
}

interface ReviewResponse {
  review: string;
  suggestions?: Array<{
    line?: number;
    message: string;
    severity?: string;
  }>;
}

interface OutputLine {
  text: string;
  type: "stdout" | "stderr" | "system";
  timestamp?: string;
}

export interface EnhancedEditorProps {
  initialValue?: string;
  initialLanguage?: string;
  projectId?: string;
  onSave?: (value: string) => void;
  className?: string;
  height?: string;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const LANGUAGES: { value: SupportedLanguage; label: string }[] = [
  { value: "python", label: "Python" },
  { value: "javascript", label: "JavaScript" },
  { value: "typescript", label: "TypeScript" },
  { value: "yaml", label: "YAML" },
  { value: "json", label: "JSON" },
  { value: "bash", label: "Bash" },
];

const SEVERITY_MAP: Record<string, number> = {
  error: 8,
  warning: 4,
  info: 2,
  hint: 1,
};

function createTabId(): string {
  return `tab-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
}

// ---------------------------------------------------------------------------
// EnhancedEditor Component
// ---------------------------------------------------------------------------

export function EnhancedEditor({
  initialValue = "",
  initialLanguage = "python",
  projectId,
  onSave,
  className,
  height = "100%",
}: EnhancedEditorProps) {
  const editorRef = React.useRef<editor.IStandaloneCodeEditor | null>(null);
  const monacoRef = React.useRef<typeof import("monaco-editor") | null>(null);
  const dividerRef = React.useRef<HTMLDivElement>(null);
  const containerRef = React.useRef<HTMLDivElement>(null);
  const wsRef = React.useRef<WebSocket | null>(null);

  const [tabs, setTabs] = React.useState<EditorTab[]>(() => [
    {
      id: createTabId(),
      label: "untitled-1",
      language: initialLanguage as SupportedLanguage,
      value: initialValue,
      isDirty: false,
    },
  ]);
  const [activeTabId, setActiveTabId] = React.useState(tabs[0].id);

  const [outputLines, setOutputLines] = React.useState<OutputLine[]>([]);
  const [isRunning, setIsRunning] = React.useState(false);
  const [isLinting, setIsLinting] = React.useState(false);
  const [isReviewing, setIsReviewing] = React.useState(false);
  const [lintSummary, setLintSummary] = React.useState<{
    errors: number;
    warnings: number;
  } | null>(null);
  const [editorSplitRatio, setEditorSplitRatio] = React.useState(0.65);
  const [showOutput, setShowOutput] = React.useState(false);
  const [showSidebar, setShowSidebar] = React.useState(false);
  const [reviewContent, setReviewContent] = React.useState<string>("");
  const [codeGenPrompt, setCodeGenPrompt] = React.useState("");
  const [isGenerating, setIsGenerating] = React.useState(false);

  const outputEndRef = React.useRef<HTMLDivElement>(null);

  const activeTab = React.useMemo(
    () => tabs.find((t) => t.id === activeTabId) ?? tabs[0],
    [tabs, activeTabId],
  );

  // -------------------------------------------------------------------------
  // Editor mount
  // -------------------------------------------------------------------------

  const handleEditorMount = React.useCallback(
    (ed: editor.IStandaloneCodeEditor, monaco: typeof import("monaco-editor")) => {
      editorRef.current = ed;
      monacoRef.current = monaco;

      ed.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
        const value = ed.getValue();
        onSave?.(value);
        setTabs((prev) =>
          prev.map((t) =>
            t.id === activeTabId ? { ...t, isDirty: false } : t,
          ),
        );
      });
    },
    [activeTabId, onSave],
  );

  // -------------------------------------------------------------------------
  // Tab management
  // -------------------------------------------------------------------------

  const addTab = React.useCallback(() => {
    const nextNum = tabs.length + 1;
    const newTab: EditorTab = {
      id: createTabId(),
      label: `untitled-${nextNum}`,
      language: "python",
      value: "",
      isDirty: false,
    };
    setTabs((prev) => [...prev, newTab]);
    setActiveTabId(newTab.id);
  }, [tabs.length]);

  const closeTab = React.useCallback(
    (tabId: string) => {
      setTabs((prev) => {
        const filtered = prev.filter((t) => t.id !== tabId);
        if (filtered.length === 0) {
          const fresh: EditorTab = {
            id: createTabId(),
            label: "untitled-1",
            language: "python",
            value: "",
            isDirty: false,
          };
          return [fresh];
        }
        return filtered;
      });

      if (activeTabId === tabId) {
        setTabs((prev) => {
          const idx = prev.findIndex((t) => t.id === tabId);
          const next = prev[Math.max(0, idx - 1)] ?? prev[0];
          setActiveTabId(next.id);
          return prev;
        });
      }
    },
    [activeTabId],
  );

  const updateActiveTabValue = React.useCallback(
    (value: string | undefined) => {
      setTabs((prev) =>
        prev.map((t) =>
          t.id === activeTabId
            ? { ...t, value: value ?? "", isDirty: true }
            : t,
        ),
      );
    },
    [activeTabId],
  );

  const updateActiveTabLanguage = React.useCallback(
    (lang: SupportedLanguage) => {
      setTabs((prev) =>
        prev.map((t) =>
          t.id === activeTabId ? { ...t, language: lang } : t,
        ),
      );
    },
    [activeTabId],
  );

  // -------------------------------------------------------------------------
  // Lint
  // -------------------------------------------------------------------------

  const handleLint = React.useCallback(async () => {
    const monaco = monacoRef.current;
    const ed = editorRef.current;
    if (!monaco || !ed) return;

    setIsLinting(true);
    setLintSummary(null);

    try {
      const res = await apiFetch<LintResponse>("/api/v1/testing/lint", {
        method: "POST",
        body: JSON.stringify({
          code: activeTab.value,
          language: activeTab.language,
          project_id: projectId,
        }),
      });

      const model = ed.getModel();
      if (!model) return;

      const markers: editor.IMarkerData[] = (res.diagnostics ?? []).map(
        (d) => ({
          severity:
            SEVERITY_MAP[d.severity] ?? monaco.MarkerSeverity.Info,
          startLineNumber: d.line,
          startColumn: d.column,
          endLineNumber: d.end_line ?? d.line,
          endColumn: d.end_column ?? d.column + 1,
          message: d.message,
          source: d.source ?? "lint",
          code: d.code,
        }),
      );

      monaco.editor.setModelMarkers(model, "lint", markers);

      const errors = markers.filter(
        (m) => m.severity === monaco.MarkerSeverity.Error,
      ).length;
      const warnings = markers.filter(
        (m) => m.severity === monaco.MarkerSeverity.Warning,
      ).length;
      setLintSummary({ errors, warnings });

      if (!showOutput) setShowOutput(true);
      setOutputLines((prev) => [
        ...prev,
        {
          text: `Lint complete: ${errors} error(s), ${warnings} warning(s)`,
          type: "system",
        },
      ]);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Lint failed";
      setOutputLines((prev) => [...prev, { text: msg, type: "stderr" }]);
      if (!showOutput) setShowOutput(true);
    } finally {
      setIsLinting(false);
    }
  }, [activeTab, projectId, showOutput]);

  // -------------------------------------------------------------------------
  // Run
  // -------------------------------------------------------------------------

  const handleRun = React.useCallback(async () => {
    setIsRunning(true);
    setShowOutput(true);
    setOutputLines((prev) => [
      ...prev,
      { text: "--- Running script ---", type: "system" },
    ]);

    try {
      const res = await apiFetch<RunResponse>(
        "/api/v1/execution/scripts/run",
        {
          method: "POST",
          body: JSON.stringify({
            code: activeTab.value,
            language: activeTab.language,
            project_id: projectId,
          }),
        },
      );

      const runId = res.run_id;
      if (!runId) {
        setOutputLines((prev) => [
          ...prev,
          { text: "No run_id returned from server.", type: "stderr" },
        ]);
        setIsRunning(false);
        return;
      }

      const wsUrl = getWsUrl(`/ws/run.${runId}`);
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === "output" || msg.type === "stdout") {
            setOutputLines((prev) => [
              ...prev,
              { text: msg.data ?? msg.text ?? "", type: "stdout" },
            ]);
          } else if (msg.type === "stderr" || msg.type === "error") {
            setOutputLines((prev) => [
              ...prev,
              { text: msg.data ?? msg.text ?? "", type: "stderr" },
            ]);
          } else if (msg.type === "exit" || msg.type === "done") {
            setOutputLines((prev) => [
              ...prev,
              {
                text: `Process exited with code ${msg.exit_code ?? 0}`,
                type: "system",
              },
            ]);
            setIsRunning(false);
            ws.close();
          }
        } catch {
          setOutputLines((prev) => [
            ...prev,
            { text: event.data, type: "stdout" },
          ]);
        }
      };

      ws.onerror = () => {
        setOutputLines((prev) => [
          ...prev,
          { text: "WebSocket connection error.", type: "stderr" },
        ]);
        setIsRunning(false);
      };

      ws.onclose = () => {
        setIsRunning(false);
      };
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Run failed";
      setOutputLines((prev) => [...prev, { text: msg, type: "stderr" }]);
      setIsRunning(false);
    }
  }, [activeTab, projectId]);

  const handleStop = React.useCallback(() => {
    wsRef.current?.close();
    wsRef.current = null;
    setIsRunning(false);
    setOutputLines((prev) => [
      ...prev,
      { text: "Execution stopped.", type: "system" },
    ]);
  }, []);

  // -------------------------------------------------------------------------
  // AI Code Review
  // -------------------------------------------------------------------------

  const handleReview = React.useCallback(async () => {
    setIsReviewing(true);
    setShowSidebar(true);
    setReviewContent("");

    try {
      const res = await apiFetch<ReviewResponse>(
        "/api/v1/assistant/review-code",
        {
          method: "POST",
          body: JSON.stringify({
            code: activeTab.value,
            language: activeTab.language,
            project_id: projectId,
          }),
        },
      );

      setReviewContent(res.review ?? "No review content returned.");

      if (res.suggestions?.length && monacoRef.current && editorRef.current) {
        const model = editorRef.current.getModel();
        if (model) {
          const markers: editor.IMarkerData[] = res.suggestions
            .filter((s) => s.line)
            .map((s) => ({
              severity: monacoRef.current!.MarkerSeverity.Hint,
              startLineNumber: s.line!,
              startColumn: 1,
              endLineNumber: s.line!,
              endColumn: model.getLineMaxColumn(s.line!),
              message: s.message,
              source: "ai-review",
            }));
          monacoRef.current.editor.setModelMarkers(model, "ai-review", markers);
        }
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Review failed";
      setReviewContent(`Error: ${msg}`);
    } finally {
      setIsReviewing(false);
    }
  }, [activeTab, projectId]);

  // -------------------------------------------------------------------------
  // Code generation
  // -------------------------------------------------------------------------

  const handleGenerate = React.useCallback(async () => {
    if (!codeGenPrompt.trim()) return;
    setIsGenerating(true);

    try {
      const res = await apiFetch<{ code: string }>(
        "/api/v1/assistant/review-code",
        {
          method: "POST",
          body: JSON.stringify({
            prompt: codeGenPrompt,
            language: activeTab.language,
            context: activeTab.value,
            project_id: projectId,
            mode: "generate",
          }),
        },
      );

      if (res.code && editorRef.current) {
        const ed = editorRef.current;
        const position = ed.getPosition();
        if (position) {
          ed.executeEdits("ai-generate", [
            {
              range: {
                startLineNumber: position.lineNumber,
                startColumn: position.column,
                endLineNumber: position.lineNumber,
                endColumn: position.column,
              },
              text: res.code,
            },
          ]);
        }
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Generation failed";
      setOutputLines((prev) => [...prev, { text: msg, type: "stderr" }]);
      setShowOutput(true);
    } finally {
      setIsGenerating(false);
      setCodeGenPrompt("");
    }
  }, [codeGenPrompt, activeTab, projectId]);

  // -------------------------------------------------------------------------
  // Draggable split divider
  // -------------------------------------------------------------------------

  const handleDividerMouseDown = React.useCallback(
    (e: React.MouseEvent) => {
      e.preventDefault();
      const container = containerRef.current;
      if (!container) return;

      const startY = e.clientY;
      const containerRect = container.getBoundingClientRect();
      const startRatio = editorSplitRatio;

      const onMouseMove = (ev: MouseEvent) => {
        const dy = ev.clientY - startY;
        const newRatio = startRatio + dy / containerRect.height;
        setEditorSplitRatio(Math.max(0.2, Math.min(0.85, newRatio)));
      };

      const onMouseUp = () => {
        document.removeEventListener("mousemove", onMouseMove);
        document.removeEventListener("mouseup", onMouseUp);
      };

      document.addEventListener("mousemove", onMouseMove);
      document.addEventListener("mouseup", onMouseUp);
    },
    [editorSplitRatio],
  );

  // -------------------------------------------------------------------------
  // Auto-scroll output
  // -------------------------------------------------------------------------

  React.useEffect(() => {
    outputEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [outputLines]);

  // -------------------------------------------------------------------------
  // Cleanup WebSocket on unmount
  // -------------------------------------------------------------------------

  React.useEffect(() => {
    return () => {
      wsRef.current?.close();
    };
  }, []);

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------

  const editorHeightPct = showOutput
    ? `${editorSplitRatio * 100}%`
    : "100%";
  const outputHeightPct = showOutput
    ? `${(1 - editorSplitRatio) * 100}%`
    : "0%";

  return (
    <div
      ref={containerRef}
      className={cn(
        "flex flex-col bg-[#1e1e1e] border border-zinc-800 rounded-lg overflow-hidden",
        className,
      )}
      style={{ height }}
    >
      {/* ================================================================ */}
      {/* Toolbar */}
      {/* ================================================================ */}
      <div className="flex items-center gap-1 px-2 py-1.5 bg-zinc-900 border-b border-zinc-800 shrink-0">
        {/* Language selector */}
        <Select
          value={activeTab.language}
          onValueChange={(v) => updateActiveTabLanguage(v as SupportedLanguage)}
        >
          <SelectTrigger className="h-7 w-32 text-xs bg-zinc-800 border-zinc-700 text-zinc-300">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {LANGUAGES.map((lang) => (
              <SelectItem key={lang.value} value={lang.value}>
                {lang.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <div className="w-px h-5 bg-zinc-700 mx-1" />

        {/* Lint button */}
        <Button
          variant="ghost"
          size="sm"
          onClick={handleLint}
          disabled={isLinting}
          className="h-7 gap-1.5 text-xs text-zinc-400 hover:text-zinc-100"
        >
          {isLinting ? (
            <Loader2 className="size-3.5 animate-spin" />
          ) : (
            <AlertTriangle className="size-3.5" />
          )}
          Lint
          {lintSummary && (
            <Badge
              variant={lintSummary.errors > 0 ? "destructive" : "secondary"}
              className="ml-1 h-4 px-1.5 text-[10px]"
            >
              {lintSummary.errors > 0
                ? `${lintSummary.errors}E`
                : `${lintSummary.warnings}W`}
            </Badge>
          )}
        </Button>

        {/* Run / Stop button */}
        {isRunning ? (
          <Button
            variant="ghost"
            size="sm"
            onClick={handleStop}
            className="h-7 gap-1.5 text-xs text-red-400 hover:text-red-300"
          >
            <Square className="size-3.5" />
            Stop
          </Button>
        ) : (
          <Button
            variant="ghost"
            size="sm"
            onClick={handleRun}
            className="h-7 gap-1.5 text-xs text-emerald-400 hover:text-emerald-300"
          >
            <Play className="size-3.5" />
            Run
          </Button>
        )}

        <div className="w-px h-5 bg-zinc-700 mx-1" />

        {/* AI Review */}
        <Button
          variant="ghost"
          size="sm"
          onClick={handleReview}
          disabled={isReviewing}
          className="h-7 gap-1.5 text-xs text-violet-400 hover:text-violet-300"
        >
          {isReviewing ? (
            <Loader2 className="size-3.5 animate-spin" />
          ) : (
            <Bot className="size-3.5" />
          )}
          Review
        </Button>

        {/* AI Sidebar toggle */}
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setShowSidebar((v) => !v)}
          className="h-7 gap-1.5 text-xs text-zinc-400 hover:text-zinc-100"
        >
          {showSidebar ? (
            <PanelRightClose className="size-3.5" />
          ) : (
            <PanelRightOpen className="size-3.5" />
          )}
          AI
        </Button>

        <div className="flex-1" />

        {/* Output toggle */}
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setShowOutput((v) => !v)}
          className="h-7 gap-1.5 text-xs text-zinc-400 hover:text-zinc-100"
        >
          <ChevronDown
            className={cn(
              "size-3.5 transition-transform",
              showOutput && "rotate-180",
            )}
          />
          Output
        </Button>
      </div>

      {/* ================================================================ */}
      {/* Tab Bar */}
      {/* ================================================================ */}
      <div className="flex items-center bg-zinc-900/80 border-b border-zinc-800 shrink-0 overflow-x-auto">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTabId(tab.id)}
            className={cn(
              "group relative flex items-center gap-1.5 px-3 py-1.5 text-xs border-r border-zinc-800 transition-colors min-w-0 shrink-0",
              tab.id === activeTabId
                ? "bg-[#1e1e1e] text-zinc-200"
                : "bg-zinc-900/60 text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800/50",
            )}
          >
            <FileCode2 className="size-3 shrink-0" />
            <span className="truncate max-w-[120px]">{tab.label}</span>
            {tab.isDirty && (
              <span className="size-1.5 rounded-full bg-blue-400 shrink-0" />
            )}
            {tabs.length > 1 && (
              <span
                role="button"
                tabIndex={0}
                onClick={(e) => {
                  e.stopPropagation();
                  closeTab(tab.id);
                }}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.stopPropagation();
                    closeTab(tab.id);
                  }
                }}
                className="ml-1 opacity-0 group-hover:opacity-100 hover:text-red-400 transition-opacity shrink-0"
              >
                <X className="size-3" />
              </span>
            )}
          </button>
        ))}

        <button
          onClick={addTab}
          className="flex items-center justify-center px-2 py-1.5 text-zinc-500 hover:text-zinc-300 transition-colors shrink-0"
          title="New tab"
        >
          <Plus className="size-3.5" />
        </button>
      </div>

      {/* ================================================================ */}
      {/* Main content: Editor + optional sidebar */}
      {/* ================================================================ */}
      <div className="flex flex-1 min-h-0 overflow-hidden">
        {/* Editor + Output column */}
        <div className="flex flex-col flex-1 min-w-0">
          {/* Editor pane */}
          <div style={{ height: editorHeightPct }} className="min-h-0">
            <MonacoEditor
              height="100%"
              language={activeTab.language}
              value={activeTab.value}
              theme="vs-dark"
              onChange={updateActiveTabValue}
              onMount={handleEditorMount}
              options={{
                minimap: { enabled: false },
                fontSize: 13,
                lineNumbers: "on",
                wordWrap: "on",
                scrollBeyondLastLine: false,
                padding: { top: 8, bottom: 8 },
                smoothScrolling: true,
                cursorBlinking: "smooth",
                renderLineHighlight: "gutter",
                bracketPairColorization: { enabled: true },
                automaticLayout: true,
              }}
            />
          </div>

          {/* Draggable divider */}
          {showOutput && (
            <div
              ref={dividerRef}
              onMouseDown={handleDividerMouseDown}
              className="flex items-center justify-center h-2 bg-zinc-900 border-y border-zinc-800 cursor-row-resize hover:bg-zinc-700/50 transition-colors shrink-0 group"
            >
              <GripHorizontal className="size-4 text-zinc-600 group-hover:text-zinc-400" />
            </div>
          )}

          {/* Output / Terminal panel */}
          {showOutput && (
            <div
              style={{ height: outputHeightPct }}
              className="flex flex-col min-h-0 bg-[#1a1a1a]"
            >
              <div className="flex items-center justify-between px-3 py-1 bg-zinc-900/80 border-b border-zinc-800 shrink-0">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-medium text-zinc-400">
                    Output
                  </span>
                  {isRunning && (
                    <Badge
                      variant="secondary"
                      className="h-4 px-1.5 text-[10px] gap-1"
                    >
                      <Loader2 className="size-2.5 animate-spin" />
                      Running
                    </Badge>
                  )}
                </div>
                <div className="flex items-center gap-1">
                  <Button
                    variant="ghost"
                    size="icon-sm"
                    onClick={() => {
                      const text = outputLines.map((l) => l.text).join("\n");
                      navigator.clipboard.writeText(text);
                    }}
                    className="size-6 text-zinc-500 hover:text-zinc-300"
                    title="Copy output"
                  >
                    <Copy className="size-3" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon-sm"
                    onClick={() => setOutputLines([])}
                    className="size-6 text-zinc-500 hover:text-zinc-300"
                    title="Clear output"
                  >
                    <Trash2 className="size-3" />
                  </Button>
                </div>
              </div>

              <ScrollArea className="flex-1">
                <div className="p-3 font-mono text-xs leading-relaxed">
                  {outputLines.length === 0 ? (
                    <span className="text-zinc-600 italic">
                      No output yet. Run your code to see results.
                    </span>
                  ) : (
                    outputLines.map((line, i) => (
                      <div
                        key={i}
                        className={cn(
                          "whitespace-pre-wrap break-all",
                          line.type === "stderr" && "text-red-400",
                          line.type === "stdout" && "text-zinc-300",
                          line.type === "system" && "text-blue-400 italic",
                        )}
                      >
                        {line.text}
                      </div>
                    ))
                  )}
                  <div ref={outputEndRef} />
                </div>
              </ScrollArea>
            </div>
          )}
        </div>

        {/* ============================================================== */}
        {/* AI Sidebar (Code Generation / Review) */}
        {/* ============================================================== */}
        {showSidebar && (
          <div className="flex flex-col w-80 bg-zinc-900/90 border-l border-zinc-800 shrink-0">
            <Tabs defaultValue="review" className="flex flex-col flex-1 gap-0">
              <TabsList className="rounded-none bg-zinc-900 border-b border-zinc-800 w-full justify-start px-2 h-9">
                <TabsTrigger
                  value="review"
                  className="text-xs data-[state=active]:bg-zinc-800"
                >
                  <Bot className="size-3 mr-1" />
                  Review
                </TabsTrigger>
                <TabsTrigger
                  value="generate"
                  className="text-xs data-[state=active]:bg-zinc-800"
                >
                  <Sparkles className="size-3 mr-1" />
                  Generate
                </TabsTrigger>
              </TabsList>

              {/* Review content */}
              <div className="flex-1 min-h-0 overflow-hidden">
                <ScrollArea className="h-full">
                  <div className="p-4">
                    {isReviewing ? (
                      <div className="flex flex-col items-center gap-3 py-8 text-zinc-500">
                        <Loader2 className="size-6 animate-spin text-violet-400" />
                        <span className="text-xs">
                          Analyzing your code...
                        </span>
                      </div>
                    ) : reviewContent ? (
                      <div className="prose prose-invert prose-sm max-w-none text-zinc-300 text-xs leading-relaxed whitespace-pre-wrap">
                        {reviewContent}
                      </div>
                    ) : (
                      <div className="flex flex-col items-center gap-2 py-8 text-zinc-600">
                        <Bot className="size-8" />
                        <p className="text-xs text-center">
                          Click &quot;Review&quot; in the toolbar to get AI
                          feedback on your code.
                        </p>
                      </div>
                    )}
                  </div>
                </ScrollArea>
              </div>

              {/* Generate input */}
              <div className="p-3 border-t border-zinc-800 shrink-0">
                <div className="flex gap-2">
                  <textarea
                    value={codeGenPrompt}
                    onChange={(e) => setCodeGenPrompt(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        handleGenerate();
                      }
                    }}
                    placeholder="Describe code to generate..."
                    rows={2}
                    className="flex-1 rounded-md bg-zinc-800 border border-zinc-700 px-3 py-2 text-xs text-zinc-300 placeholder:text-zinc-600 resize-none focus:outline-none focus:border-violet-500/50"
                  />
                  <Button
                    variant="ghost"
                    size="icon-sm"
                    onClick={handleGenerate}
                    disabled={isGenerating || !codeGenPrompt.trim()}
                    className="self-end text-violet-400 hover:text-violet-300"
                  >
                    {isGenerating ? (
                      <Loader2 className="size-4 animate-spin" />
                    ) : (
                      <Send className="size-4" />
                    )}
                  </Button>
                </div>
              </div>
            </Tabs>
          </div>
        )}
      </div>
    </div>
  );
}
