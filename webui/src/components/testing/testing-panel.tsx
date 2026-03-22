"use client";

import * as React from "react";
import Link from "next/link";
import { Code, FlaskConical, Play, Save, Wrench } from "lucide-react";

import { apiFetch, useCreateComponent, useLintCode, useRunTest, getBackendUrl } from "@/lib/api";
import type { AssistantModelCatalogEntry, TestResult, TestRun } from "@/lib/types";
import { CodeEditor } from "@/components/code-editor";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

type TestingPanelProps = {
  resourceType?: string;
  resourceId?: string;
  resourceName?: string;
  defaultLanguage?: string;
  defaultCode?: string;
};

export function TestingPanel({
  resourceType,
  resourceId,
  resourceName,
  defaultLanguage = "python",
  defaultCode = "",
}: TestingPanelProps) {
  const [code, setCode] = React.useState(defaultCode);
  const [language, setLanguage] = React.useState(defaultLanguage);
  const [inputData, setInputData] = React.useState("");
  const [expectedOutput, setExpectedOutput] = React.useState("");
  const [datasetId, setDatasetId] = React.useState("");
  const [runResult, setRunResult] = React.useState<TestRun | null>(null);
  const [testResults, setTestResults] = React.useState<TestResult[]>([]);
  const [lintIssues, setLintIssues] = React.useState<string[]>([]);
  const [snippetName, setSnippetName] = React.useState("");
  const [runLogs, setRunLogs] = React.useState<string[]>([]);
  const [sandboxEnabled, setSandboxEnabled] = React.useState(true);
  const [trackingEnabled, setTrackingEnabled] = React.useState(false);
  const [agentEvalEnabled, setAgentEvalEnabled] = React.useState(false);
  const [rlMetricsEnabled, setRlMetricsEnabled] = React.useState(false);
  const [evaluationProvider, setEvaluationProvider] = React.useState("ollama");
  const [evaluationModel, setEvaluationModel] = React.useState("");
  const [evaluationEndpoint, setEvaluationEndpoint] = React.useState("");
  const [evaluationHfExecutionMode, setEvaluationHfExecutionMode] = React.useState("hybrid");
  const [modelCatalog, setModelCatalog] = React.useState<AssistantModelCatalogEntry[]>([]);

  const { trigger: runTest, isMutating: isRunning } = useRunTest();
  const { trigger: lintCode, isMutating: isLinting } = useLintCode();
  const { trigger: createComponent, isMutating: isSavingSnippet } = useCreateComponent();

  React.useEffect(() => {
    if (defaultCode && defaultCode !== code) {
      setCode(defaultCode);
    }
  }, [defaultCode, code]);

  React.useEffect(() => {
    if (defaultLanguage && defaultLanguage !== language) {
      setLanguage(defaultLanguage);
    }
  }, [defaultLanguage, language]);

  React.useEffect(() => {
    const loadCatalog = async () => {
      try {
        const data = await apiFetch<{ models: AssistantModelCatalogEntry[] }>("/api/v1/assistant/models/catalog");
        setModelCatalog(data.models || []);
      } catch {
        // Optional metadata only; ignore failures.
      }
    };
    loadCatalog();
  }, []);

  React.useEffect(() => {
    if (!runResult?.id) return;

    const wsUrl = getBackendUrl().replace(/^http/, "ws") + "/ws";
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      ws.send(
        JSON.stringify({
          command: "subscribe",
          params: { topic: `run.${runResult.id}` },
        })
      );
    };

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.type === "run.log" && payload.data?.message) {
          setRunLogs((prev) => [...prev, payload.data.message]);
        }
      } catch {
        // ignore parsing errors
      }
    };

    return () => {
      ws.close();
    };
  }, [runResult?.id]);

  const evaluationModels = React.useMemo(() => {
    const provider = evaluationProvider || "ollama";
    const names = modelCatalog
      .filter((entry) => {
        if (provider === "ollama") {
          return entry.provider === "ollama" || entry.provider === "custom";
        }
        return entry.provider === provider;
      })
      .map((entry) => entry.model)
      .filter(Boolean);
    const deduped = Array.from(new Set(names));
    if (evaluationModel && !deduped.includes(evaluationModel)) {
      deduped.unshift(evaluationModel);
    }
    return deduped;
  }, [evaluationModel, evaluationProvider, modelCatalog]);

  const handleRunTest = async () => {
    setLintIssues([]);
    setRunLogs([]);
    const response = await runTest({
      code,
      language,
      resource_type: resourceType,
      resource_id: resourceId,
      input_data: inputData,
      expected_output: expectedOutput,
      dataset_id: datasetId || undefined,
      sandbox_enabled: sandboxEnabled,
      tracking_enabled: trackingEnabled,
      agent_eval_enabled: agentEvalEnabled,
      rl_metrics_enabled: rlMetricsEnabled,
      evaluation_provider: agentEvalEnabled ? evaluationProvider : undefined,
      evaluation_model: agentEvalEnabled ? (evaluationModel || undefined) : undefined,
      evaluation_endpoint: agentEvalEnabled ? (evaluationEndpoint || undefined) : undefined,
      evaluation_hf_execution_mode: agentEvalEnabled ? evaluationHfExecutionMode : undefined,
    });
    if (response?.run) {
      setRunResult(response.run);
      setTestResults(response.results || []);
    }
  };

  const handleLint = async () => {
    const response = await lintCode({ code, language });
    setLintIssues(response?.issues || []);
  };

  const handleSaveSnippet = async () => {
    const name = snippetName.trim() || `${resourceName || "Snippet"} ${new Date().toISOString()}`;
    await createComponent({
      name,
      category: "snippet",
      code,
      language,
      description: resourceName ? `Snippet from ${resourceName}` : "Testing snippet",
    });
    setSnippetName("");
  };

  const primaryResult = testResults[0];
  const parsedOutput = React.useMemo(() => {
    if (!primaryResult?.output) return null;
    try {
      return JSON.parse(primaryResult.output);
    } catch {
      return null;
    }
  }, [primaryResult]);

  return (
    <Card className="border-dashed">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FlaskConical className="size-5 text-violet-500" />
          Testing Sandbox
        </CardTitle>
        <CardDescription>
          Run free-form tests with optional tracking and evaluation
          {resourceName ? ` for ${resourceName}.` : "."}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Label className="text-sm font-medium">Test Code</Label>
            <Select value={language} onValueChange={setLanguage}>
              <SelectTrigger className="w-[140px]">
                <SelectValue placeholder="Language" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="python">Python</SelectItem>
                <SelectItem value="javascript">JavaScript</SelectItem>
                <SelectItem value="typescript">TypeScript</SelectItem>
                <SelectItem value="yaml">YAML</SelectItem>
                <SelectItem value="json">JSON</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <CodeEditor
            value={code}
            onChange={setCode}
            language={language}
            height={280}
          />
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="inputData">Input Data (JSON or text)</Label>
            <Textarea
              id="inputData"
              value={inputData}
              onChange={(e) => setInputData(e.target.value)}
              rows={4}
              className="font-mono text-xs"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="expectedOutput">Expected Output</Label>
            <Textarea
              id="expectedOutput"
              value={expectedOutput}
              onChange={(e) => setExpectedOutput(e.target.value)}
              rows={4}
              className="font-mono text-xs"
            />
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="datasetId">Test Dataset (optional)</Label>
            <Input
              id="datasetId"
              placeholder="dataset id or name"
              value={datasetId}
              onChange={(e) => setDatasetId(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="snippetName">Snippet Name</Label>
            <Input
              id="snippetName"
              placeholder="Save this snippet to the library"
              value={snippetName}
              onChange={(e) => setSnippetName(e.target.value)}
            />
          </div>
        </div>

        <div className="grid gap-3 md:grid-cols-2">
          <div className="flex items-center justify-between rounded-md border px-3 py-2">
            <div>
              <p className="text-sm font-medium">Sandbox Execution</p>
              <p className="text-xs text-muted-foreground">Use restricted builtins</p>
            </div>
            <Switch checked={sandboxEnabled} onCheckedChange={setSandboxEnabled} />
          </div>
          <div className="flex items-center justify-between rounded-md border px-3 py-2">
            <div>
              <p className="text-sm font-medium">Experiment Tracking</p>
              <p className="text-xs text-muted-foreground">Log metrics to MLFlow</p>
            </div>
            <Switch checked={trackingEnabled} onCheckedChange={setTrackingEnabled} />
          </div>
          <div className="flex items-center justify-between rounded-md border px-3 py-2">
            <div>
              <p className="text-sm font-medium">Agent Evaluation</p>
              <p className="text-xs text-muted-foreground">Use LLM judge scoring</p>
            </div>
            <Switch checked={agentEvalEnabled} onCheckedChange={setAgentEvalEnabled} />
          </div>
          <div className="flex items-center justify-between rounded-md border px-3 py-2">
            <div>
              <p className="text-sm font-medium">RL Metrics</p>
              <p className="text-xs text-muted-foreground">Emit reward signals</p>
            </div>
            <Switch checked={rlMetricsEnabled} onCheckedChange={setRlMetricsEnabled} />
          </div>
        </div>

        {agentEvalEnabled && (
          <div className="rounded-md border p-3 space-y-3">
            <p className="text-sm font-medium">Evaluation Model Configuration</p>
            <div className="grid gap-3 md:grid-cols-2">
              <div className="space-y-2">
                <Label>Provider</Label>
                <Select value={evaluationProvider} onValueChange={setEvaluationProvider}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select provider" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="ollama">Ollama</SelectItem>
                    <SelectItem value="huggingface_local">Hugging Face (local)</SelectItem>
                    <SelectItem value="openai_compatible">OpenAI-compatible</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Model</Label>
                <Select
                  value={evaluationModel || "__testing_default__"}
                  onValueChange={(value) => setEvaluationModel(value === "__testing_default__" ? "" : value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select model" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="__testing_default__">Testing default model</SelectItem>
                    {evaluationModels.map((model) => (
                      <SelectItem key={model} value={model}>
                        {model}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              {(evaluationProvider === "ollama" || evaluationProvider === "openai_compatible") && (
                <div className="space-y-2">
                  <Label>Endpoint Override</Label>
                  <Input
                    placeholder={evaluationProvider === "ollama" ? "http://localhost:11434" : "http://localhost:8000/v1"}
                    value={evaluationEndpoint}
                    onChange={(e) => setEvaluationEndpoint(e.target.value)}
                  />
                </div>
              )}
              {evaluationProvider === "huggingface_local" && (
                <div className="space-y-2">
                  <Label>HF Execution Mode</Label>
                  <Select value={evaluationHfExecutionMode} onValueChange={setEvaluationHfExecutionMode}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="local">local</SelectItem>
                      <SelectItem value="remote">remote</SelectItem>
                      <SelectItem value="hybrid">hybrid</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              )}
            </div>
          </div>
        )}

        <div className="flex flex-wrap items-center gap-3">
          <Button onClick={handleRunTest} disabled={isRunning || !code.trim()}>
            <Play className="size-4 mr-2" />
            {isRunning ? "Running..." : "Run Test"}
          </Button>
          <Button variant="outline" onClick={handleLint} disabled={isLinting || !code.trim()}>
            <Wrench className="size-4 mr-2" />
            {isLinting ? "Linting..." : "Lint"}
          </Button>
          <Button
            variant="outline"
            onClick={handleSaveSnippet}
            disabled={isSavingSnippet || !code.trim()}
          >
            <Save className="size-4 mr-2" />
            Save Snippet
          </Button>
          <Link href="/agents">
            <Button variant="ghost" size="sm" className="gap-2">
              <Code className="size-4" />
              Open Agent UI
            </Button>
          </Link>
        </div>

        {lintIssues.length > 0 && (
          <div className="rounded-md border border-amber-500/40 bg-amber-500/5 p-3 text-sm">
            <p className="font-medium text-amber-600">Lint Issues</p>
            <ul className="mt-2 space-y-1 text-xs text-muted-foreground">
              {lintIssues.map((issue, idx) => (
                <li key={idx}>{issue}</li>
              ))}
            </ul>
          </div>
        )}

        <Separator />

        <div className="space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant={runResult?.status === "success" ? "default" : "secondary"}>
              {runResult?.status || "idle"}
            </Badge>
            {runResult?.duration_seconds && (
              <span className="text-xs text-muted-foreground">
                {runResult.duration_seconds.toFixed(2)}s
              </span>
            )}
          </div>

          {primaryResult && (
            <div className="grid gap-3 md:grid-cols-2">
              <div className="rounded-md border bg-muted/30 p-3 text-xs">
                <p className="text-sm font-medium">Output</p>
                <pre className="mt-2 whitespace-pre-wrap font-mono">
                  {parsedOutput?.stdout || primaryResult.output}
                </pre>
              </div>
              <div className="rounded-md border bg-muted/30 p-3 text-xs">
                <p className="text-sm font-medium">Result & Errors</p>
                <pre className="mt-2 whitespace-pre-wrap font-mono">
                  {parsedOutput?.stderr || primaryResult.error_message || "No errors"}
                </pre>
              </div>
            </div>
          )}

          {runLogs.length > 0 && (
            <div className="rounded-md border bg-muted/30 p-3 text-xs">
              <p className="text-sm font-medium">Run Logs</p>
              <div className="mt-2 max-h-40 space-y-1 overflow-auto font-mono">
                {runLogs.map((line, idx) => (
                  <div key={idx} className={cn("whitespace-pre-wrap text-muted-foreground")}>
                    {line}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
